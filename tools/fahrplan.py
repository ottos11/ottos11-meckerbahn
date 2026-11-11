#!/usr/bin/env python3
"""Fahrplandateien für Meckerlinie aus einem GTFS-Fahrplan (DELFI, Deutschland gesamt).

Aufruf:  python3 tools/fahrplan.py <gtfs.zip> <ausgabeordner> [stadt,stadt,...]

Erzeugt je Stadt:
  <stadt>/index.json        alle Haltestellen der Stadt: Kennung, Name, Lage, Verkehrsarten
  <stadt>/s/<kennung>.json  die Abfahrten einer Haltestelle im Zeitraum
und manifest.json mit Stand, Zeitraum und Quellenhinweis.

Zeitraum: 14 Tage zurück bis 21 Tage voraus, damit sich Vorfälle auch nachträglich melden
lassen. Für Tage, die der Fahrplan nicht mehr enthält, gilt der Fahrplan desselben
Wochentags aus der ersten Fahrplanwoche (Feiertage können dann abweichen).

Format einer Haltestellendatei:
  {"p": [[linie, art, betrieb, richtung], ...],      Fahrtmuster
   "d": [[muster, tage, [minuten, ...]], ...]}       tage: Bitmaske über den Zeitraum
                                                      (Bit i = Tag from+i), als Zahl;
                                                      minuten ab Mitternacht des Betriebstags
"""
import csv, io, json, math, os, re, sys, zipfile, datetime as dt
from collections import defaultdict

PAST, AHEAD = 14, 21
DAYS = PAST + AHEAD
HERE = os.path.dirname(os.path.abspath(__file__))


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ---------------- Städte aus www/cities.js ----------------
def load_cities():
    src = open(os.path.join(HERE, "..", "www", "cities.js"), encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'id:\s*"(\w+)",\s*name:\s*"([^"]+)",\s*center:\s*\[([\d.]+),\s*([\d.]+)\],\s*r:\s*([\d.]+)', src):
        out[m.group(1)] = {"id": m.group(1), "name": m.group(2), "lat": float(m.group(3)),
                           "lon": float(m.group(4)), "r": float(m.group(5))}
    return out


def km(lat1, lon1, lat2, lon2):
    return math.hypot((lat1 - lat2) * 111.32, (lon1 - lon2) * 111.32 * math.cos(math.radians(lat1)))


# ---------------- wie in der App ----------------
def stop_key(n):
    s = (n or "").lower()
    s = re.sub(r"\bhauptbahnhof\b", "hbf", s)
    s = re.sub(r"\b(bahnhof|bhf|bf)\b\.?", "bf", s)
    s = re.sub(r"[.,]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^((u|s|s\+u|u\+s|bf)\s+)+", "", s).strip()
    return s


def plain_name(n):
    return not re.match(r"^(u|s|s\+u|u\+s|bf\.?|bahnhof)\s", (n or "").strip(), re.I)


def mode_of(route_type, short):
    """GTFS-Verkehrsart als BUS, TRAM, SUBWAY (U-Bahn) oder SUBURBAN (S-Bahn). Sonst None."""
    try:
        t = int(route_type)
    except ValueError:
        return None
    s = (short or "").strip()
    if t in (3, 11) or 700 <= t <= 716 or t == 800:
        return "BUS"
    if t == 0 or 900 <= t <= 906:
        return "TRAM"
    if t == 1 or 400 <= t <= 404:
        return "SUBWAY"
    if t == 109 or t == 300:
        return "SUBURBAN"
    if (t == 2 or 100 <= t <= 117) and re.match(r"^S\s?\d", s):
        return "SUBURBAN"
    return None


def clean_line(s):
    return re.sub(r"^(Bus|Tram|STR)\s+", "", (s or "").strip(), flags=re.I).strip()


# ---------------- GTFS lesen ----------------
def rows(z, name):
    """Liefert (Spaltenindex, Zeilen) einer GTFS-Datei, oder (None, []) wenn sie fehlt."""
    names = {os.path.basename(n): n for n in z.namelist()}
    if name not in names:
        return None, iter(())
    f = io.TextIOWrapper(z.open(names[name]), encoding="utf-8-sig", newline="")
    r = csv.reader(f)
    head = [h.strip() for h in next(r)]
    return {h: i for i, h in enumerate(head)}, r


def col(ix, row, name, default=""):
    i = ix.get(name)
    return row[i] if i is not None and i < len(row) else default


def ymd(s):
    return dt.date(int(s[:4]), int(s[4:6]), int(s[6:8]))


def hms_min(s):
    if not s:
        return None
    p = s.strip().split(":")
    return int(p[0]) * 60 + int(p[1])


def stable_id(stop_id, parent):
    """Haltestellenkennung, die von Woche zu Woche gleich bleibt: der Haltestellenteil der DHID."""
    for s in (parent, stop_id):
        m = re.match(r"^(de:\d{5}:\d+)", s or "")
        if m:
            return m.group(1)
    return parent or stop_id


def fname(cid):
    return re.sub(r"[^A-Za-z0-9_-]", "_", cid.replace("de:", ""))


def main():
    gtfs, outdir = sys.argv[1], sys.argv[2]
    all_cities = load_cities()
    want = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] else list(all_cities)
    cities = [all_cities[c] for c in want if c in all_cities]
    if not cities:
        sys.exit("Keine bekannte Stadt: " + ",".join(want))
    log("Städte:", ", ".join(c["id"] for c in cities))
    today = dt.date.fromisoformat(os.environ["FP_TODAY"]) if os.environ.get("FP_TODAY") else dt.date.today()
    start = today - dt.timedelta(days=PAST)
    z = zipfile.ZipFile(gtfs)

    # --- Haltestellen ---
    ix, r = rows(z, "stops.txt")
    names = {}            # alle Haltestellen: Name (für Fahrtziele)
    pts = {}              # Haltepunkte in einer Stadt: stop_id -> (stadt, roh-kennung)
    raw = defaultdict(lambda: {"names": defaultdict(int), "lat": 0.0, "lon": 0.0, "n": 0})
    for row in r:
        sid = col(ix, row, "stop_id")
        nm = col(ix, row, "stop_name").strip()
        names[sid] = nm
        if col(ix, row, "location_type", "0") not in ("", "0"):
            continue
        try:
            lat, lon = float(col(ix, row, "stop_lat")), float(col(ix, row, "stop_lon"))
        except ValueError:
            continue
        for c in cities:
            if km(c["lat"], c["lon"], lat, lon) <= c["r"]:
                key = (c["id"], stable_id(sid, col(ix, row, "parent_station")))
                pts[sid] = key
                g = raw[key]
                g["names"][nm] += 1
                g["lat"] += lat; g["lon"] += lon; g["n"] += 1
                break
    log("Haltepunkte gesamt:", len(names), "in den Städten:", len(pts))

    # Haltestellen mit gleichem Namen dicht beieinander zusammenlegen (wie die App):
    # "U Jungfernstieg" und "Jungfernstieg" sind eine Haltestelle.
    clusters = {}         # (stadt, roh) -> cluster dict
    by_key = defaultdict(list)
    for key, g in sorted(raw.items()):
        lat, lon = g["lat"] / g["n"], g["lon"] / g["n"]
        nms = sorted(g["names"].items(), key=lambda kv: (-kv[1], kv[0]))
        nm = next((n for n, _ in nms if plain_name(n)), nms[0][0])
        k = (key[0], stop_key(nm))
        home = next((cl for cl in by_key[k] if km(cl["lat"], cl["lon"], lat, lon) <= 0.4), None)
        if home is None:
            home = {"city": key[0], "id": key[1], "name": nm, "lat": lat, "lon": lon, "ids": [], "modes": set()}
            by_key[k].append(home)
        elif plain_name(nm) and not plain_name(home["name"]):
            home["name"] = nm
        home["ids"].append(key[1])
        clusters[key] = home
    stop_cl = {sid: clusters[key] for sid, key in pts.items()}

    # --- Betriebe, Linien, Fahrten ---
    ix, r = rows(z, "agency.txt")
    agency = {col(ix, row, "agency_id"): col(ix, row, "agency_name").strip() for row in r}
    ix, r = rows(z, "routes.txt")
    routes = {}
    for row in r:
        short = col(ix, row, "route_short_name") or col(ix, row, "route_long_name")
        m = mode_of(col(ix, row, "route_type"), short)
        if not m:
            continue
        ag = col(ix, row, "agency_id")
        routes[col(ix, row, "route_id")] = (clean_line(short), m, agency.get(ag, agency.get("", "")) if ag else next(iter(agency.values()), ""))
    ix, r = rows(z, "trips.txt")
    trips = {}
    for row in r:
        rt = routes.get(col(ix, row, "route_id"))
        if rt:
            trips[col(ix, row, "trip_id")] = (rt, col(ix, row, "service_id"), col(ix, row, "trip_headsign").strip())
    log("Linien:", len(routes), "Fahrten:", len(trips))

    # --- Abfahrten: stop_times ist nach Fahrt sortiert, also Fahrt für Fahrt auswerten ---
    pat_ix = {c["id"]: {} for c in cities}      # muster -> nummer, je Stadt
    deps = defaultdict(lambda: defaultdict(set))  # cluster-id -> (muster, service) -> minuten
    used_svc = set()
    agn = defaultdict(lambda: defaultdict(int))   # Betriebe je Stadt, für die Zuordnung in cities.js
    ix, r = rows(z, "stop_times.txt")
    i_trip, i_stop, i_seq, i_dep = ix["trip_id"], ix["stop_id"], ix["stop_sequence"], ix["departure_time"]
    i_arr, i_pick = ix.get("arrival_time"), ix.get("pickup_type")
    i_hs = ix.get("stop_headsign")
    cur, buf, last = None, [], (-1, "")
    done = set()
    n_rows = n_split = 0

    def flush():
        nonlocal n_split
        if cur is None or not buf:
            return
        if cur in done:
            n_split += 1
        done.add(cur)
        (line, mode, ag), svc, hs = trips[cur]
        dest = hs or names.get(last[1], "")
        for seq, cl, minute, pick, shs in buf:
            if seq >= last[0] or pick == "1" or minute is None:
                continue          # an der Endhaltestelle fährt nichts mehr ab
            p = (line, mode, ag, shs or dest)
            pi = pat_ix[cl["city"]]
            if p not in pi:
                pi[p] = len(pi)
            deps[cl["city"] + "|" + cl["id"]][(pi[p], svc)].add(minute)
            cl["modes"].add(mode)
            used_svc.add(svc)
            agn[cl["city"]][(ag, mode)] += 1

    for row in r:
        n_rows += 1
        if n_rows % 5_000_000 == 0:
            log(f"  {n_rows // 1_000_000} Mio. Zeilen")
        t = row[i_trip]
        if t != cur:
            flush()
            cur, buf, last = (t if t in trips else None), [], (-1, "")
        if cur is None:
            continue
        seq = int(row[i_seq])
        if seq > last[0]:
            last = (seq, row[i_stop])
        cl = stop_cl.get(row[i_stop])
        if cl is not None:
            tm = row[i_dep] or (row[i_arr] if i_arr is not None else "")
            buf.append((seq, cl, hms_min(tm), row[i_pick] if i_pick is not None and i_pick < len(row) else "",
                        row[i_hs].strip() if i_hs is not None and i_hs < len(row) else ""))
    flush()
    log("stop_times:", n_rows, "Zeilen; nicht zusammenhängende Fahrten:", n_split)

    # --- Verkehrstage als Bitmaske über den Zeitraum ---
    cal, lo = {}, None
    ix, r = rows(z, "calendar.txt")
    wd = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for row in r:
        s = col(ix, row, "service_id")
        a, b = ymd(col(ix, row, "start_date")), ymd(col(ix, row, "end_date"))
        lo = a if lo is None or a < lo else lo
        if s in used_svc:
            cal[s] = (a, b, [col(ix, row, d) == "1" for d in wd])
    extra = defaultdict(dict)
    ix, r = rows(z, "calendar_dates.txt")
    for row in r:
        s = col(ix, row, "service_id")
        d = ymd(col(ix, row, "date"))
        if s in used_svc:
            extra[s][d] = col(ix, row, "exception_type") == "1"
    feed_lo = lo
    ix, r = rows(z, "feed_info.txt")
    for row in r:
        v = col(ix, row, "feed_start_date")
        if v:
            feed_lo = ymd(v)
    if feed_lo is None:
        feed_lo = min((d for e in extra.values() for d in e), default=start)

    def active(s, d):
        if d in extra[s]:
            return extra[s][d]
        c = cal.get(s)
        return bool(c and c[0] <= d <= c[1] and c[2][d.weekday()])

    days = []
    for i in range(DAYS):
        d = start + dt.timedelta(days=i)
        while d < feed_lo:           # vor Fahrplanbeginn: gleicher Wochentag eine Woche später
            d += dt.timedelta(days=7)
        days.append(d)
    mask = {}
    for s in used_svc:
        m = 0
        for i, d in enumerate(days):
            if active(s, d):
                m |= 1 << i
        mask[s] = m
    log("Fahrplan gültig ab", feed_lo, "| Zeitraum", start, "+", DAYS, "Tage")

    # --- schreiben ---
    os.makedirs(outdir, exist_ok=True)
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    man = {"built": built, "from": start.isoformat(), "days": DAYS, "estimatedBefore": feed_lo.isoformat(),
           "source": "DELFI e.V., Sollfahrplandaten Deutschland (GTFS), CC BY 4.0", "cities": {}}
    for c in cities:
        cid = c["id"]
        pats = sorted(pat_ix[cid].items(), key=lambda kv: kv[1])
        seen = set()
        index = []
        sdir = os.path.join(outdir, cid, "s")
        os.makedirs(sdir, exist_ok=True)
        n_dep = 0
        for cl in clusters.values():
            if cl["city"] != cid or id(cl) in seen:
                continue
            seen.add(id(cl))
            groups = defaultdict(set)
            for (pi, svc), mins in deps.get(cid + "|" + cl["id"], {}).items():
                if mask.get(svc):
                    groups[(pi, mask[svc])] |= mins
            if not groups:
                continue      # hier hält im Zeitraum nichts
            used = sorted({pi for pi, _ in groups})
            remap = {pi: j for j, pi in enumerate(used)}
            d = [[remap[pi], m, sorted(mins)] for (pi, m), mins in sorted(groups.items())]
            n_dep += sum(len(x[2]) for x in d)
            fn = fname(cl["id"])
            with open(os.path.join(sdir, fn + ".json"), "w", encoding="utf-8") as f:
                json.dump({"p": [list(pats[pi][0]) for pi in used], "d": d}, f, ensure_ascii=False, separators=(",", ":"))
            index.append([fn, cl["name"], round(cl["lat"], 5), round(cl["lon"], 5), sorted(cl["modes"])])
        index.sort(key=lambda x: x[1])
        with open(os.path.join(outdir, cid, "index.json"), "w", encoding="utf-8") as f:
            json.dump({"city": cid, "built": built, "from": start.isoformat(), "days": DAYS, "stops": index},
                      f, ensure_ascii=False, separators=(",", ":"))
        man["cities"][cid] = {"stops": len(index), "patterns": len(pats),
                              "agencies": [[a, m, n] for (a, m), n in sorted(agn[cid].items(), key=lambda kv: -kv[1])]}
        log(f"{cid}: {len(index)} Haltestellen, {len(pats)} Fahrtmuster, {n_dep} Abfahrtszeiten-Einträge")
    with open(os.path.join(outdir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
