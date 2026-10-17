// The CrowPanel's scroll wheel (up, down, press) and its menu and back buttons.
#pragma once

enum class Button { None, Up, Down, Press, Menu, Back };

// The scroll wheel's press, which wakes the board from deep sleep, and the
// Menu button, which wakes it onto the next screensaver (both active low).
static const int WAKE_PIN = 5, MENU_PIN = 2;

void buttonsBegin();
// Returns a button once per press (debounced), or Button::None.
Button buttonPressed();
