// Weather from Open-Meteo (no key needed). One request covers every city.
#pragma once
#include "types.h"

void weatherUrl(const CityConfig *cities, int count, char *out, int size);

// Fills one CityWeather per city, in request order. Returns false if the JSON
// could not be read.
bool parseWeather(const char *json, CityWeather *out, int count);

// WMO weather code to icon and label.
void describeWeather(int code, bool isDay, Icon &icon, const char *&label);
