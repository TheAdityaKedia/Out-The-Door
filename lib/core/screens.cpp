#include "screens.h"

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#include "clock.h"
#include "moon.h"
#include "text.h"

// ---- pieces shared by several screens

static void header(Adafruit_GFX &g, const char *left, const char *right) {
  g.fillRect(0, 0, SCREEN_W, 16, INK);
  drawText(g, BOLD12, 4, 1, left, PAPER);
  drawTextRight(g, BOLD12, SCREEN_W - 4, 1, right, PAPER);
}

static void pageDots(Adafruit_GFX &g, int page) {
  for (int k = 0; k < PAGE_COUNT; k++) {
    const int x = SCREEN_W / 2 - 18 + k * 12, y = SCREEN_H - 5;
    if (k == page)
      g.fillCircle(x, y, 2, INK);
    else
      g.drawCircle(x, y, 2, INK);
  }
}

static void dottedRule(Adafruit_GFX &g, int x0, int x1, int y) {
  for (int x = x0; x < x1; x += 2) g.drawPixel(x, y, INK);
}

static void thickLine(Adafruit_GFX &g, int x0, int y0, int x1, int y1) {
  g.drawLine(x0, y0, x1, y1, INK);
  g.drawLine(x0 + 1, y0, x1 + 1, y1, INK);
  g.drawLine(x0, y0 + 1, x1, y1 + 1, INK);
}

// ---- weather icons, centred on (cx, cy), about 32 px across

static void sun(Adafruit_GFX &g, int cx, int cy, int r) {
  g.fillCircle(cx, cy, r, INK);
  for (int k = 0; k < 8; k++) {
    const double a = k * M_PI / 4, c = cos(a), s = sin(a);
    thickLine(g, (int)(cx + (r + 3) * c), (int)(cy + (r + 3) * s), (int)(cx + (r + 7) * c),
              (int)(cy + (r + 7) * s));
  }
}

static void cloud(Adafruit_GFX &g, int cx, int cy) {
  g.fillCircle(cx - 8, cy, 6, INK);
  g.fillCircle(cx + 2, cy - 4, 8, INK);
  g.fillCircle(cx + 10, cy + 1, 5, INK);
  g.fillRect(cx - 8, cy, 18, 7, INK);
}

static void icon(Adafruit_GFX &g, Icon kind, int cx, int cy) {
  switch (kind) {
    case Icon::Sun:
      sun(g, cx, cy, 9);
      break;
    case Icon::Moon:
      g.fillCircle(cx, cy, 10, INK);
      g.fillCircle(cx + 6, cy - 4, 9, PAPER);
      break;
    case Icon::Partly:
      sun(g, cx + 5, cy - 6, 7);
      g.fillRect(cx - 16, cy - 2, 30, 14, PAPER);
      cloud(g, cx - 2, cy + 4);
      break;
    case Icon::Fog:
      cloud(g, cx, cy - 4);
      g.fillRect(cx - 16, cy + 7, 26, 2, INK);
      g.fillRect(cx - 10, cy + 11, 26, 2, INK);
      g.fillRect(cx - 16, cy + 15, 24, 2, INK);
      break;
    case Icon::Rain:
      cloud(g, cx, cy - 4);
      for (int dx = -8; dx <= 8; dx += 8) thickLine(g, cx + dx, cy + 7, cx + dx - 3, cy + 14);
      break;
    case Icon::Snow:
      cloud(g, cx, cy - 4);
      g.fillRect(cx - 9, cy + 8, 3, 3, INK);
      g.fillRect(cx - 1, cy + 12, 3, 3, INK);
      g.fillRect(cx + 7, cy + 8, 3, 3, INK);
      break;
    case Icon::Storm:
      cloud(g, cx, cy - 4);
      g.fillRect(cx - 5, cy + 3, 11, 4, PAPER);
      g.fillTriangle(cx + 2, cy + 4, cx - 4, cy + 12, cx + 1, cy + 12, INK);
      g.fillTriangle(cx + 5, cy + 9, cx - 1, cy + 9, cx - 3, cy + 19, INK);
      break;
    case Icon::Cloud:
    default:
      cloud(g, cx, cy);
      break;
  }
}

// ---- screens

void drawTrains(Adafruit_GFX &g, const Now &now, const TrainsView &v) {
  char buf[48];
  formatTime(now, buf, sizeof buf);
  header(g, v.stationLabel, buf);
  if (!v.minutes || v.ageSeconds > v.giveUpAfter) {
    drawTextCenter(g, BOLD14, SCREEN_W / 2, 44, "No train times right now", INK);
    drawTextCenter(g, SANS11, SCREEN_W / 2, 66, "Checking again shortly", INK);
    pageDots(g, 0);
    return;
  }
  const int top = 18, rowH = 32;
  for (int i = 0; i < 3; i++) {
    const int y = top + i * rowH;
    const TrainRow &row = v.minutes[i];
    drawText(g, BOLD14, 4, y + 8, v.rows[i].label, INK);
    int right = SCREEN_W - 4;
    if (row.count >= 2) {
      snprintf(buf, sizeof buf, "%d", row.minutes[1]);
      drawTextRight(g, BOLD16, right, y + 10, buf, INK);
      right -= textWidth(BOLD16, buf) + 6;
    }
    if (row.count >= 1) {
      snprintf(buf, sizeof buf, "%d", row.minutes[0]);
      drawTextRight(g, BOLD26, right, y + 1, buf, INK);
    } else {
      drawTextRight(g, BOLD16, right, y + 10, "--", INK);
    }
    if (i < 2) dottedRule(g, 4, SCREEN_W - 4, y + rowH - 1);
  }
  if (v.ageSeconds > v.staleAfter) {
    snprintf(buf, sizeof buf, "updated %ld min ago", v.ageSeconds / 60);
    drawTextCenter(g, BOLD10, SCREEN_W / 2, SCREEN_H - 12, buf, INK);
  } else {
    pageDots(g, 0);
  }
}

void drawWeather(Adafruit_GFX &g, const Now &now, const CityConfig *config, const CityWeather *cities) {
  char buf[32];
  formatDayMonthDay(now, buf, sizeof buf);
  header(g, "Weather", buf);
  const int half = SCREEN_W / 2;
  g.drawFastVLine(half, 20, SCREEN_H - 32, INK);
  for (int i = 0; i < 2; i++) {
    const int x0 = i * half, cx = x0 + half / 2;
    drawTextCenter(g, BOLD12, cx, 19, config[i].label, INK);
    if (!cities) {
      drawTextCenter(g, BOLD30, cx, 50, "--", INK);
      continue;
    }
    const CityWeather &c = cities[i];
    icon(g, c.icon, x0 + 24, 62);
    snprintf(buf, sizeof buf, "%d\xB0", c.temp);
    drawText(g, BOLD30, x0 + 46, 40, buf, INK);
    drawTextCenter(g, BOLD12, x0 + 46 + (half - 50) / 2, 76, c.label, INK);
    snprintf(buf, sizeof buf, "H %d  L %d", c.high, c.low);
    drawTextCenter(g, SANS10, cx, 96, buf, INK);
  }
  pageDots(g, 1);
}

void drawOblique(Adafruit_GFX &g, const Now &now, const char *card, int page) {
  char buf[32];
  formatMonthDay(now, buf, sizeof buf);
  header(g, "Oblique Strategies", buf);
  const int boxTop = 22, boxBottom = SCREEN_H - 12;
  g.drawRect(6, boxTop, SCREEN_W - 12, boxBottom - boxTop + 1, INK);

  // Largest size that fits: (font, line height, most lines).
  struct Size { const Font *font; int lineH, most; };
  const Size sizes[] = {{&BOLD17, 21, 3}, {&BOLD14, 17, 4}, {&BOLD12, 15, 5}};
  char lines[5][64];
  int n = 0;
  const Size *pick = &sizes[2];
  for (const Size &s : sizes) {
    n = wrapText(*s.font, card, SCREEN_W - 28, lines, s.most);
    pick = &s;
    if (n <= s.most) break;
  }
  if (n > pick->most) n = pick->most;
  const int block = (n - 1) * pick->lineH + pick->font->height;
  int y = boxTop + (boxBottom - boxTop - block) / 2 + 1;
  for (int i = 0; i < n; i++, y += pick->lineH) drawTextCenter(g, *pick->font, SCREEN_W / 2, y, lines[i], INK);
  if (page >= 0) pageDots(g, page);
}

// Lit side white, dark side a checker dither, like the mockup.
static void moonDisc(Adafruit_GFX &g, int cx, int cy, int r, double age) {
  const double phase = age / SYNODIC_MONTH, k = cos(2 * M_PI * phase);
  const int rr = r * r, edge = (r - 1) * (r - 1);
  for (int y = -r; y <= r; y++) {
    const double w = sqrt((double)(rr - y * y)), t = k * w;
    for (int x = -(int)w; x <= (int)w; x++) {
      const int d = x * x + y * y;
      if (d > rr) continue;
      const bool lit = phase < 0.5 ? (x > t) : (x < -t);
      if (!lit && (((x + y) & 1) == 0 || d > edge)) g.drawPixel(cx + x, cy + y, INK);
    }
  }
  g.drawCircle(cx, cy, r, INK);
}

void drawMoon(Adafruit_GFX &g, const Now &now) {
  char buf[48];
  formatMonthDay(now, buf, sizeof buf);
  header(g, "Moon", buf);
  const double age = moonAge(now.utcDays);
  moonDisc(g, 40, 64, 32, age);

  const char *name = moonPhaseName(age);
  const char *space = strchr(name, ' ');
  char first[16];
  snprintf(first, sizeof first, "%.*s", (int)(space - name), name);
  const int tx = 84;
  drawText(g, BOLD18, tx, 22, first, INK);
  drawText(g, BOLD18, tx, 42, space + 1, INK);
  snprintf(buf, sizeof buf, "%d%% lit", (int)lround(moonIllumination(age) * 100));
  drawText(g, BOLD14, tx, 66, buf, INK);

  const bool full = strcmp(name, "Full Moon") == 0;
  const double ahead = full ? fmod(SYNODIC_MONTH - age, SYNODIC_MONTH) : daysUntilFull(age);
  const Now then = makeNow((time_t)(now.epoch + (long)(ahead * 86400)));
  char day[24];
  formatDayMonthDay(then, day, sizeof day);
  snprintf(buf, sizeof buf, "%s %s", full ? "New moon" : "Full moon", day);
  drawText(g, SANS11, tx, 86, buf, INK);
  pageDots(g, 3);
}

void drawSplash(Adafruit_GFX &g, const char *line) {
  drawTextCenter(g, BOLD14, SCREEN_W / 2, 40, "out the door", INK);
  drawTextCenter(g, SANS11, SCREEN_W / 2, 64, line, INK);
}
