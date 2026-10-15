// Text in our DejaVu bitmap fonts, placed by the top of the line (like the
// mockups) rather than by the baseline as Adafruit GFX does.
#pragma once
#include <Adafruit_GFX.h>

struct Font {
  const GFXfont *gfx;
  int8_t ascent;
  uint8_t height;
};

extern const Font BOLD10, SANS10, SANS11, BOLD12, BOLD14, BOLD16, BOLD17, BOLD18, BOLD26, BOLD30;

int textWidth(const Font &f, const char *s);
// Draws s with its top-left at (x, y); returns the x after the last character.
int drawText(Adafruit_GFX &g, const Font &f, int x, int y, const char *s, uint16_t color);
void drawTextRight(Adafruit_GFX &g, const Font &f, int right, int y, const char *s, uint16_t color);
void drawTextCenter(Adafruit_GFX &g, const Font &f, int cx, int y, const char *s, uint16_t color);

// Word-wraps s into at most maxLines lines no wider than maxWidth. Returns
// the number of lines, or maxLines + 1 if it doesn't fit.
int wrapText(const Font &f, const char *s, int maxWidth, char lines[][64], int maxLines);
