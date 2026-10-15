// The CrowPanel's 2.13" e-paper. Board V1.0 has an SSD1680 controller and
// V1.2 a JD79661; both take the same 250x122 picture, sent differently.
#pragma once
#include <Adafruit_GFX.h>

class Panel {
 public:
  explicit Panel(int revision) : rev_(revision) {}
  void begin();
  // Sends the canvas to the screen. A full refresh flashes but clears any
  // ghosting; a partial one is quick and quiet.
  void show(const GFXcanvas1 &canvas, bool full);
  // Puts the controller into deep sleep; the next show() wakes it.
  void sleep();

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
  void initSsd1680();
  void cursorSsd1680();
  void showJd79661(bool full);
  void initJd79661();
  void lutJd79661(bool full);

  int rev_;
  bool awake_ = false;
  bool lutSwapped_ = false;
  uint8_t frame_[BYTES];     // picture being sent, 1 = black
  uint8_t previous_[BYTES];  // what is on screen now, for partial refreshes
};
