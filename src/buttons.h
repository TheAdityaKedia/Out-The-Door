// The CrowPanel's scroll wheel (up, down, press) and its menu and back buttons.
#pragma once

enum class Button { None, Up, Down, Press, Menu, Back };

void buttonsBegin();
// Returns a button once per press (debounced), or Button::None.
Button buttonPressed();
