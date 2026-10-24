#include "text.h"

#include <string.h>

#include "fonts/Bold10.h"
#include "fonts/Bold12.h"
#include "fonts/Bold14.h"
#include "fonts/Bold16.h"
#include "fonts/Bold17.h"
#include "fonts/Bold18.h"
#include "fonts/Bold26.h"
#include "fonts/Bold30.h"
#include "fonts/Sans10.h"
#include "fonts/Sans11.h"

#define FONT(name) {&DejaVu##name, DejaVu##name##Ascent, DejaVu##name.yAdvance}
const Font BOLD10 = FONT(Bold10), SANS10 = FONT(Sans10), SANS11 = FONT(Sans11),
           BOLD12 = FONT(Bold12), BOLD14 = FONT(Bold14), BOLD16 = FONT(Bold16),
           BOLD17 = FONT(Bold17), BOLD18 = FONT(Bold18), BOLD26 = FONT(Bold26),
           BOLD30 = FONT(Bold30);

static int advance(const Font &f, uint8_t c) {
  if (c < f.gfx->first || c > f.gfx->last) c = '?';
  return f.gfx->glyph[c - f.gfx->first].xAdvance;
}

int textWidth(const Font &f, const char *s) {
  int w = 0;
  for (; *s; s++) w += advance(f, (uint8_t)*s);
  return w;
}

int drawText(Adafruit_GFX &g, const Font &f, int x, int y, const char *s, uint16_t color) {
  g.setFont(f.gfx);
  g.setTextColor(color);
  g.setTextWrap(false);
  g.setCursor(x, y + f.ascent);
  for (; *s; s++) g.write((uint8_t)*s);
  return g.getCursorX();
}

void drawTextRight(Adafruit_GFX &g, const Font &f, int right, int y, const char *s, uint16_t color) {
  drawText(g, f, right - textWidth(f, s), y, s, color);
}

void drawTextCenter(Adafruit_GFX &g, const Font &f, int cx, int y, const char *s, uint16_t color) {
  drawText(g, f, cx - textWidth(f, s) / 2, y, s, color);
}

int wrapText(const Font &f, const char *s, int maxWidth, char lines[][64], int maxLines) {
  int n = 0;
  char line[64] = "";
  char word[64];
  while (*s) {
    while (*s == ' ') s++;
    if (!*s) break;
    int len = 0;
    while (s[len] && s[len] != ' ' && len < 63) len++;
    memcpy(word, s, len);
    word[len] = 0;
    s += len;

    char trial[128];
    strcpy(trial, line);
    if (*line) strcat(trial, " ");
    strcat(trial, word);
    if (textWidth(f, trial) <= maxWidth && strlen(trial) < 64) {
      strcpy(line, trial);
    } else {
      if (*line) {
        if (n == maxLines) return maxLines + 1;
        strcpy(lines[n++], line);
      }
      strcpy(line, word);
    }
  }
  if (*line) {
    if (n == maxLines) return maxLines + 1;
    strcpy(lines[n++], line);
  }
  return n;
}
