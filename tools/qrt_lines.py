"""Build Queensland Rail Travel's shipped lines (Intercity SSOT 8.14). Run by hand, never by Home Assistant; the output
is committed as custom_components/live_track_intercity_rail/data/qrt_lines.json.gz.

    python tools/qrt_lines.py RAIL.json STATIONS.json [--report R.txt]

WHAT SHIPS: SAW's own material only (10_SEED/05_SHARED_LESSONS_DATA.md B18 condition 5): each line's stop pattern,
the PlaceCode -> station pairing with its position, and the line on OpenStreetMap's track. NO TIMES: every install reads
QRT's Service Updates page for its own user (sources/qrt.py).

INPUTS. tools/qrt_source.json: the pairing of QRT's PlaceCodes to OSM station elements and each line's stop pattern in
its OUT direction (from Brisbane; the Inlander from Townsville, Kuranda from Cairns, the Gulflander from Normanton),
read off QRT's own answers (bin\\qrt_make_source.py). RAIL.json: an Overpass pull of Queensland's 1067 mm track, or
untagged, rail, preserved and narrow_gauge, sidings, yards, spurs and crossovers dropped (bin\\qrt_osm_pull.py).
STATIONS.json: every station, halt and stop in Queensland from the same pull. (c) OpenStreetMap contributors, ODbL 1.0.

THE LINES, as tools/journey_beyond.py: each pattern routed leg by leg on the track (Renfe's tool's Graph and A*), joined,
simplified by Douglas-Peucker at DP_M; a leg with no route, or over DETOUR_X times its straight line plus DETOUR_EXTRA_M,
is the straight line and the report says so; where a train REVERSES at a call (legs meeting at over REVERSE_DEG) the
line is cut into sections. Each pattern ships OUT and BACK ("<pattern>_out#<n>", "<pattern>_back#<n>"): the back line is
the out line reversed, so a train always runs its line's own way. Every call carries its distance along its direction's
line (`m`).
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
SOURCE = ROOT / "tools" / "qrt_source.json"
DATA_VERSION = 1
DP_M = 15.0
DETOUR_X = 3.0
DETOUR_EXTRA_M = 20000.0
REVERSE_DEG = 150.0
BEARING_M = 3000.0


def _tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def build(rail_path, stations_path, log):
    renfe = _tool("renfe_spain_lines")
    jb = _tool("journey_beyond")          # encode, end_bearing, osm_positions: the same helpers
    t0 = time.time()
    src = json.load(open(SOURCE, encoding="utf-8"))
    rail_raw = open(rail_path, "rb").read()
    osm = json.loads(rail_raw)
    g = renfe.Graph(osm, log)
    found = jb.osm_positions(json.load(open(stations_path, encoding="utf-8")))
    stations = {}
    for sid, s in src["stations"].items():
        if s["osm"] not in found:
            raise SystemExit(f"{sid}: OSM element {s['osm']} not in the stations pull")
        la, lo = found[s["osm"]]
        g.stops[sid] = (la, lo, s["name"])
        stations[sid] = [s["name"], round(la, 5), round(lo, 5)]
        log(f"{sid} {s['name']} {la:.5f},{lo:.5f} ({s['osm']})")
    lines, patterns = {}, {}
    for pid, p in src["patterns"].items():
        seq = p["calls"]
        ms, total, legs = [0.0], 0.0, []
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
            turn = abs((jb.end_bearing(legs[i][0], renfe.hav, True) - jb.end_bearing(legs[i - 1][0], renfe.hav, False)
                        + 180) % 360 - 180)
            if turn > REVERSE_DEG:
                starts.append(i)
                log(f"{pid}: reverses at {seq[i]} ({turn:.0f} deg): a new section")
        secs = []
        for n, s in enumerate(starts):
            e = starts[n + 1] if n + 1 < len(starts) else len(legs)
            pts = []
            for leg, _ in legs[s:e]:
                pts.extend(leg if not pts else leg[1:])
            secs.append((renfe.dp(pts, DP_M), round(ms[e] - ms[s], 1)))
        nsec, ncall = len(secs), len(seq)
        for n, (pts, length) in enumerate(secs):
            lines[f"{pid}_out#{n}"] = [length, jb.encode(pts)]
            back_pts, back_len = secs[nsec - 1 - n]
            lines[f"{pid}_back#{n}"] = [back_len, jb.encode(back_pts[::-1])]
        patterns[pid] = {
            "line": p["line"], "prefix": p["prefix"], "picture": p["picture"],
            "out": {"calls": [[c, round(m)] for c, m in zip(seq, ms)], "sections": starts},
            "back": {"calls": [[c, round(total - m)] for c, m in zip(seq[::-1], ms[::-1])],
                     "sections": [0] + sorted(ncall - 1 - s for s in starts[1:])}}
        log(f"{pid}: {total / 1000:.0f} km, {sum(len(x[0]) for x in secs)} points, sections {starts}")
    meta = {"built": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "osm_base": (osm.get("osm3s") or {}).get("timestamp_osm_base"),
            "osm_sha256": hashlib.sha256(rail_raw).hexdigest(),
            "licence": "ODbL 1.0: (c) OpenStreetMap contributors, openstreetmap.org/copyright",
            "rules": {"dp_m": DP_M, "detour": [DETOUR_X, DETOUR_EXTRA_M]},
            "seconds": round(time.time() - t0)}
    return {"v": DATA_VERSION, "meta": meta, "stations": stations, "patterns": patterns, "lines": lines}


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
    data = build(a.rail, a.stations, log)
    raw = json.dumps(data, separators=(",", ":"), ensure_ascii=True, sort_keys=True).encode("ascii")
    path = DATA / "qrt_lines.json.gz"
    with open(path, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", compresslevel=9, mtime=0) as gz:
            gz.write(raw)
    log("wrote", path.name, "json", len(raw), "bytes, gzip", os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
