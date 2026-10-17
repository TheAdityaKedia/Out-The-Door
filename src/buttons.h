// The CrowPanel's scroll wheel (up, down, press) and its menu and back buttons.
#pragma once

enum class Button { None, Up, Down, Press, Menu, Back };

// The GPIOs of all five buttons, active low (used to wake from deep sleep).
static const int BUTTON_PINS[] = {6, 4, 5, 2, 1};

void buttonsBegin();
// Returns a button once per press (debounced), or Button::None.
Button buttonPressed();
