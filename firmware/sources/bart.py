# BART real-time departures (legacy JSON API, cmd=etd).

def url(station, key):
    return ("https://api.bart.gov/api/etd.aspx?cmd=etd&orig=%s&key=%s&json=y"
            % (station, key))


def parse(data, rows):
    # Returns one list of minutes (ints, soonest first) per configured row.
    # Trains already "Leaving" are dropped (too late to catch), as are trains
    # to destinations not in any row.
    out = [[] for _ in rows]
    stations = data.get("root", {}).get("station") or []
    if not stations:
        return out
    for etd in stations[0].get("etd") or []:
        abbr = etd.get("abbreviation", "")
        for i, (_, codes) in enumerate(rows):
            if abbr in codes:
                for est in etd.get("estimate") or []:
                    if est.get("cancelflag") == "1":
                        continue
                    m = est.get("minutes", "")
                    if m.isdigit():
                        out[i].append(int(m))
    for mins in out:
        mins.sort()
    return out


def adjusted(rows_minutes, age_seconds, count=2):
    # BART gives minutes as of the fetch; count down since then, dropping
    # trains that have gone, and keep the next `count` per row.
    gone = age_seconds // 60
    return [[m - gone for m in mins if m - gone >= 0][:count] for mins in rows_minutes]
