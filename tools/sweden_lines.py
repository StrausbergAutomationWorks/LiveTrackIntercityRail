"""Build Sweden's shipped route lines (Trafikverket's station pairs on OpenStreetMap's track). Run by hand, never by
Home Assistant; the output is committed as custom_components/live_track_intercity_rail/data/sweden_lines.json.gz.

    python tools/sweden_lines.py pull  OUT.json                                     (Overpass, about a minute)
    python tools/sweden_lines.py lines OSM.json STATIONS.json ANN.json.gz [...] [--report R.txt] [--out F]

Lee 2026-11-08 ~18:2x CST (Intercity SSOT 8.9): "OSM lines, as Renfe": Sweden's timetable has no shapes, so SAW
routes every station pair its intercity trains run between once, on OpenStreetMap's track, and ships the lines; the
runtime assembles each run's line from them (sources/sweden_lines.py), as Renfe (Spain) does
(sources/renfe_ld_lines.py). (c) OpenStreetMap contributors, ODbL 1.0 (the map's credit line carries it).

INPUTS. STATIONS.json: saw_livetrack.trafikverket's stations file ({"stations": {signature: {"name", "lat", "lon",
"country"}}}). ANN.json.gz: TrainAnnouncement rows (a JSON list, one or more Stockholm days; bin\\se_trv_days.py).
Trafikverket, CC0.

THE PAIRS: every run the shared client routes to the intercity consumer (saw_livetrack.trafikverket.route_of), split
into its trips as the client splits them (split_trips), its rows in time order (arrivals before departures at a time),
consecutive distinct signatures, public or not: a row the public does not see is still a place the train passes, which
keeps the route on the right track. The runtime assembles a run's line from the same sequence.

THE ROUTING is Renfe's tool's (tools/renfe_spain_lines.py: Graph, its joins, candidate snapping and A*) with no gauge:
every Swedish line here is standard gauge (`mode` None, the plain shortest path). The pull keeps railway=rail without
sidings and yards and drops industrial, military and test usage; tourism and freight are KEPT (Inlandsbanan,
diversions). A pair with no route, or whose route is over DETOUR_X times its straight line and DETOUR_EXTRA_M longer
(a gap in OpenStreetMap forcing a detour), ships no line: the runtime keeps the straight line for that leg, and the
report lists each one to be read. Lines are simplified by Douglas-Peucker at DP_M.
"""

from __future__ import annotations

import argparse
import collections
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
OVERPASS = "https://overpass-api.de/api/interpreter"
USER_AGENT = "StrausbergAutomationWorks/live_track_intercity_rail (build)"
PULL_QUERY = ('[out:json][timeout:900];area["ISO3166-1"="SE"][admin_level=2]->.se;('
              'way["railway"="rail"]["service"!~"siding|yard"]["usage"!~"industrial|military|test"](area.se););'
              'out tags geom;')
DATA_VERSION = 1
DP_M = 15.0
DETOUR_X = 3.0
DETOUR_EXTRA_M = 10000.0


def _renfe_tool():
    spec = importlib.util.spec_from_file_location("renfe_spain_lines_tool", ROOT / "tools" / "renfe_spain_lines.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def patterns(ann_paths, route_of, call_record, split_trips):
    """{signature tuple: trips} of every intercity run in the files, each run split into its trips as the client does
    (Öresundståg 1154 and 1165 carry two trips under one number and date)."""
    runs = collections.defaultdict(list)
    for path in ann_paths:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            rows = json.load(fh)
        for r in rows:
            k = ((r.get("AdvertisedTrainIdent") or "").strip(), (r.get("ScheduledDepartureDateTime") or "")[:10])
            runs[k].append(r)
    pats = collections.Counter()
    brands = collections.Counter()
    for k, rows in runs.items():
        rows.sort(key=lambda r: (r.get("AdvertisedTimeAtLocation") or "", r.get("ActivityType") != "Ankomst"))
        route = route_of(rows)
        if not route or route[0] != "intercity":
            continue
        brands[route[1]] += 1
        calls = [call_record(r) for r in rows]
        for trip in split_trips(calls):
            sigs = []
            for c in trip:
                if c["sig"] and (not sigs or sigs[-1] != c["sig"]):
                    sigs.append(c["sig"])
            pats[tuple(sigs)] += 1
    return pats, brands


def pair_key(a, b):
    lo, hi = sorted((a, b))
    return f"{lo}|{hi}"


def build(osm_path, stations_path, ann_paths, log):
    from saw_livetrack.trafikverket import call_record, route_of, split_trips  # saw-livetrack 0.2.31 or later
    renfe = _renfe_tool()
    t0 = time.time()
    osm_raw = open(osm_path, "rb").read()
    osm = json.loads(gzip.decompress(osm_raw) if osm_path.endswith(".gz") else osm_raw)
    g = renfe.Graph(osm, log)
    st = json.load(open(stations_path, encoding="utf-8"))["stations"]
    g.stops = {s: (v["lat"], v["lon"], v["name"]) for s, v in st.items()}
    pats, brands = patterns(ann_paths, route_of, call_record, split_trips)
    log("announcement files", [os.path.basename(p) for p in ann_paths], "intercity runs", sum(pats.values()),
        "patterns", len(pats), "by brand", dict(brands))
    pairs = sorted({tuple(sorted((a, b))) for p in pats for a, b in zip(p, p[1:])
                    if a != b and a in g.stops and b in g.stops})
    unknown = sorted({s for p in pats for s in p if s not in g.stops})
    log("distinct station pairs", len(pairs), "signatures with no station", unknown)
    lines, dropped, failed = {}, [], collections.Counter()
    ratios = []
    t1 = time.time()
    for n, (a, b) in enumerate(pairs):
        r = g.route(a, b, None)
        straight = renfe.hav(g.stops[a][:2], g.stops[b][:2])
        if r is None:
            failed[g.fails.get((a, b), "?")] += 1
            dropped.append((a, b, g.stops[a][2], g.stops[b][2], round(straight), "no route: " + g.fails.get((a, b), "?")))
            continue
        _, length, nodes, _ = r
        if len(nodes) < 2:
            failed["one node"] += 1
            continue
        if length > DETOUR_X * straight + DETOUR_EXTRA_M:
            dropped.append((a, b, g.stops[a][2], g.stops[b][2], round(straight), "detour %d m" % round(length)))
            continue
        if straight > 500:
            ratios.append(length / straight)
        pts = renfe.dp([g.pts[i] for i in nodes], DP_M)
        lines[pair_key(a, b)] = [round(length, 1), encode(pts)]
        if n % 500 == 0:
            log(f"  pair {n}/{len(pairs)} {time.time() - t1:.0f}s")
    ratios.sort()
    q = lambda f: round(ratios[min(len(ratios) - 1, int(f * len(ratios)))], 2) if ratios else None
    log("pairs with a line", len(lines), "of", len(pairs), "failed", dict(failed), "dropped (straight at runtime)",
        len(dropped), f"{time.time() - t1:.0f}s")
    log("line length over straight line p50/p90/p99/max", [q(.5), q(.9), q(.99)], round(ratios[-1], 2) if ratios else None)
    for d in dropped:
        log("REVIEW straight leg:", d)
    legs_total = sum(n * (len(p) - 1) for p, n in pats.items())
    legs_lined = sum(n * sum(1 for a, b in zip(p, p[1:]) if pair_key(a, b) in lines) for p, n in pats.items())
    log("run legs with a shipped line", legs_lined, "of", legs_total, f"({100 * legs_lined / max(1, legs_total):.1f}%)")
    meta = {"built": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "osm_base": (osm.get("osm3s") or {}).get("timestamp_osm_base"),
            "osm_sha256": hashlib.sha256(osm_raw).hexdigest(),
            "announcements": [os.path.basename(p) for p in ann_paths],
            "licence": "ODbL 1.0: (c) OpenStreetMap contributors, openstreetmap.org/copyright",
            "rules": {"join_m": renfe.JOIN_M, "cand_m": renfe.CAND_M, "dp_m": DP_M,
                      "detour": [DETOUR_X, DETOUR_EXTRA_M]},
            "pairs": len(pairs), "lines": len(lines), "points": sum(len(v[1]) // 2 for v in lines.values()),
            "seconds": round(time.time() - t0)}
    return {"v": DATA_VERSION, "meta": meta, "lines": lines}


def encode(points):
    out, pla, plo = [], 0, 0
    for la, lo in points:
        a, b = round(la * 1e5), round(lo * 1e5)
        out += [a - pla, b - plo]
        pla, plo = a, b
    return out


def write_gz(obj, path):
    raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=True, sort_keys=True).encode("ascii")
    with open(path, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", compresslevel=9, mtime=0) as gz:
            gz.write(raw)
    return len(raw), os.path.getsize(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("pull")
    p1.add_argument("out")
    p2 = sub.add_parser("lines")
    p2.add_argument("osm")
    p2.add_argument("stations")
    p2.add_argument("ann", nargs="+")
    p2.add_argument("--out", default=str(DATA / "sweden_lines.json.gz"))
    p2.add_argument("--report")
    a = ap.parse_args(argv)
    rep = open(a.report, "w", encoding="utf-8") if getattr(a, "report", None) else None

    def log(*x):
        line = " ".join(str(v) for v in x)
        print(line.encode("ascii", "backslashreplace").decode("ascii"), flush=True)
        if rep:
            print(line, file=rep, flush=True)
    if a.cmd == "pull":
        import requests
        r = requests.post(OVERPASS, data={"data": PULL_QUERY}, headers={"User-Agent": USER_AGENT}, timeout=1000)
        r.raise_for_status()
        open(a.out, "wb").write(r.content)
        log("pulled", len(r.content), "bytes to", a.out)
    else:
        out = build(a.osm, a.stations, a.ann, log)
        raw, gz = write_gz(out, a.out)
        log("wrote", a.out, "json", raw, "bytes, gzip", gz, "bytes")


if __name__ == "__main__":
    main()
