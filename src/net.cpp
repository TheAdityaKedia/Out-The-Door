#include "net.h"

#include <HTTPClient.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <time.h>

#include "config.h"
#include "secrets.h"

bool wifiConnect(uint32_t timeoutMs) {
  if (WiFi.status() == WL_CONNECTED) return true;
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  const uint32_t start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - start > timeoutMs) {
      Serial.println("wifi: timed out");
      return false;
    }
    delay(200);
  }
  Serial.printf("wifi: connected, %s\n", WiFi.localIP().toString().c_str());
  return true;
}

void wifiOff() {
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
}

bool httpGet(const char *url, String &body) {
  if (!wifiConnect()) return false;
  WiFiClientSecure client;
  // The data is public and read-only, so the certificate isn't checked; this
  // avoids bundling root certificates that expire.
  client.setInsecure();
  HTTPClient http;
  http.setTimeout(15000);
  if (!http.begin(client, url)) return false;
  const int status = http.GET();
  const bool ok = status == HTTP_CODE_OK;
  if (ok)
    body = http.getString();
  else
    Serial.printf("http: %d for %s\n", status, url);
  http.end();
  return ok;
}

bool clockValid() { return time(nullptr) > 1700000000; }  // after Nov 2023

bool clockStart(uint32_t timeoutMs) {
  // Syncs at boot and then every hour on its own.
  configTzTime(TIME_ZONE, "pool.ntp.org", "time.nist.gov");
  const uint32_t start = millis();
  while (!clockValid()) {
    if (millis() - start > timeoutMs) return false;
    delay(200);
  }
  return true;
}
