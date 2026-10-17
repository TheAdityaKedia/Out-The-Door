#include "panel.h"

#include <Arduino.h>

#include "config.h"

// CrowPanel 2.13" pins (from Elecrow's examples and schematic).
static const int PIN_SCK = 12, PIN_MOSI = 11, PIN_CS = 14, PIN_DC = 13, PIN_RST = 10,
                 PIN_BUSY = 9, PIN_POWER = 7;

void Panel::begin() {
  pinMode(PIN_POWER, OUTPUT);
  digitalWrite(PIN_POWER, HIGH);  // the panel's 3.3 V rail
  pinMode(PIN_CS, OUTPUT);
  digitalWrite(PIN_CS, HIGH);
  pinMode(PIN_DC, OUTPUT);
  pinMode(PIN_RST, OUTPUT);
  digitalWrite(PIN_RST, HIGH);
  pinMode(PIN_BUSY, INPUT);
  pinMode(PIN_SCK, OUTPUT);
  pinMode(PIN_MOSI, OUTPUT);
  memset(previous_, 0, BYTES);
  delay(100);
}

// Canvas (x 0..249 left to right, y 0..121 top to bottom) to panel memory:
// 250 rows of 16 bytes, row r = column 249 - x, bit (y % 8) of byte y / 8.
// This matches the layout of Elecrow's examples (their USE_HORIZONTIAL 2).
void Panel::pack(const GFXcanvas1 &canvas, uint8_t *out) {
  memset(out, 0, BYTES);
  for (int y = 0; y < 122; y++) {
    for (int x = 0; x < 250; x++) {
      int cx = x, cy = y;
      if (PANEL_FLIP_180) {
        cx = 249 - x;
        cy = 121 - y;
      }
      if (canvas.getPixel(cx, cy)) out[(y >> 3) + (249 - x) * 16] |= 0x80 >> (y & 7);
    }
  }
}

void Panel::show(const GFXcanvas1 &canvas, bool full) {
  pack(canvas, frame_);
  if (rev_ == 10)
    showSsd1680(full);
  else
    showJd79661(full);
  memcpy(previous_, frame_, BYTES);
}

void Panel::sleep() {
  if (!awake_) return;
  if (rev_ == 10) {
    command(0x10);  // deep sleep mode 1
    data(0x01);
  } else {
    command(0x07);  // deep sleep
    data(0xA5);
  }
  delay(20);
  awake_ = false;
}

// ---- SPI and pins

void Panel::reset() {
  digitalWrite(PIN_RST, HIGH);
  delay(10);
  digitalWrite(PIN_RST, LOW);
  delay(rev_ == 10 ? 10 : 100);
  digitalWrite(PIN_RST, HIGH);
  delay(rev_ == 10 ? 10 : 100);
}

// SSD1680 holds BUSY high while working; the JD79661 holds it low.
bool Panel::waitIdle(uint32_t timeoutMs) {
  const int busyLevel = rev_ == 10 ? HIGH : LOW;
  const uint32_t start = millis();
  while (digitalRead(PIN_BUSY) == busyLevel) {
    if (millis() - start > timeoutMs) {
      Serial.println("panel: timed out waiting for BUSY");
      return false;
    }
    delay(1);
  }
  return true;
}

// Bit-banged SPI, as in Elecrow's examples: the hardware SPI peripheral did
// not reach the panel on this board.
static inline void writeByte(uint8_t b) {
  for (int i = 0; i < 8; i++) {
    digitalWrite(PIN_SCK, LOW);
    digitalWrite(PIN_MOSI, (b & 0x80) ? HIGH : LOW);
    digitalWrite(PIN_SCK, HIGH);
    b <<= 1;
  }
}

void Panel::command(uint8_t c) {
  digitalWrite(PIN_DC, LOW);
  digitalWrite(PIN_CS, LOW);
  writeByte(c);
  digitalWrite(PIN_CS, HIGH);
  digitalWrite(PIN_DC, HIGH);
}

void Panel::data(uint8_t d) { data(&d, 1); }

void Panel::data(const uint8_t *d, size_t n) {
  digitalWrite(PIN_DC, HIGH);
  digitalWrite(PIN_CS, LOW);
  for (size_t i = 0; i < n; i++) writeByte(d[i]);
  digitalWrite(PIN_CS, HIGH);
}

void Panel::dataFill(uint8_t value, size_t n) {
  digitalWrite(PIN_DC, HIGH);
  digitalWrite(PIN_CS, LOW);
  for (size_t i = 0; i < n; i++) writeByte(value);
  digitalWrite(PIN_CS, HIGH);
}

// Sends a frame (1 = black), flipping bits when the controller wants 1 = white.
void Panel::sendFrame(const uint8_t *frame, bool oneIsWhite) {
  const bool flip = oneIsWhite != (bool)PANEL_INVERT;
  uint8_t row[16];
  for (int r = 0; r < 250; r++) {
    for (int i = 0; i < 16; i++) row[i] = flip ? (uint8_t)~frame[r * 16 + i] : frame[r * 16 + i];
    data(row, 16);
  }
}

// ---- SSD1680 (board V1.0). Register values follow Elecrow's V1.0 examples.

void Panel::initSsd1680() {
  reset();
  waitIdle(1000);
  command(0x12);  // software reset
  waitIdle(1000);
  command(0x01);  // driver output: 250 gate lines
  data(0xF9);
  data(0x00);
  data(0x00);
  command(0x11);  // data entry: x then y increasing
  data(0x03);
  command(0x44);  // RAM x range: bytes 0..15
  data(0x00);
  data(0x0F);
  command(0x45);  // RAM y range: rows 0..249
  data(0x00);
  data(0x00);
  data(0xF9);
  data(0x00);
  command(0x3C);  // border waveform
  data(0x01);
  command(0x18);  // internal temperature sensor
  data(0x80);
  waitIdle(1000);
  awake_ = true;
}

void Panel::cursorSsd1680() {
  command(0x4E);  // RAM x address
  data(0x00);
  command(0x4F);  // RAM y address
  data(0x00);
  data(0x00);
}

void Panel::showSsd1680(bool full) {
  if (!awake_) {
    initSsd1680();
    full = true;
  }
  // 0x24 takes the new picture (1 = white). 0x26 holds the one already on
  // screen, which a partial refresh compares against; a full refresh gets
  // the new picture in both.
  cursorSsd1680();
  command(0x26);
  sendFrame(full ? frame_ : previous_, true);
  cursorSsd1680();
  command(0x24);
  sendFrame(frame_, true);
  command(0x22);              // display update control
  data(full ? 0xF4 : 0xFC);   // full: OTP waveform, mode 1; partial: mode 2
  command(0x20);              // go
  waitIdle(full ? 5000 : 3000);
}

// ---- JD79661 (board V1.2). Register values and waveforms follow Elecrow's
// V1.2 example; it is put to sleep after every refresh and woken by a reset.

static const uint8_t LUT_GC[5][8] = {
    {0x01, 0x00, 0x14, 0x14, 0x01, 0x00, 0x00, 0x01},  // 0x20
    {0x01, 0x60, 0x14, 0x14, 0x01, 0x00, 0x00, 0x01},  // 0x21
    {0x01, 0x20, 0x14, 0x14, 0x01, 0x00, 0x00, 0x01},  // 0x22
    {0x01, 0x10, 0x14, 0x14, 0x01, 0x00, 0x00, 0x01},  // 0x23
    {0x01, 0x90, 0x14, 0x14, 0x01, 0x00, 0x00, 0x01},  // 0x24
};
static const uint8_t LUT_DU[5][8] = {
    {0x01, 0x00, 0x14, 0x01, 0x01, 0x00, 0x00, 0x00},
    {0x01, 0x00, 0x14, 0x01, 0x01, 0x00, 0x00, 0x00},
    {0x01, 0x80, 0x14, 0x01, 0x01, 0x00, 0x00, 0x00},
    {0x01, 0x40, 0x14, 0x01, 0x01, 0x00, 0x00, 0x00},
    {0x01, 0x00, 0x14, 0x01, 0x01, 0x00, 0x00, 0x00},
};

void Panel::initJd79661() {
  reset();
  static const uint8_t panel[] = {0xF7, 0x8A};
  static const uint8_t power[] = {0x03, 0x00, 0x3F, 0x3F, 0x03};
  static const uint8_t booster[] = {0x27, 0x27, 0x2F};
  static const uint8_t resolution[] = {0x80, 0x00, 0xFA};  // 128 x 250
  static const uint8_t gateStart[] = {0x00, 0x00, 0x00};
  command(0x00);
  data(panel, sizeof panel);
  command(0x01);
  data(power, sizeof power);
  command(0x03);
  data(0x00);
  command(0x06);
  data(booster, sizeof booster);
  command(0x30);
  data(0x0D);
  command(0x60);
  data(0x22);
  command(0x82);
  data(0x07);
  command(0xE3);
  data(0x88);
  command(0x41);
  data(0x00);
  command(0x61);
  data(resolution, sizeof resolution);
  command(0x65);
  data(gateStart, sizeof gateStart);
  awake_ = true;
}

void Panel::lutJd79661(bool full) {
  const uint8_t(*lut)[8] = full ? LUT_GC : LUT_DU;
  // Each table is 56 bytes; only the first 8 are non-zero.
  auto send = [&](uint8_t reg, const uint8_t *row) {
    command(reg);
    data(row, 8);
    dataFill(0x00, 48);
  };
  send(0x20, lut[0]);
  send(0x21, lut[1]);
  send(0x24, lut[4]);
  // 0x22 and 0x23 swap every refresh to keep the panel DC-balanced.
  send(lutSwapped_ ? 0x23 : 0x22, lut[2]);
  send(lutSwapped_ ? 0x22 : 0x23, lut[3]);
  lutSwapped_ = !lutSwapped_;
}

void Panel::showJd79661(bool full) {
  initJd79661();
  command(0x50);  // VCOM and data interval: picture data is 1 = black
  data(0xD7);
  command(0x10);  // the picture on screen now
  sendFrame(previous_, false);
  command(0x13);  // the new picture
  sendFrame(frame_, false);
  lutJd79661(full);
  command(0x17);  // refresh
  data(0xA5);
  waitIdle(full ? 8000 : 4000);
  sleep();
}
