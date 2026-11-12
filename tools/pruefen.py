#!/usr/bin/env python3
"""Prüft neu erzeugte Fahrplandateien, bevor sie veröffentlicht werden.

Aufruf:  python3 tools/pruefen.py <neues manifest.json> [<altes manifest.json>]

Fehler (Exitcode 1, dann wird nichts veröffentlicht und die App behält die alten Daten):
  - Der DELFI-Fahrplan ist älter als 14 Tage.
  - Eine Stadt hat keine Haltestellen oder an einem normalen Tag keine Abfahrten.
  - Haltestellen oder Abfahrten je Tag einer Stadt weichen um mehr als 20 % von der Vorwoche ab.
Warnungen (es wird trotzdem veröffentlicht):
  - Der Fahrplan endet vor dem Ende des Zeitraums, etwa weil der Fahrplanwechsel noch fehlt.
  - Einzelne Tage haben deutlich weniger Abfahrten als üblich (oft Feiertage).

Ergebnis als Tabelle in $GITHUB_STEP_SUMMARY, wenn gesetzt.
Mit PRUEFUNG_OHNE_VERGLEICH=1 entfällt der Vergleich mit der Vorwoche (nach gewollten Änderungen).
"""
import json, os, sys, statistics, datetime as dt

MAX_AGE, MAX_CHANGE, LOW_DAY = 14, 0.20, 0.5
WD = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def d(s):
    return dt.date.fromisoformat(s)


def fmt(day):
    return f"{WD[day.weekday()]} {day.day:02d}.{day.month:02d}."


def main():
    new = json.load(open(sys.argv[1], encoding="utf-8"))
    old = None
    if len(sys.argv) > 2 and os.path.exists(sys.argv[2]) and not os.environ.get("PRUEFUNG_OHNE_VERGLEICH"):
        try:
            old = json.load(open(sys.argv[2], encoding="utf-8"))
        except ValueError:
            old = None
    errors, warns, rows = [], [], []
    built = d(new["built"][:10])
    start, days = d(new["from"]), new["days"]
    dates = [start + dt.timedelta(days=i) for i in range(days)]

    # --- Aktualität ---
    if new.get("feedDate"):
        age = (built - d(new["feedDate"])).days
        if age > MAX_AGE:
            errors.append(f"Der DELFI-Fahrplan ist {age} Tage alt (Stand {new['feedDate']}). Erlaubt sind {MAX_AGE}.")
    else:
        warns.append("Das Datum des DELFI-Fahrplans ist unbekannt.")

    # --- Fahrplanende, z. B. fehlender Fahrplanwechsel ---
    end = d(new["feedEnd"]) if new.get("feedEnd") else None
    if end and end < dates[-1]:
        warns.append(f"Der Fahrplan reicht nur bis {fmt(end)}{end.year}. Für die Tage danach zeigt die App keine Abfahrten.")
    year = dates[-1].year
    # Fahrplanwechsel: zweiter Samstag im Dezember, gilt ab dem Sonntag danach
    dec = dt.date(year, 12, 1)
    wechsel = dec + dt.timedelta(days=(5 - dec.weekday()) % 7 + 7 + 1)
    if start <= wechsel <= dates[-1] and end and end < wechsel:
        warns.append(f"Der neue Jahresfahrplan ab {fmt(wechsel)}{year} ist noch nicht in den DELFI-Daten.")

    for cid, c in new["cities"].items():
        pd = c.get("perDay") or []
        stops = c.get("stops", 0)
        # nur Tage, die der Fahrplan abdeckt
        covered = [(day, n) for day, n in zip(dates, pd) if not end or day <= end]
        normal = [n for day, n in covered if day.weekday() < 5]
        med = statistics.median(normal) if normal else 0
        if stops == 0:
            errors.append(f"{cid}: keine Haltestellen.")
        if med == 0:
            errors.append(f"{cid}: an Werktagen keine Abfahrten.")
        # schwache Tage gegenüber demselben Wochentag
        weak = []
        for wd in range(7):
            vals = [n for day, n in covered if day.weekday() == wd]
            if not vals:
                continue
            m = statistics.median(vals)
            weak += [day for day, n in covered if day.weekday() == wd and m and n < LOW_DAY * m]
        if weak:
            warns.append(f"{cid}: deutlich weniger Abfahrten als üblich am " + ", ".join(fmt(x) for x in sorted(weak)) + " (Feiertag?).")
        # Vergleich mit der Vorwoche
        cmp_txt = "–"
        if old and cid in old.get("cities", {}) and old["cities"][cid].get("perDay"):
            o = old["cities"][cid]
            o_start, o_end = d(old["from"]), d(old["feedEnd"]) if old.get("feedEnd") else None
            o_dates = [o_start + dt.timedelta(days=i) for i in range(old["days"])]
            o_norm = [n for day, n in zip(o_dates, o["perDay"]) if day.weekday() < 5 and (not o_end or day <= o_end)]
            o_med = statistics.median(o_norm) if o_norm else 0
            ch_stops = (stops - o["stops"]) / o["stops"] if o.get("stops") else 0
            ch_dep = (med - o_med) / o_med if o_med else 0
            cmp_txt = f"{ch_stops:+.0%} / {ch_dep:+.0%}"
            if abs(ch_stops) > MAX_CHANGE:
                errors.append(f"{cid}: {ch_stops:+.0%} Haltestellen gegenüber der Vorwoche ({o['stops']} → {stops}).")
            if abs(ch_dep) > MAX_CHANGE:
                errors.append(f"{cid}: {ch_dep:+.0%} Abfahrten je Werktag gegenüber der Vorwoche ({int(o_med)} → {int(med)}).")
        rows.append((cid, stops, int(med), c.get("dupRemoved", 0), cmp_txt))

    # --- Bericht ---
    out = ["## Prüfung der Fahrplandateien", "",
           f"DELFI-Fahrplan vom {new.get('feedDate') or '?'}, gültig {new.get('feedStart')} bis {new.get('feedEnd')}. "
           f"Zeitraum der Dateien: {fmt(start)} bis {fmt(dates[-1])}{dates[-1].year}.", "",
           "| Stadt | Haltestellen | Abfahrten je Werktag | doppelte entfernt | Änderung zur Vorwoche (Halt. / Abf.) |",
           "|---|---:|---:|---:|---|"]
    out += [f"| {a} | {b} | {c} | {dd} | {e} |" for a, b, c, dd, e in rows]
    out.append("")
    if errors:
        out += ["### Fehler: nicht veröffentlicht", ""] + [f"- {e}" for e in errors] + [""]
    if warns:
        out += ["### Hinweise", ""] + [f"- {w}" for w in warns] + [""]
    if not errors:
        out.append("Alles in Ordnung, die Dateien werden veröffentlicht." if not warns else "Die Dateien werden trotz der Hinweise veröffentlicht.")
    text = "\n".join(out)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(text + "\n")
    for w in warns:
        print("::warning::" + w)
    for e in errors:
        print("::error::" + e)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
