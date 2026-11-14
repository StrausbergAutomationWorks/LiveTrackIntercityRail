"""Build Journey Beyond's shipped data (Intercity SSOT 8.13). Run by hand, never by Home Assistant; the outputs are
committed as custom_components/live_track_intercity_rail/data/journey_beyond_timetable.json and
journey_beyond_lines.json.gz.

    python tools/journey_beyond.py RAIL.json STATIONS.json [--report R.txt]

INPUTS. tools/journey_beyond_source.json: the five trains transcribed BY HAND from Journey Beyond's booking calendar
and timetable pages (its "about"). RAIL.json: an Overpass pull of Australia's railway=rail ways whose gauge includes
1435 or carries no gauge tag, sidings, yards, spurs and crossovers dropped (bin\\jb_osm_pull.py). STATIONS.json: an
Overpass pull of station features by name (the same script); each station names its OSM element. A station with no
element takes an APPROXIMATE position (APPROX, Nominatim, 2026-11-14) and is moved to the nearest track node.
(c) OpenStreetMap contributors, ODbL 1.0 (the map's credit line carries it).

THE LINES: each stop pattern is routed leg by leg on the track (Renfe's tool's Graph and A*, no gauge preference: the
pull is standard gauge or untagged already), joined, and simplified by Douglas-Peucker at DP_M. A leg with no route,
or one over DETOUR_X times its straight line plus DETOUR_EXTRA_M, is the straight line, and the report says so. Every
call carries its distance along its pattern's line (`m`), which the runtime uses to pace a call with no time.

SECTIONS: where a train REVERSES at a call (the Indian Pacific at Adelaide, the Great Southern at Canberra: the leg in
and the leg out meet at over REVERSE_DEG), its line would run over the same track twice, and a point there would match
both passes (V/Line's folds, Intercity SSOT 8.5). So the line is cut there: each section ships as its own line,
"<pattern>#<n>", and the pattern lists the call where each section starts (`sections`).

THE ZONES: each station's IANA zone from its position (saw_livetrack.zones.zone_at; decision 6), stored, so the
runtime needs only zoneinfo. Broken Hill must come out Australia/Broken_Hill: the build refuses otherwise.

THE TIMETABLE: times as minutes from the run's first local midnight (day x 1440 + hh x 60 + mm), at each station's own
local clock. A run is a weekly series [pattern, first date, weeks, departure, arrival]: its departure and arrival
replace the pattern's ends (the calendar wins for the ends, Lee 2026-11-14).
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import importlib.util
import json
import os
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "custom_components" / "live_track_intercity_rail" / "data"
SOURCE = ROOT / "tools" / "journey_beyond_source.json"
DATA_VERSION = 1
DP_M = 15.0
DETOUR_X = 3.0
DETOUR_EXTRA_M = 20000.0
REVERSE_DEG = 150.0
BEARING_M = 3000.0
# Nominatim, 2026-11-14 (bin\jb_nominatim3.py): the stations with no OSM station element.
APPROX = {"MLA": (-27.30312, 133.62179), "LPL": (-34.36166, 138.37612), "SYD": (-33.88399, 151.20634),
          # Katherine: OSM's station way w595656860 lies over 3 km from the pulled track (2026-11-14 build); its node
          # n2409193438, snapped.
          "KTR": (-14.51461, 132.25368)}
APPROX_MAX_M = 15000.0
EXPECT_ZONE = {"BKH": "Australia/Broken_Hill", "ADL": "Australia/Adelaide", "DRW": "Australia/Darwin",
               "EPT": "Australia/Perth", "SYD": "Australia/Sydney", "SCS": "Australia/Melbourne",
               "RMS": "Australia/Brisbane"}


def _renfe_tool():
    spec = importlib.util.spec_from_file_location("renfe_spain_lines_tool", ROOT / "tools" / "renfe_spain_lines.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def minutes(text):
    """"2 17:30" -> 2 x 1440 + 17 x 60 + 30; None for None."""
    if text is None:
        return None
    day, hm = text.split()
    h, m = hm.split(":")
    return int(day) * 1440 + int(h) * 60 + int(m)


def encode(points):
    out, pla, plo = [], 0, 0
    for la, lo in points:
        a, b = round(la * 1e5), round(lo * 1e5)
        out += [a - pla, b - plo]
        pla, plo = a, b
    return out


def bearing(a, b):
    import math
    la1, la2 = math.radians(a[0]), math.radians(b[0])
    dl = math.radians(b[1] - a[1])
    y = math.sin(dl) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(dl)
    return math.degrees(math.atan2(y, x)) % 360


def end_bearing(leg, hav, at_start):
    """The bearing over the first (or last) BEARING_M of a leg, pointing along the direction of travel."""
    pts = leg if at_start else leg[::-1]
    run, far = 0.0, pts[-1]
    for a, b in zip(pts, pts[1:]):
        run += hav(a, b)
        if run >= BEARING_M:
            far = b
            break
    return bearing(pts[0], far) if at_start else bearing(far, pts[0])


def osm_positions(stations_doc):
    pos = {}
    for e in stations_doc.get("elements", []):
        la = e.get("lat", (e.get("center") or {}).get("lat"))
        lo = e.get("lon", (e.get("center") or {}).get("lon"))
        if la is not None and lo is not None:
            pos[f'{e["type"][0]}{e["id"]}'] = (float(la), float(lo))
    return pos


def build(rail_path, stations_path, log):
    from saw_livetrack.zones import DATA_VERSION as ZONES_VERSION, zone_at
    renfe = _renfe_tool()
    t0 = time.time()
    src = json.load(open(SOURCE, encoding="utf-8"))
    rail_raw = open(rail_path, "rb").read()
    osm = json.loads(rail_raw)
    g = renfe.Graph(osm, log)
    found = osm_positions(json.load(open(stations_path, encoding="utf-8")))
    stations = {}
    for sid, s in src["stations"].items():
        if s.get("osm"):
            if s["osm"] not in found:
                raise SystemExit(f"{sid}: OSM element {s['osm']} not in the stations pull")
            la, lo = found[s["osm"]]
            how = s["osm"]
        else:
            la, lo = APPROX[sid]
            how = "approx"
        g.stops[sid] = (la, lo, s["name"])
        if how == "approx":
            m, node = g.snap(sid)
            if node < 0 or m > APPROX_MAX_M:
                raise SystemExit(f"{sid}: no track within {APPROX_MAX_M} m of its approximate position")
            la, lo = g.pts[node]
            g.stops[sid] = (la, lo, s["name"])
            log(f"{sid} {s['name']}: approximate position moved {round(m)} m to the track")
        zone = zone_at(la, lo)
        if sid in EXPECT_ZONE and zone != EXPECT_ZONE[sid]:
            raise SystemExit(f"{sid}: zone {zone}, expected {EXPECT_ZONE[sid]}")
        stations[sid] = [s["name"], round(la, 5), round(lo, 5), zone]
        log(f"{sid} {s['name']} {la:.5f},{lo:.5f} {zone} ({how})")
    lines, patterns = {}, {}
    for pid, p in src["patterns"].items():
        seq = [c[0] for c in p["calls"]]
        pts, ms, total, legs = [], [0.0], 0.0, []
        for a, b in zip(seq, seq[1:]):
            straight = renfe.hav(g.stops[a][:2], g.stops[b][:2])
            r = g.route(a, b, None)
            if r is None or r[1] > DETOUR_X * straight + DETOUR_EXTRA_M:
                why = g.fails.get((a, b), "?") if r is None else f"detour {round(r[1])} m"
                log(f"REVIEW {pid} {a}-{b}: straight line ({why}); straight {round(straight)} m")
                leg, length = [g.stops[a][:2], g.stops[b][:2]], straight
            else:
                leg, length = [g.pts[i] for i in r[2]], r[1]
                log(f"{pid} {a}-{b}: {length / 1000:.1f} km on the track (x{length / max(1.0, straight):.2f} straight)")
            legs.append((leg, length))
            total += length
            ms.append(total)
        starts = [0]
        for i in range(1, len(legs)):
            turn = abs((end_bearing(legs[i][0], renfe.hav, True) - end_bearing(legs[i - 1][0], renfe.hav, False)
                        + 180) % 360 - 180)
            if turn > REVERSE_DEG:
                starts.append(i)
                log(f"{pid}: reverses at {seq[i]} ({turn:.0f} deg): a new section")
        simple = []
        for n, s in enumerate(starts):
            e = starts[n + 1] if n + 1 < len(starts) else len(legs)
            pts = []
            for leg, _ in legs[s:e]:
                pts.extend(leg if not pts else leg[1:])
            sec = renfe.dp(pts, DP_M)
            simple += sec
            lines[f"{pid}#{n}"] = [round(ms[e] - ms[s], 1), encode(sec)]
        calls = []
        for c, m in zip(p["calls"], ms):
            calls.append([c[0], minutes(c[1]), minutes(c[2]), round(m)])
        patterns[pid] = {"service": p["service"], "dir": p["dir"], "calls": calls, "sections": starts}
        if p.get("weights"):
            patterns[pid]["weights"] = p["weights"]
        log(f"{pid}: {total / 1000:.0f} km, {len(simple)} points")
    runs = []
    for r in src["runs"]:
        first = dt.date.fromisoformat(r["first"])
        runs.append([r["pattern"], first.isoformat(), int(r["weeks"]), minutes("0 " + r["dep"]), minutes(r["arr"])])
    last = max(dt.date.fromisoformat(r[1]) + dt.timedelta(weeks=r[2] - 1) for r in runs)
    meta = {"built": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "osm_base": (osm.get("osm3s") or {}).get("timestamp_osm_base"),
            "osm_sha256": hashlib.sha256(rail_raw).hexdigest(),
            "zones": ZONES_VERSION(),
            "licence": "ODbL 1.0: (c) OpenStreetMap contributors, openstreetmap.org/copyright",
            "rules": {"dp_m": DP_M, "detour": [DETOUR_X, DETOUR_EXTRA_M]},
            "seconds": round(time.time() - t0)}
    timetable = {"v": DATA_VERSION, "last_departure": last.isoformat(), "services": src["services"],
                 "stations": stations, "patterns": patterns, "runs": runs,
                 "credit": "Timetable: Journey Beyond (journeybeyondrail.com.au)"}
    log("runs", sum(r[2] for r in runs), "departures to", last.isoformat())
    return timetable, {"v": DATA_VERSION, "meta": meta, "lines": lines}


def write_gz(obj, path):
    raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=True, sort_keys=True).encode("ascii")
    with open(path, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", compresslevel=9, mtime=0) as gz:
            gz.write(raw)
    return len(raw), os.path.getsize(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("rail")
    ap.add_argument("stations")
    ap.add_argument("--report")
    a = ap.parse_args(argv)
    rep = open(a.report, "w", encoding="utf-8") if a.report else None

    def log(*x):
        line = " ".join(str(v) for v in x)
        print(line.encode("ascii", "backslashreplace").decode("ascii"), flush=True)
        if rep:
            print(line, file=rep, flush=True)
    timetable, lines = build(a.rail, a.stations, log)
    tt = json.dumps(timetable, separators=(",", ":"), ensure_ascii=False, sort_keys=True)
    with open(DATA / "journey_beyond_timetable.json", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(tt + "\n")
    raw, gz = write_gz(lines, DATA / "journey_beyond_lines.json.gz")
    log("wrote timetable", len(tt.encode("utf-8")), "bytes; lines json", raw, "bytes, gzip", gz, "bytes")


if __name__ == "__main__":
    main()
