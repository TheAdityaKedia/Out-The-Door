#!/bin/sh
# Copy the firmware onto a Pico plugged in over USB. Needs mpremote:
#   pip install mpremote
# The first run also downloads Waveshare's display drivers into firmware/lib/.
set -e
cd "$(dirname "$0")/../firmware"

WS=https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/main/python
[ -f lib/epd_v3.py ] || curl -fsSL "$WS/Pico_ePaper-2.13_V3.py" -o lib/epd_v3.py
[ -f lib/epd_v4.py ] || curl -fsSL "$WS/Pico_ePaper-2.13_V4.py" -o lib/epd_v4.py

if [ ! -f secrets.py ]; then
  echo "Make firmware/secrets.py first: copy secrets_example.py and fill in your Wi-Fi." >&2
  exit 1
fi

for d in lib fonts sources screens; do
  mpremote mkdir ":$d" 2>/dev/null || true
done
mpremote cp -r lib fonts sources screens :
mpremote cp main.py config.py secrets.py clock.py gfx.py net.py display.py cards.txt :
echo "Copied. Resetting the Pico..."
mpremote reset
