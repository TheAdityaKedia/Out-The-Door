// The CrowPanel's scroll wheel (up, down, press) and its menu and back buttons.
#pragma once

enum class Button { None, Up, Down, Press, Menu, Back };

// The scroll wheel's press, which wakes the board from deep sleep (active low).
static const int WAKE_PIN = 5;

void buttonsBegin();
// Returns a button once per press (debounced), or Button::None.
Button buttonPressed();
