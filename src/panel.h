// The CrowPanel's 2.13" e-paper. Board V1.0 has an SSD1680 controller and
// V1.2 a JD79661; both take the same 250x122 picture, sent differently.
#pragma once
#include <Adafruit_GFX.h>

class Panel {
 public:
  explicit Panel(int revision) : rev_(revision) {}
  // keepPrevious: the picture from before deep sleep is still on screen.
  void begin(bool keepPrevious);
  // Sends the canvas to the screen. A full refresh flashes but clears any
  // ghosting; a partial one is quick and quiet.
  void show(const GFXcanvas1 &canvas, bool full);
  // Shows a 4-grey picture with a full refresh (SSD1680 only). levels holds
  // one byte per canvas pixel, row by row: 0 black, 1 dark grey, 2 light
  // grey, 3 white. The next show() returns to black and white.
  void showGrey4(const uint8_t *levels);
  // Puts the controller into deep sleep; the next show() wakes it.
  void sleep();
  // Cuts the panel's power for deep sleep; the picture stays on the e-paper.
  void powerOff();

 private:
  static const int BYTES = 16 * 250;  // 128 (122 used) x 250, 1 bit per pixel

  void pack(const GFXcanvas1 &canvas, uint8_t *out);
  void reset();
  bool waitIdle(uint32_t timeoutMs);
  void command(uint8_t c);
  void data(uint8_t d);
  void data(const uint8_t *d, size_t n);
  void dataFill(uint8_t value, size_t n);
  void sendFrame(const uint8_t *frame, bool oneIsWhite);

  void showSsd1680(bool full);
  void sendPlane(const uint8_t *levels, int bit);
  void initSsd1680();
  void cursorSsd1680();
  void showJd79661(bool full);
  void initJd79661();
  void lutJd79661(bool full);

  int rev_;
  bool awake_ = false;
  uint8_t frame_[BYTES];  // picture being sent, 1 = black
};
