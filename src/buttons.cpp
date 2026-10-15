#include "buttons.h"

#include <Arduino.h>

// All active low.
static const struct {
  int pin;
  Button button;
} PINS[] = {{6, Button::Up}, {4, Button::Down}, {5, Button::Press}, {2, Button::Menu}, {1, Button::Back}};
static const int COUNT = sizeof(PINS) / sizeof(PINS[0]);
static const uint32_t DEBOUNCE_MS = 40;

static bool down[COUNT];
static uint32_t changedAt[COUNT];

void buttonsBegin() {
  for (int i = 0; i < COUNT; i++) {
    pinMode(PINS[i].pin, INPUT_PULLUP);
    down[i] = false;
    changedAt[i] = 0;
  }
}

Button buttonPressed() {
  const uint32_t now = millis();
  for (int i = 0; i < COUNT; i++) {
    const bool pressed = digitalRead(PINS[i].pin) == LOW;
    if (pressed != down[i] && now - changedAt[i] > DEBOUNCE_MS) {
      down[i] = pressed;
      changedAt[i] = now;
      if (pressed) return PINS[i].button;
    }
  }
  return Button::None;
}
