// Just enough of Arduino.h to build the drawing and parsing code on a laptop.
#pragma once
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include <string>

typedef bool boolean;
#define PROGMEM
#define pgm_read_byte(addr) (*(const uint8_t *)(addr))
#define pgm_read_word(addr) (*(const uint16_t *)(addr))
#define pgm_read_dword(addr) (*(const uint32_t *)(addr))

class __FlashStringHelper;

class String {
 public:
  String(const char *c = "") : s_(c) {}
  unsigned length() const { return s_.size(); }
  const char *c_str() const { return s_.c_str(); }

 private:
  std::string s_;
};
