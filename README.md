# out-the-door

A small e-ink display for the wall by the front door. It cycles through four screens, 20 seconds each:

1. **BART**: the next two trains from 19th St toward Richmond, SFO / Millbrae and Berryessa
2. **Weather**: Oakland and San Francisco right now, with today's high and low
3. **Oblique Strategies**: a card of the day
4. **Moon**: tonight's phase and the next full moon

From 11 pm to 6 am it stops cycling and just shows the card of the day.

![The four screens](previews/all_screens.png)

## Hardware

- Raspberry Pi Pico 2 W (with headers)
- Waveshare Pico-ePaper-2.13 (250x122, black and white). It plugs straight onto the Pico.
- A micro-USB cable and a USB wall adapter

## Setup

1. **Check the display version.** The back of the display board says V3 or V4. Set `DISPLAY_VERSION` in `firmware/config.py` to match.
2. **Flash MicroPython.** Hold BOOTSEL while plugging the Pico in, then drag the Pico 2 W `.uf2` from [micropython.org/download](https://micropython.org/download/) onto the drive that appears.
3. **Add your Wi-Fi.** Copy `firmware/secrets_example.py` to `firmware/secrets.py` and fill it in. You can use BART's shared key or [register your own](https://api.bart.gov/api/register.aspx).
4. **Copy it over.** Run `pip install mpremote`, then `tools/deploy.sh`. The first run also downloads Waveshare's display drivers.
5. **Check the screen.** Run `mpremote run tools/hello.py`. You should see a thin border on all four edges. If the top or bottom edge is cut off, set `DISPLAY_Y_OFFSET = 6` in `config.py` and deploy again.
6. **Unplug it and plug it into the wall.** It starts on its own.

## Changing things

Everything adjustable is in `firmware/config.py`: the station, which destinations count for each row, the cities, the time per screen and the quiet hours. Add cards to `firmware/cards.txt`, one per line. It ships with a short starter set, so paste in the full deck if you have it.

## Working on the screens without the Pico

`tools/preview.py` runs the real drawing code on a laptop and writes PNGs to `previews/`. It uses sample data by default; pass `--live` to use real train times and weather. It needs Pillow (`pip install pillow`).

`tools/test_logic.py` checks the time-zone, train-time, weather and moon calculations.

Fonts are DejaVu Sans, pre-rendered to bitmaps by `tools/make_fonts.py`. Run it again if you change sizes.

## Layout

```
firmware/          everything that goes on the Pico
  main.py          boot, rotation loop, fetch schedule, quiet hours
  config.py        settings
  clock.py         Pacific time (DST included) and date helpers
  net.py           Wi-Fi, HTTP, NTP
  display.py       Waveshare driver wrapper, partial vs full refresh
  gfx.py           text, header, dots, weather icons
  sources/         BART, Open-Meteo, card of the day, moon maths
  screens/         one draw() per screen
  fonts/           generated bitmap fonts
tools/             laptop-side scripts (preview, tests, fonts, deploy)
```
