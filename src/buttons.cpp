#include "buttons.h"

#include <Arduino.h>

// All active low.
static const struct {
  int pin;
  Button button;
} PINS[] = {{6, Button::Up}, {4, Button::Down}, {5, Button::Press}, {2, Button::Menu}, {1, Button::Back}};
static const int COUNT = sizeof(PINS) / sizeof(PINS[0]);
static const uint32_t DEBOUNCE_MS = 40;

// Presses are latched by interrupts: a scroll-wheel click is a short pulse,
// and the main loop is often busy refreshing the panel or fetching data.
static volatile bool pending[COUNT];
static volatile uint32_t pressedAt[COUNT];

static void IRAM_ATTR onEdge(void *arg) {
  const int i = (int)(intptr_t)arg;
  const uint32_t now = millis();
  if (now - pressedAt[i] > DEBOUNCE_MS) {
    pressedAt[i] = now;
    pending[i] = true;
  }
}

void buttonsBegin() {
  for (int i = 0; i < COUNT; i++) {
    pinMode(PINS[i].pin, INPUT_PULLUP);
    pending[i] = false;
    pressedAt[i] = 0;
    attachInterruptArg(digitalPinToInterrupt(PINS[i].pin), onEdge, (void *)(intptr_t)i, FALLING);
  }
}

Button buttonPressed() {
  for (int i = 0; i < COUNT; i++) {
    if (pending[i]) {
      pending[i] = false;
      return PINS[i].button;
    }
  }
  return Button::None;
}
