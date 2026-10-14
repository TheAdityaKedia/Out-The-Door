# Wi-Fi, HTTP and clock sync.
import gc
import time

import network
import ntptime
import requests

_wlan = network.WLAN(network.STA_IF)


def connect(ssid, password, timeout=20):
    if _wlan.isconnected():
        return True
    _wlan.active(True)
    _wlan.connect(ssid, password)
    start = time.ticks_ms()
    while not _wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), start) > timeout * 1000:
            print("wifi: timed out")
            return False
        time.sleep(0.5)
    print("wifi: connected", _wlan.ifconfig()[0])
    return True


def get_json(url, timeout=15):
    gc.collect()
    r = requests.get(url, timeout=timeout)
    try:
        if r.status_code != 200:
            raise OSError("HTTP %d" % r.status_code)
        return r.json()
    finally:
        r.close()


def sync_clock():
    for _ in range(3):
        try:
            ntptime.settime()  # sets the RTC to UTC
            print("clock: synced")
            return True
        except Exception as e:
            print("clock: retry", e)
            time.sleep(2)
    return False
