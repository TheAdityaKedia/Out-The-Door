#pragma once
#include <stddef.h>
#include <stdint.h>
#include <string.h>

class Print {
 public:
  virtual ~Print() {}
  virtual size_t write(uint8_t) = 0;
  virtual size_t write(const uint8_t *buf, size_t n) {
    size_t i = 0;
    while (i < n && write(buf[i])) i++;
    return i;
  }
  size_t print(const char *s) { return write((const uint8_t *)s, strlen(s)); }
};
