#!/bin/sh
# Build and run the laptop-side checks and screen previews (no board needed).
#   tools/host.sh            run the checks and write previews/*.pbm (+ PNGs if Pillow is installed)
# Needs a C++17 compiler and git. The first run downloads Adafruit GFX and
# ArduinoJson (the same versions the firmware uses) into host/deps/.
set -e
cd "$(dirname "$0")/.."
DEPS=host/deps
mkdir -p "$DEPS" host/build previews
[ -d "$DEPS/gfx" ] || git clone -q --depth 1 --branch 1.11.11 https://github.com/adafruit/Adafruit-GFX-Library "$DEPS/gfx"
[ -d "$DEPS/json" ] || git clone -q --depth 1 --branch v7.2.1 https://github.com/bblanchon/ArduinoJson "$DEPS/json"

c++ -std=c++17 -O1 -Wall -Wno-unused-function -Wno-sign-compare -DARDUINO=100 \
  -DARDUINOJSON_ENABLE_ARDUINO_STRING=0 -DARDUINOJSON_ENABLE_ARDUINO_STREAM=0 \
  -DARDUINOJSON_ENABLE_ARDUINO_PRINT=0 -DARDUINOJSON_ENABLE_PROGMEM=0 \
  -Ihost/shim -I"$DEPS/gfx" -I"$DEPS/json/src" -Ilib/core -Iinclude \
  host/main.cpp lib/core/*.cpp "$DEPS/gfx/Adafruit_GFX.cpp" \
  -o host/build/check
host/build/check host/fixtures previews

if python3 -c "import PIL" 2>/dev/null; then
  python3 tools/previews.py
fi
