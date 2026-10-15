// Wi-Fi, HTTPS GETs and the clock.
#pragma once
#include <Arduino.h>

bool wifiConnect(uint32_t timeoutMs = 20000);
void wifiOff();
// Fetches url into body. Returns false on any failure.
bool httpGet(const char *url, String &body);
// Starts NTP with the Pacific time zone; waits up to timeoutMs for a valid time.
bool clockStart(uint32_t timeoutMs = 15000);
bool clockValid();
