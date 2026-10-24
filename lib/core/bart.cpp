#include "bart.h"

#include <ArduinoJson.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void bartUrl(const char *station, const char *key, char *out, int size) {
  snprintf(out, size, "https://api.bart.gov/api/etd.aspx?cmd=etd&orig=%s&key=%s&json=y", station,
           key);
}

static int rowFor(const char *abbr, const TrainRowConfig *rows, int rowCount) {
  for (int i = 0; i < rowCount; i++)
    for (const char *code : rows[i].codes)
      if (code && strcmp(code, abbr) == 0) return i;
  return -1;
}

static void insertSorted(TrainRow &row, int minutes) {
  if (row.count == TrainRow::MAX) return;
  int i = row.count++;
  while (i > 0 && row.minutes[i - 1] > minutes) {
    row.minutes[i] = row.minutes[i - 1];
    i--;
  }
  row.minutes[i] = minutes;
}

bool parseBart(const char *json, const TrainRowConfig *rows, int rowCount, TrainRow *out) {
  JsonDocument filter;
  JsonObject est = filter["root"]["station"][0]["etd"][0].to<JsonObject>();
  est["abbreviation"] = true;
  est["estimate"][0]["minutes"] = true;
  est["estimate"][0]["cancelflag"] = true;

  JsonDocument doc;
  if (deserializeJson(doc, json, DeserializationOption::Filter(filter))) return false;

  for (int i = 0; i < rowCount; i++) out[i].count = 0;
  for (JsonObject etd : doc["root"]["station"][0]["etd"].as<JsonArray>()) {
    int r = rowFor(etd["abbreviation"] | "", rows, rowCount);
    if (r < 0) continue;
    for (JsonObject e : etd["estimate"].as<JsonArray>()) {
      const char *m = e["minutes"] | "";
      const char *cancelled = e["cancelflag"] | "0";
      if (strcmp(cancelled, "1") == 0 || m[0] < '0' || m[0] > '9') continue;
      insertSorted(out[r], atoi(m));
    }
  }
  return true;
}

TrainRow countDown(const TrainRow &row, long ageSeconds) {
  TrainRow left;
  left.count = 0;
  const int gone = (int)(ageSeconds / 60);
  for (int i = 0; i < row.count; i++)
    if (row.minutes[i] - gone >= 0) left.minutes[left.count++] = row.minutes[i] - gone;
  return left;
}
