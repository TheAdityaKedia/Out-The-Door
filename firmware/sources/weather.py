# Weather from Open-Meteo (no key needed). One request covers every city.

def url(cities):
    lats = ",".join("%.4f" % c[1] for c in cities)
    lons = ",".join("%.4f" % c[2] for c in cities)
    return ("https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s"
            "&current=temperature_2m,weather_code,is_day"
            "&daily=temperature_2m_max,temperature_2m_min"
            "&temperature_unit=fahrenheit&timezone=America%%2FLos_Angeles&forecast_days=1"
            % (lats, lons))


# WMO weather code -> (icon kind, day label, night label)
def describe(code, is_day):
    if code == 0:
        return ("sun", "Sunny") if is_day else ("moon", "Clear")
    if code in (1, 2):
        return ("partly", "Some sun") if is_day else ("cloud", "Few clouds")
    if code == 3:
        return ("cloud", "Cloudy")
    if code in (45, 48):
        return ("fog", "Foggy")
    if 51 <= code <= 57:
        return ("rain", "Drizzle")
    if 61 <= code <= 67 or 80 <= code <= 82:
        return ("rain", "Rain")
    if 71 <= code <= 77 or code in (85, 86):
        return ("snow", "Snow")
    if code >= 95:
        return ("storm", "Thunder")
    return ("cloud", "Cloudy")


def parse(data):
    # Returns a list of dicts, one per city in request order.
    if isinstance(data, dict):
        data = [data]
    out = []
    for loc in data:
        cur = loc["current"]
        daily = loc["daily"]
        icon, label = describe(int(cur["weather_code"]), bool(cur.get("is_day", 1)))
        out.append({
            "temp": round(cur["temperature_2m"]),
            "high": round(daily["temperature_2m_max"][0]),
            "low": round(daily["temperature_2m_min"][0]),
            "icon": icon,
            "label": label,
        })
    return out
