#include "weather.h"

#include <ArduinoJson.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

void weatherUrl(const CityConfig *cities, int count, char *out, int size) {
  char lats[64] = "", lons[64] = "";
  for (int i = 0; i < count; i++) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s%.4f", i ? "," : "", cities[i].lat);
    strncat(lats, buf, sizeof lats - strlen(lats) - 1);
    snprintf(buf, sizeof buf, "%s%.4f", i ? "," : "", cities[i].lon);
    strncat(lons, buf, sizeof lons - strlen(lons) - 1);
  }
  snprintf(out, size,
           "https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s"
           "&current=temperature_2m,weather_code,is_day"
           "&daily=temperature_2m_max,temperature_2m_min"
           "&temperature_unit=fahrenheit&timezone=America%%2FLos_Angeles&forecast_days=1",
           lats, lons);
}

void describeWeather(int code, bool isDay, Icon &icon, const char *&label) {
  if (code == 0) {
    icon = isDay ? Icon::Sun : Icon::Moon;
    label = isDay ? "Sunny" : "Clear";
  } else if (code == 1 || code == 2) {
    icon = isDay ? Icon::Partly : Icon::Cloud;
    label = isDay ? "Some sun" : "Few clouds";
  } else if (code == 45 || code == 48) {
    icon = Icon::Fog;
    label = "Foggy";
  } else if (code >= 51 && code <= 57) {
    icon = Icon::Rain;
    label = "Drizzle";
  } else if ((code >= 61 && code <= 67) || (code >= 80 && code <= 82)) {
    icon = Icon::Rain;
    label = "Rain";
  } else if ((code >= 71 && code <= 77) || code == 85 || code == 86) {
    icon = Icon::Snow;
    label = "Snow";
  } else if (code >= 95) {
    icon = Icon::Storm;
    label = "Thunder";
  } else {
    icon = Icon::Cloud;
    label = "Cloudy";
  }
}

static void readCity(JsonObject loc, CityWeather &c) {
  JsonObject cur = loc["current"];
  JsonObject daily = loc["daily"];
  c.temp = (int)lround(cur["temperature_2m"].as<double>());
  c.high = (int)lround(daily["temperature_2m_max"][0].as<double>());
  c.low = (int)lround(daily["temperature_2m_min"][0].as<double>());
  describeWeather(cur["weather_code"] | 3, (cur["is_day"] | 1) != 0, c.icon, c.label);
}

bool parseWeather(const char *json, CityWeather *out, int count) {
  JsonDocument doc;
  if (deserializeJson(doc, json)) return false;
  if (doc.is<JsonArray>()) {
    JsonArray all = doc.as<JsonArray>();
    if ((int)all.size() < count) return false;
    for (int i = 0; i < count; i++) readCity(all[i], out[i]);
  } else {
    if (count != 1) return false;
    readCity(doc.as<JsonObject>(), out[0]);
  }
  return true;
}
