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

// Page dots run down the right edge, beside the scroll wheel; screen content
// stays left of CONTENT_R to leave them room.
static const int CONTENT_R = SCREEN_W - 12, DOTS_X = SCREEN_W - 5;

static void pageDots(Adafruit_GFX &g, int page) {
  const int top = 16 + (SCREEN_H - 16) / 2 - (PAGE_COUNT - 1) * 5;
  for (int k = 0; k < PAGE_COUNT; k++) {
    const int x = DOTS_X, y = top + k * 10;
    if (k == page)
      g.fillCircle(x, y, 2, INK);
    else
      g.drawCircle(x, y, 2, INK);
  }
}

static void dottedRule(Adafruit_GFX &g, int x0, int x1, int y) {
  for (int x = x0; x < x1; x += 2) g.drawPixel(x, y, INK);
}

// ---- screens

void drawTrains(Adafruit_GFX &g, const Now &now, const TrainsView &v) {
  char buf[48];
  const bool stale = v.minutes && v.ageSeconds > v.staleAfter && v.ageSeconds <= v.giveUpAfter;
  const bool compact = v.rowCount > 3;
  if (stale && compact)
    snprintf(buf, sizeof buf, "%ld min ago", v.ageSeconds / 60);
  else
    formatTime(now, buf, sizeof buf);
  header(g, v.stationLabel, buf);
  if (!v.minutes || v.ageSeconds > v.giveUpAfter) {
    drawTextCenter(g, BOLD14, (4 + CONTENT_R) / 2, 44, "No train times right now", INK);
    drawTextCenter(g, SANS11, (4 + CONTENT_R) / 2, 66, "Checking again shortly", INK);
    pageDots(g, 0);
    return;
  }
  // Three roomy rows, or four compact ones.
  const int top = compact ? 17 : 18, rowH = compact ? 26 : 34;
  const Font &labelFont = BOLD14, &firstFont = compact ? BOLD18 : BOLD26, &laterFont = compact ? BOLD14 : BOLD16;
  const int labelY = compact ? 6 : 9, firstY = compact ? 4 : 2, laterY = compact ? 6 : 11;
  for (int i = 0; i < v.rowCount; i++) {
    const int y = top + i * rowH;
    const TrainRow &row = v.minutes[i];
    drawText(g, labelFont, 4, y + labelY, v.rows[i].label, INK);
    int right = CONTENT_R;
    if (row.count >= 2) {
      snprintf(buf, sizeof buf, "%d", row.minutes[1]);
      drawTextRight(g, laterFont, right, y + laterY, buf, INK);
      right -= textWidth(laterFont, buf) + 6;
    }
    if (row.count >= 1) {
      snprintf(buf, sizeof buf, "%d", row.minutes[0]);
      drawTextRight(g, firstFont, right, y + firstY, buf, INK);
    } else {
      drawTextRight(g, laterFont, right, y + laterY, "--", INK);
    }
    if (i < v.rowCount - 1) dottedRule(g, 4, CONTENT_R, y + rowH - 1);
  }
  if (stale && !compact) {
    snprintf(buf, sizeof buf, "updated %ld min ago", v.ageSeconds / 60);
    drawTextCenter(g, BOLD10, (4 + CONTENT_R) / 2, SCREEN_H - 12, buf, INK);
  }
  pageDots(g, 0);
}

// ---- small outline weather icons, centred on (cx, cy), about 20 px across

static void smallCloud(Adafruit_GFX &g, int cx, int cy) {
  g.fillCircle(cx - 4, cy + 1, 4, INK);
  g.fillCircle(cx + 1, cy - 2, 5, INK);
  g.fillCircle(cx + 6, cy + 1, 3, INK);
  g.fillRect(cx - 4, cy + 1, 10, 4, INK);
}

static void smallIcon(Adafruit_GFX &g, Icon kind, int cx, int cy) {
  switch (kind) {
    case Icon::Sun:
      g.drawCircle(cx, cy, 5, INK);
      g.drawCircle(cx, cy, 4, INK);
      for (int k = 0; k < 8; k++) {
        const double a = k * M_PI / 4, c = cos(a), s = sin(a);
        g.drawLine((int)lround(cx + 7 * c), (int)lround(cy + 7 * s), (int)lround(cx + 10 * c),
                   (int)lround(cy + 10 * s), INK);
      }
      break;
    case Icon::Moon:
      g.fillCircle(cx, cy, 7, INK);
      g.fillCircle(cx + 4, cy - 3, 6, PAPER);
      break;
    case Icon::Partly:
      g.drawCircle(cx + 4, cy - 4, 4, INK);
      g.fillRect(cx - 9, cy - 1, 14, 9, PAPER);
      smallCloud(g, cx - 2, cy + 2);
      break;
    case Icon::Fog:
      g.fillRect(cx - 10, cy - 5, 20, 2, INK);
      g.fillRect(cx - 6, cy - 1, 16, 2, INK);
      g.fillRect(cx - 10, cy + 3, 18, 2, INK);
      break;
    case Icon::Rain:
      smallCloud(g, cx, cy - 3);
      for (int dx = -4; dx <= 4; dx += 4) g.drawLine(cx + dx, cy + 4, cx + dx - 2, cy + 8, INK);
      break;
    case Icon::Snow:
      smallCloud(g, cx, cy - 3);
      for (int dx = -4; dx <= 4; dx += 4) g.fillRect(cx + dx, cy + 5 + (dx == 0 ? 2 : 0), 2, 2, INK);
      break;
    case Icon::Storm:
      smallCloud(g, cx, cy - 3);
      g.fillTriangle(cx + 1, cy + 2, cx - 3, cy + 7, cx, cy + 7, INK);
      g.fillTriangle(cx + 2, cy + 6, cx - 1, cy + 6, cx - 2, cy + 11, INK);
      break;
    case Icon::Cloud:
    default:
      smallCloud(g, cx, cy);
      break;
  }
}

// Plain small text; a warning is shown white on a black tag.
static void note(Adafruit_GFX &g, int x, int y, bool alignRight, const char *text, bool warn) {
  const int w = textWidth(SANS10, text);
  if (alignRight) x -= w;
  if (warn) g.fillRoundRect(x - 3, y - 1, w + 6, SANS10.height + 1, 3, INK);
  drawText(g, SANS10, x, y, text, warn ? PAPER : INK);
}

void drawWeather(Adafruit_GFX &g, const Now &now, const CityConfig *config, const CityWeather *cities) {
  char buf[32];
  formatDayMonthDay(now, buf, sizeof buf);
  header(g, "Weather", buf);
  g.drawFastHLine(4, 68, CONTENT_R - 3, INK);
  for (int i = 0; i < 2; i++) {
    const int row = i ? 72 : 20;
    drawText(g, BOLD12, 4, row, config[i].label, INK);
    if (!cities) {
      drawText(g, BOLD30, 4, row + 13, "--", INK);
      continue;
    }
    const CityWeather &c = cities[i];
    snprintf(buf, sizeof buf, "%d\xB0", c.temp);
    drawText(g, BOLD30, 4, row + 13, buf, INK);
    smallIcon(g, c.icon, 74, row + 27);

    // Everything on the right hangs off the day bar's two ends.
    const int bx0 = 112, bx1 = CONTENT_R - 2, by0 = row + 4, by1 = row + 11;
    g.fillRect(bx0, by0, bx1 - bx0 + 1, by1 - by0 + 1, PAPER);
    g.drawRect(bx0, by0, bx1 - bx0 + 1, by1 - by0 + 1, INK);
    int mx = c.high > c.low ? bx0 + (c.temp - c.low) * (bx1 - bx0) / (c.high - c.low) : (bx0 + bx1) / 2;
    if (mx < bx0 + 4) mx = bx0 + 4;
    if (mx > bx1 - 4) mx = bx1 - 4;
    g.fillTriangle(mx - 4, by0 - 4, mx + 4, by0 - 4, mx, by0 + 1, INK);
    g.fillRect(mx - 1, by0, 2, by1 - by0 + 1, INK);
    snprintf(buf, sizeof buf, "L %d\xB0", c.low);
    drawText(g, SANS10, bx0, row + 13, buf, INK);
    snprintf(buf, sizeof buf, "H %d\xB0", c.high);
    drawTextRight(g, SANS10, bx1, row + 13, buf, INK);

    if (c.uv >= 0) {
      const char *rating = c.uv <= 2 ? "low" : c.uv <= 5 ? "ok" : c.uv <= 7 ? "high" : "v.high";
      snprintf(buf, sizeof buf, "UV %d %s", c.uv, rating);
      note(g, bx0, row + 30, false, buf, c.uv > 5);
    }
    if (c.aqi >= 0) {
      const char *rating = c.aqi <= 50 ? "good" : c.aqi <= 100 ? "fair" : c.aqi <= 150 ? "bad" : "v.bad";
      snprintf(buf, sizeof buf, "AQI %d %s", c.aqi, rating);
      note(g, bx1, row + 30, true, buf, c.aqi > 100);
    }
  }
  pageDots(g, 1);
}

void drawOblique(Adafruit_GFX &g, const Now &now, const char *card, int page) {
  char buf[32];
  formatMonthDay(now, buf, sizeof buf);
  header(g, "Oblique Strategies", buf);
  // Without dots (quiet hours) the card takes the full width.
  const int boxTop = 22, boxBottom = SCREEN_H - 6, boxR = page >= 0 ? CONTENT_R : SCREEN_W - 6;
  g.drawRect(6, boxTop, boxR - 6, boxBottom - boxTop + 1, INK);

  // Largest size that fits: (font, line height, most lines).
  struct Size { const Font *font; int lineH, most; };
  const Size sizes[] = {{&BOLD17, 21, 3}, {&BOLD14, 17, 4}, {&BOLD12, 15, 5}};
  char lines[5][64];
  int n = 0;
  const Size *pick = &sizes[2];
  for (const Size &s : sizes) {
    n = wrapText(*s.font, card, boxR - 22, lines, s.most);
    pick = &s;
    if (n <= s.most) break;
  }
  if (n > pick->most) n = pick->most;
  const int block = (n - 1) * pick->lineH + pick->font->height;
  int y = boxTop + (boxBottom - boxTop - block) / 2 + 1;
  for (int i = 0; i < n; i++, y += pick->lineH) drawTextCenter(g, *pick->font, (6 + boxR) / 2, y, lines[i], INK);
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

  const char *name = moonPhaseName(age);
  const char *space = strchr(name, ' ');
  char first[16], lit[16], next[48];
  snprintf(first, sizeof first, "%.*s", (int)(space - name), name);
  snprintf(lit, sizeof lit, "%d%% lit", (int)lround(moonIllumination(age) * 100));
  const bool full = strcmp(name, "Full Moon") == 0;
  const double ahead = full ? fmod(SYNODIC_MONTH - age, SYNODIC_MONTH) : daysUntilFull(age);
  const Now then = makeNow((time_t)(now.epoch + (long)(ahead * 86400)));
  char day[24];
  formatDayMonthDay(then, day, sizeof day);
  snprintf(next, sizeof next, "%s %s", full ? "New moon" : "Full moon", day);

  // Disc and text centred as one block, left to right between the screen
  // edge and the dots, and top to bottom under the header.
  int textW = textWidth(BOLD18, first);
  const int widths[] = {textWidth(BOLD18, space + 1), textWidth(BOLD14, lit), textWidth(SANS11, next)};
  for (int w : widths) if (w > textW) textW = w;
  const int r = 32, gap = 12, blockW = 2 * r + gap + textW;
  const int left = (CONTENT_R + 4 - blockW) / 2;
  moonDisc(g, left + r, 70, r, age);
  const int tx = left + 2 * r + gap, ty = 30;
  drawText(g, BOLD18, tx, ty, first, INK);
  drawText(g, BOLD18, tx, ty + 20, space + 1, INK);
  drawText(g, BOLD14, tx, ty + 44, lit, INK);
  drawText(g, SANS11, tx, ty + 64, next, INK);
  pageDots(g, 3);
}

// Half a sun on the horizon at (cx, horizon y), about 15 px wide, with a
// small arrow under the horizon: up for sunrise, down for sunset.
static void sunIcon(Adafruit_GFX &g, int cx, int hy, bool up) {
  g.drawFastHLine(cx - 8, hy, 17, INK);
  for (int dy = 1; dy <= 4; dy++)
    for (int dx = -4; dx <= 4; dx++)
      if (dx * dx + dy * dy <= 18) g.drawPixel(cx + dx, hy - dy, INK);
  for (int k = 1; k <= 3; k++) {
    const double a = M_PI + k * M_PI / 4, c = cos(a), s = sin(a);
    g.drawLine((int)lround(cx + 6 * c), (int)lround(hy + 6 * s), (int)lround(cx + 8 * c), (int)lround(hy + 8 * s), INK);
  }
  if (up)
    g.fillTriangle(cx - 3, hy + 5, cx + 3, hy + 5, cx, hy + 2, INK);
  else
    g.fillTriangle(cx - 3, hy + 2, cx + 3, hy + 2, cx, hy + 5, INK);
}

void drawSunMoon(Adafruit_GFX &g, const Now &now, const CityConfig &where) {
  char buf[48];
  formatDayMonthDay(now, buf, sizeof buf);
  header(g, "Sun & Moon", buf);
  g.drawFastHLine(4, 68, CONTENT_R - 3, INK);

  // Top: day length, and a bar from sunrise to sunset with now marked on it,
  // drawn like the weather screen's low-to-high bar.
  drawText(g, BOLD12, 4, 20, "Daylight", INK);
  long rise, set;
  if (!sunTimes(now.localDays, where.lat, where.lon, &rise, &set)) {
    drawText(g, BOLD26, 4, 34, "--", INK);
  } else {
    const long mins = (set - rise + 30) / 60;
    snprintf(buf, sizeof buf, "%ldh %ldm", mins / 60, mins % 60);
    drawText(g, BOLD26, 4, 34, buf, INK);

    const int bx0 = 140, bx1 = CONTENT_R - 2, by0 = 24, by1 = 31;
    g.drawRect(bx0, by0, bx1 - bx0 + 1, by1 - by0 + 1, INK);
    // Fills as the day goes: empty before sunrise, full after sunset.
    if (now.epoch >= set) {
      g.fillRect(bx0, by0, bx1 - bx0 + 1, by1 - by0 + 1, INK);
    } else if (now.epoch > rise) {
      const int mx = bx0 + (int)((now.epoch - rise) * (bx1 - bx0) / (set - rise));
      g.fillRect(bx0, by0, mx - bx0, by1 - by0 + 1, INK);
      g.fillTriangle(mx - 4, by0 - 4, mx + 4, by0 - 4, mx, by0 + 1, INK);
    }
    const int ty = 34;
    // Times without the a/p: sunrise is always morning, sunset evening.
    formatTime(makeNow((time_t)rise), buf, sizeof buf);
    buf[strlen(buf) - 1] = 0;
    sunIcon(g, bx0 + 8, ty + 7, true);
    drawText(g, SANS10, bx0 + 20, ty + 1, buf, INK);
    formatTime(makeNow((time_t)set), buf, sizeof buf);
    buf[strlen(buf) - 1] = 0;
    sunIcon(g, bx1 - textWidth(SANS10, buf) - 12, ty + 7, false);
    drawTextRight(g, SANS10, bx1, ty + 1, buf, INK);
  }

  // Bottom: the moon, its phase, and the next full (or new) moon.
  const double age = moonAge(now.utcDays);
  moonDisc(g, 25, 95, 20, age);
  const char *name = moonPhaseName(age);
  drawText(g, BOLD14, 56, 76, name, INK);
  snprintf(buf, sizeof buf, "%d%% lit", (int)lround(moonIllumination(age) * 100));
  drawText(g, SANS10, 56, 100, buf, INK);
  const bool full = strcmp(name, "Full Moon") == 0;
  const double ahead = full ? fmod(SYNODIC_MONTH - age, SYNODIC_MONTH) : daysUntilFull(age);
  const Now then = makeNow((time_t)(now.epoch + (long)(ahead * 86400)));
  char day[24];
  formatDayMonthDay(then, day, sizeof day);
  snprintf(buf, sizeof buf, "%s %s", full ? "New" : "Full", day);
  drawTextRight(g, SANS10, CONTENT_R - 2, 100, buf, INK);
  pageDots(g, 3);
}

void drawSplash(Adafruit_GFX &g, const char *line) {
  drawTextCenter(g, BOLD14, SCREEN_W / 2, 40, "out the door", INK);
  drawTextCenter(g, SANS11, SCREEN_W / 2, 64, line, INK);
}
