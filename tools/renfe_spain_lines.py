"""Build Renfe (Spain)'s shipped data: the route lines and the end-city table. Run by hand, never by Home
Assistant; the output is committed under custom_components/live_track_intercity_rail/data/.

    python tools/renfe_spain_lines.py pull  OUT.json                        (Overpass, about 90 s)
    python tools/renfe_spain_lines.py lines OSM.json TIMETABLE.zip [--report R.txt]
    python tools/renfe_spain_lines.py ends  TIMETABLE.zip [--report R.txt]  (Overpass and Wikidata)

TIMETABLE.zip is Renfe's AV/LD/MD GTFS (ssl.renfe.com/gtransit/Fichero_AV_LD/google_transit.zip, Renfe,
CC BY 4.0); OSM.json an Overpass answer with `out geom` (OpenStreetMap contributors, ODbL 1.0).

THE LINES. Every rule below is the prototype's (bin\\es_osm_graph2.py on 2026-11-06; Intercity SSOT 8.7 (d),
why each one exists in its RECORD.md 8.7), kept as the build must keep them:
* `railway` rail AND narrow_gauge, only siding and yard dropped (in the pull);
* a track end within JOIN_M of another way's node is joined to it (an OSM drawing gap), never across
  two gauges with nothing in common;
* each pair routed per gauge (1435, 1668, 1000), a metre of track tagged with other gauges 3x, untagged 1x;
* snapped per gauge to several candidates per stop (the nearest node of each way within CAND_M), routed
  many-to-many with A*;
* a gauge-preferred route over 25% + 5 km longer than the plain shortest path is a detour the penalty
  forced: the plain path's line is shipped under that gauge, with the gauge's own cost (round 2c);
* the gauge per LEG chosen by the runtime's own Viterbi (sources/renfe_ld_lines.choose: a change 30 km,
  the service prior x1.3), over every gauge routed, for every stop pattern of the timetable; the
  (pair, gauge) lines it picks are shipped, simplified by Douglas-Peucker at DP_M.
Pairs are routed once, from the lower stop id to the higher (the prototype routed each direction).

THE END CITIES (SSOT 8.7, decided 10:55 CST): a train whose stops include Madrid takes Madrid as its hub;
any other takes the larger of its two end cities. Each end stop's municipality from OpenStreetMap's
boundaries (Overpass is_in): admin_level 8, but 7 in Portugal (8 is a parish there: Porto Campanha came
back as Campanha); its population from Wikidata P1082 (preferred rank, else the latest), OpenStreetMap's
own `population` where Wikidata's is implausible against it (over 10x apart; Valencia de Alcantara:
Wikidata 1, OSM 5,140) or absent; and SERVES for a station that stands outside the town it serves
(Figueres-Vilafant stands in Vilafant). Every end whose municipality is not in its station's name is
listed in the report, to be read.
"""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import gzip
import hashlib
import heapq
import importlib
import importlib.machinery
import importlib.util
import io
import json
import math
import os
import pathlib
import sys
import time
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
COMP = ROOT / "custom_components" / "live_track_intercity_rail"
DATA = COMP / "data"
USER_AGENT = "StrausbergAutomationWorks/live_track_intercity_rail (build)"

# The component's HA-free modules, without its package __init__ (which imports Home Assistant).
if "ltir" not in sys.modules:
    _spec = importlib.machinery.ModuleSpec("ltir", None, is_package=True)
    _pkg = importlib.util.module_from_spec(_spec)
    _pkg.__path__ = [str(COMP)]
    sys.modules["ltir"] = _pkg
lines_mod = importlib.import_module("ltir.sources.renfe_ld_lines")

JOIN_M = 30.0
CAND_M = 500.0
SNAP_LIMIT_M = 1500.0
CAND_FALLBACK_M = 3000.0
OFF_GAUGE_X = 3.0
GUARD_RATIO, GUARD_EXTRA_M = 1.25, 5000.0
DP_M = 15.0
MODES = lines_mod.GAUGES
hav = lines_mod.metres

OVERPASS = "https://overpass-api.de/api/interpreter"
# The prototype's pull, byte for byte (bin\\es_osm_rail_pull2.py, 2026-11-06T14:01:31Z: 44,038 ways, 421,888
# points): Spain, rail and narrow gauge, sidings and yards dropped, and industrial, military, freight, test, yard,
# siding and crane usage; plus main and branch rail with no service tag in two boxes round the timetable's stops
# with no Spanish track within about 3 km, in France and in Portugal. The Portuguese box stops short of
# Valenca-Viana do Castelo, one of the 24 unrouted pairs.
PULL_QUERY = ('[out:json][timeout:900];area["ISO3166-1"="ES"][admin_level=2]->.es;('
              'way["railway"~"^(rail|narrow_gauge)$"]["service"!~"siding|yard"]'
              '["usage"!~"industrial|military|freight|test|yard|siding|crane"](area.es);'
              'way["railway"="rail"]["usage"~"^(main|branch)$"]["service"!~"."](42.396,2.58,46.06,5.682);'
              'way["railway"="rail"]["usage"~"^(main|branch)$"]["service"!~"."](40.849,-9.131,41.995,-8.245););'
              'out tags geom;')


def rows(z: zipfile.ZipFile, name: str):
    with z.open(name) as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")):
            # Renfe pads every field (05_SHARED_LESSONS.md B5).
            yield {(k or "").strip(): (v or "").strip() for k, v in r.items() if k}


def timetable(path: str):
    """(stops {id: (lat, lon, name)}, patterns {stop ids: [trip ids]}, family of each trip, digest)."""
    raw = open(path, "rb").read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    stops = {s["stop_id"]: (float(s["stop_lat"]), float(s["stop_lon"]), s.get("stop_name", ""))
             for s in rows(z, "stops.txt") if s.get("stop_lat") and s.get("stop_lon")}
    family = {r["route_id"]: (r.get("route_short_name") or "").upper() for r in rows(z, "routes.txt")}
    trip_family = {t["trip_id"]: family.get(t["route_id"], "") for t in rows(z, "trips.txt")}
    seq = collections.defaultdict(list)
    for st in rows(z, "stop_times.txt"):
        seq[st["trip_id"]].append((int(st["stop_sequence"]), st["stop_id"]))
    patterns = collections.defaultdict(list)
    for tid, r in seq.items():
        patterns[tuple(s for _, s in sorted(r))].append(tid)
    return stops, patterns, trip_family, hashlib.sha256(raw).hexdigest()


def dp(line, tol):
    """Douglas-Peucker, iterative (a line can hold tens of thousands of points)."""
    if len(line) < 3:
        return list(line)
    keep = [False] * len(line)
    keep[0] = keep[-1] = True
    stack = [(0, len(line) - 1)]
    while stack:
        i0, i1 = stack.pop()
        a, b = line[i0], line[i1]
        ky = 111320.0
        kx = 111320.0 * math.cos(math.radians(a[0]))
        ax, ay, bx, by = a[1] * kx, a[0] * ky, b[1] * kx, b[0] * ky
        dx, dy = bx - ax, by - ay
        ln = math.hypot(dx, dy) or 1e-9
        best, bi = -1.0, i0
        for i in range(i0 + 1, i1):
            px, py = line[i][1] * kx, line[i][0] * ky
            d = abs(dx * (ay - py) - dy * (ax - px)) / ln
            if d > best:
                best, bi = d, i
        if best > tol:
            keep[bi] = True
            stack += [(i0, bi), (bi, i1)]
    return [p for p, k in zip(line, keep) if k]


class Graph:
    """OpenStreetMap's track as a graph: a node per coordinate (OSM's shared nodes have identical
    coordinates), an edge per way segment, dead ends joined, snapped and routed per gauge."""

    def __init__(self, osm: dict, log) -> None:
        self.ways = ways = [e for e in osm["elements"] if e.get("type") == "way" and e.get("geometry")]
        log("ways", len(ways))
        idx: dict = {}
        self.pts = pts = []
        self.adj = adj = []

        def nid(k):
            i = idx.get(k)
            if i is None:
                i = idx[k] = len(pts)
                pts.append(k)
                adj.append([])
            return i

        for wi, w in enumerate(ways):
            g = [(round(x["lat"], 7), round(x["lon"], 7)) for x in w["geometry"]]
            for a, b in zip(g, g[1:]):
                i, j = nid(a), nid(b)
                d = hav(a, b)
                adj[i].append((j, d, wi))
                adj[j].append((i, d, wi))
        log("graph nodes", len(pts), "edges", sum(len(a) for a in adj) // 2)
        # Dead ends: a track end within JOIN_M of another way's node, never across two gauges with
        # nothing in common (the ways' own gauge tags).
        tag_g = [set(w.get("tags", {}).get("gauge", "").split(";")) - {""} for w in ways]
        cells = collections.defaultdict(list)
        for i, (la, lo) in enumerate(pts):
            cells[(int(la * 2000), int(lo * 2000))].append(i)
        joins, jd = 0, []
        for u in range(len(pts)):
            if len(adj[u]) != 1:
                continue
            wu = adj[u][0][2]
            mine = {v for v, _, _ in adj[u]}
            la, lo = pts[u]
            best = (JOIN_M, -1)
            ci, cj = int(la * 2000), int(lo * 2000)
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    for v in cells.get((ci + di, cj + dj), ()):
                        if v == u or v in mine or any(x[2] == wu for x in adj[v]):
                            continue
                        gu = tag_g[wu]
                        gv = set().union(*(tag_g[x[2]] for x in adj[v]))
                        if gu and gv and not (gu & gv):
                            continue
                        d = hav(pts[u], pts[v])
                        if d < best[0]:
                            best = (d, v)
            if best[1] >= 0:
                v = best[1]
                adj[u].append((v, best[0], wu))
                adj[v].append((u, best[0], wu))
                joins += 1
                jd.append(best[0])
        jd.sort()
        log("dead ends joined within", JOIN_M, "m:", joins,
            "p50/p90", [round(jd[int(f * (len(jd) - 1))], 1) for f in (.5, .9)] if jd else None)
        self.comp = comp = [-1] * len(pts)
        sizes = []
        for s in range(len(pts)):
            if comp[s] >= 0:
                continue
            c = len(sizes)
            comp[s] = c
            stack, n = [s], 0
            while stack:
                u = stack.pop()
                n += 1
                for v, _, _ in adj[u]:
                    if comp[v] < 0:
                        comp[v] = c
                        stack.append(v)
            sizes.append(n)
        log("components", len(sizes), "largest", sorted(sizes, reverse=True)[:5])

        def gauges(wi):
            t = ways[wi].get("tags", {})
            g = t.get("gauge")
            if not g and t.get("railway") == "narrow_gauge":
                g = "1000"
            return frozenset((g or "").split(";")) - {""}

        self.wg = [gauges(wi) for wi in range(len(ways))]
        self.grid = collections.defaultdict(list)
        for i, (la, lo) in enumerate(pts):
            self.grid[(int(la * 100), int(lo * 100))].append(i)
        node_g = [set() for _ in pts]
        for u in range(len(pts)):
            for _, _, wi in adj[u]:
                node_g[u] |= self.wg[wi]
        self.mgrid = {m: collections.defaultdict(list) for m in MODES}
        for i, (la, lo) in enumerate(pts):
            for m in MODES:
                if m in node_g[i]:
                    self.mgrid[m][(int(la * 100), int(lo * 100))].append(i)
        self.stops: dict = {}
        self._snap: dict = {}
        self._snapm: dict = {}
        self._cands: dict = {}
        self._routes: dict = {}
        self.fails: dict = {}

    # --- snapping -------------------------------------------------------------------------
    def snap(self, sid):
        """(m, node): the nearest node of any way, searched in rings of 0.01 degree."""
        if sid in self._snap:
            return self._snap[sid]
        la, lo = self.stops[sid][:2]
        best = (1e18, -1)
        ci, cj = int(la * 100), int(lo * 100)
        for r in range(0, 6):
            for di in range(-r, r + 1):
                for dj in range(-r, r + 1):
                    if max(abs(di), abs(dj)) != r:
                        continue
                    for i in self.grid.get((ci + di, cj + dj), ()):
                        d = hav((la, lo), self.pts[i])
                        if d < best[0]:
                            best = (d, i)
            if best[1] >= 0 and best[0] < r * 800:
                break
        self._snap[sid] = best
        return best

    def snap_m(self, sid, mode):
        """The nearest node carrying `mode`'s gauge within SNAP_LIMIT_M, else snap()."""
        k = (sid, mode)
        if k not in self._snapm:
            la, lo = self.stops[sid][:2]
            ci, cj = int(la * 100), int(lo * 100)
            best = (1e18, -1)
            for di in range(-2, 3):
                for dj in range(-2, 3):
                    for i in self.mgrid[mode].get((ci + di, cj + dj), ()):
                        d = hav((la, lo), self.pts[i])
                        if d < best[0]:
                            best = (d, i)
            self._snapm[k] = best if best[0] <= SNAP_LIMIT_M else self.snap(sid)
        return self._snapm[k]

    def cand(self, sid, mode):
        """[(node, m)]: the nearest node of each way of `mode`'s gauge (any way for None, untagged
        ways always) within CAND_M; failing that, the per-gauge snap within CAND_FALLBACK_M."""
        k = (sid, mode)
        if k in self._cands:
            return self._cands[k]
        la, lo = self.stops[sid][:2]
        ci, cj = int(la * 100), int(lo * 100)
        per_way: dict = {}
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for i in self.grid.get((ci + di, cj + dj), ()):
                    d = hav((la, lo), self.pts[i])
                    if d > CAND_M:
                        continue
                    for _, _, wi in self.adj[i]:
                        if mode is not None and self.wg[wi] and mode not in self.wg[wi]:
                            continue
                        if d < per_way.get(wi, (1e18,))[0]:
                            per_way[wi] = (d, i)
        out: dict = {}
        for d, i in per_way.values():
            out[i] = min(d, out.get(i, 1e18))
        if not out:
            d, i = self.snap_m(sid, mode) if mode is not None else self.snap(sid)
            if i >= 0 and d <= CAND_FALLBACK_M:
                out[i] = d
        self._cands[k] = list(out.items())
        return self._cands[k]

    # --- routing --------------------------------------------------------------------------
    def _astar_multi(self, srcs, tgts, goal, cap, mode):
        dist, prev, h = {}, {}, []
        for n, d0 in srcs:
            if d0 < dist.get(n, 1e18):
                dist[n] = d0
                heapq.heappush(h, (d0 + max(0.0, hav(self.pts[n], goal) - CAND_M), d0, n))
        start = {n for n, _ in srcs}
        tg = dict(tgts)
        best = (1e18, -1)
        while h:
            f, d, u = heapq.heappop(h)
            if f >= best[0]:
                break
            if d > dist.get(u, 1e18) or d > cap:
                continue
            if u in tg and d + tg[u] < best[0]:
                best = (d + tg[u], u)
            for v, w, wi in self.adj[u]:
                gs = self.wg[wi]
                nd = d + (w if (mode is None or not gs or mode in gs) else OFF_GAUGE_X * w)
                if nd < dist.get(v, 1e18):
                    dist[v] = nd
                    prev[v] = (u, wi, w)
                    heapq.heappush(h, (nd + max(0.0, hav(self.pts[v], goal) - CAND_M), nd, v))
        if best[1] < 0:
            return None
        g = best[1]
        path, used, length = [g], [], 0.0
        while path[-1] not in start:
            u, wi, w = prev[path[-1]]
            used.append((wi, w))
            length += w
            path.append(u)
        return best[0], length, path[::-1], used[::-1]

    def route(self, a, b, mode):
        """(cost, length m, node path, [(way, m)]) from stop a to stop b for `mode` (None: plain
        shortest), or None with the reason in self.fails."""
        k = (a, b, mode)
        if k in self._routes:
            return self._routes[k]
        A, B, r = self.cand(a, mode), self.cand(b, mode), None
        Bc = [(n, d) for n, d in B if any(self.comp[n] == self.comp[m] for m, _ in A)]
        if not A or not B:
            self.fails[(a, b)] = "snap over 3 km"
        elif not Bc:
            self.fails[(a, b)] = "different components"
        else:
            sl = hav(self.stops[a][:2], self.stops[b][:2])
            r = self._astar_multi(A, Bc, self.stops[b][:2], max(3 * 4 * sl, 30000), mode)
            if r is None:
                self.fails[(a, b)] = "no path"
        self._routes[k] = r
        return r


def q(xs, f):
    return xs[min(len(xs) - 1, int(f * len(xs)))] if xs else None


def build_lines(osm_path: str, zip_path: str, log) -> dict:
    t0 = time.time()
    osm_raw = open(osm_path, "rb").read()
    osm = json.loads(osm_raw)
    g = Graph(osm, log)
    stops, patterns, trip_family, tt_digest = timetable(zip_path)
    g.stops = stops
    log("timetable", os.path.basename(zip_path), "stops", len(stops), "trips", len(trip_family),
        "stop patterns", len(patterns), f"{time.time() - t0:.0f}s")
    legs_of = {ids: [(a, b) for a, b in zip(ids, ids[1:]) if a != b and a in stops and b in stops]
               for ids in patterns}
    pairs = sorted({tuple(sorted(p)) for legs in legs_of.values() for p in legs})
    log("distinct stop pairs (unordered)", len(pairs))
    entries: dict = {}            # (lo, hi, gauge) -> (cost, length, nodes, gauge km Counter)
    guarded = degenerate = 0
    t1 = time.time()
    for n, (lo, hi) in enumerate(pairs):
        plain = None
        for m in MODES:
            r = g.route(lo, hi, m)
            if r is None:
                continue
            cost, length, nodes, used = r
            if plain is None:
                plain = g.route(lo, hi, None)
            if plain is not None and length > GUARD_RATIO * plain[1] + GUARD_EXTRA_M:
                # A detour the penalty forced: the plain path, under this gauge's cost.
                _, length, nodes, used = plain
                guarded += 1
            if len(nodes) < 2:
                # Both stops snapped to one node (two stops a few hundred metres apart, 12 such pairs on the
                # 2026-11-05 timetable): no line; the leg keeps the straight line.
                degenerate += 1
                continue
            km = collections.Counter()
            for wi, w in used:
                km["/".join(sorted(g.wg[wi])) or "-"] += w / 1000.0
            entries[(lo, hi, m)] = (round(cost, 1), round(length, 1), nodes, km)
        if n % 500 == 0:
            log(f"  pair {n}/{len(pairs)} {time.time() - t1:.0f}s")
    routed = {(lo, hi) for lo, hi, _ in entries}
    fails = collections.Counter(g.fails.get(p) or g.fails.get(p[::-1]) or "one node" for p in pairs if p not in routed)
    log("pairs routed", len(routed), "of", len(pairs), f"({100 * len(routed) / max(1, len(pairs)):.1f}%)",
        "unrouted by reason", dict(fails), "legs replaced by the plain path", guarded,
        "routes of one node dropped", degenerate, f"{time.time() - t1:.0f}s")
    log("unrouted:", [(stops[a][2], stops[b][2], round(hav(stops[a][:2], stops[b][:2]))) for a, b in pairs
                      if (a, b) not in routed])
    # The runtime's own choice, over every gauge routed, per pattern and per family on it.
    used_keys: set = set()
    choices: dict = {}
    fam_km = collections.defaultdict(collections.Counter)
    for ids, tids in patterns.items():
        legs = legs_of[ids]
        if not legs:
            continue
        fams = collections.Counter(trip_family.get(t, "") for t in tids)
        coords = {s: v[:2] for s, v in stops.items()}
        for fam, ntrips in fams.items():
            opts = []
            for a, b in legs:
                lo, hi = sorted((a, b))
                opts.append({m: entries[(lo, hi, m)][0] for m in MODES if (lo, hi, m) in entries})
            gs = lines_mod.choose(lines_mod.leg_options(opts, legs, coords), lines_mod.preferred_gauge(fam))
            gs = [None if not o else m for o, m in zip(opts, gs)]
            choices[(ids, fam)] = gs
            for (a, b), m in zip(legs, gs):
                if m is None:
                    continue
                lo, hi = sorted((a, b))
                used_keys.add((lo, hi, m))
                for k, v in entries[(lo, hi, m)][3].items():
                    fam_km[fam][k] += v * ntrips
    log("trip-km by the track's gauge tag, per service (share):")
    for fam, c in sorted(fam_km.items(), key=lambda kv: -sum(kv[1].values())):
        tot = sum(c.values()) or 1
        log(f"   {fam}: {round(tot)} km  " + ", ".join(f"{k} {100 * v / tot:.1f}%" for k, v in c.most_common(4)))
    ratios = sorted(entries[k][1] / max(1.0, hav(stops[k[0]][:2], stops[k[1]][:2]))
                    for k in used_keys if hav(stops[k[0]][:2], stops[k[1]][:2]) > 500)
    log("shipped line length over straight line p50/p90/p99/max",
        [round(q(ratios, f), 2) for f in (.5, .9, .99)], round(ratios[-1], 2) if ratios else None)
    lines = {}
    npts = 0
    for lo, hi, m in sorted(used_keys):
        cost, length, nodes, _ = entries[(lo, hi, m)]
        pts = dp([g.pts[i] for i in nodes], DP_M)
        npts += len(pts)
        lines[lines_mod.pair_key(lo, hi, m)] = [length, cost, lines_mod.encode(pts)]
    meta = {
        "built": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "osm_base": (osm.get("osm3s") or {}).get("timestamp_osm_base"),
        "osm_sha256": hashlib.sha256(osm_raw).hexdigest(),
        "timetable": os.path.basename(zip_path), "timetable_sha256": tt_digest,
        "licence": "ODbL 1.0: (c) OpenStreetMap contributors, openstreetmap.org/copyright",
        "rules": {"join_m": JOIN_M, "cand_m": CAND_M, "off_gauge_x": OFF_GAUGE_X, "guard": [GUARD_RATIO, GUARD_EXTRA_M],
                  "dp_m": DP_M, "switch_m": lines_mod.SWITCH_M, "prior_x": lines_mod.PRIOR_X},
        "pairs": len(pairs), "pairs_routed": len(routed), "lines": len(lines), "points": npts,
    }
    out = {"v": lines_mod.DATA_VERSION, "meta": meta, "lines": lines}
    # The check that matters: the runtime, reading only what is shipped, chooses what the build chose.
    shipped = lines_mod.ShippedLines(json.loads(json.dumps(out)))
    coords = {s: v[:2] for s, v in stops.items()}
    differ = 0
    for (ids, fam), gs in choices.items():
        if shipped.assemble(ids, coords, fam)[2] != gs:
            differ += 1
    log("runtime choice differs from the build's on", differ, "of", len(choices), "pattern-families")
    if differ:
        raise SystemExit("the shipped lines do not reproduce the build's choice")
    plain_5dp = sum(len(json.dumps([[round(a, 5), round(b, 5)] for a, b in lines_mod.decode(v[2])],
                                   separators=(",", ":"))) for v in lines.values())
    log("lines", len(lines), "points", npts, "as plain JSON at 5 decimals", plain_5dp, "bytes",
        f"total {time.time() - t0:.0f}s")
    return out


def write_gz(obj, path):
    raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    with open(path, "wb") as fh:
        # mtime 0: the same lines give the same bytes.
        with gzip.GzipFile(fileobj=fh, mode="wb", compresslevel=9, mtime=0) as gz:
            gz.write(raw)
    return len(raw), os.path.getsize(path)


# --- the end cities -----------------------------------------------------------------------
MADRID_PREFIX = "madrid"
# A station outside the town it serves: stop name -> the municipality it serves (SSOT 8.7).
SERVES = {"Figueres-Vilafant": "Figueres"}


def madrid(name: str) -> bool:
    return (name or "").strip().lower().startswith(MADRID_PREFIX)


def end_stops(zip_path: str) -> dict:
    """{stop id: (name, lat, lon, trips)} for the first and last stops of every trip with no Madrid stop."""
    z = zipfile.ZipFile(zip_path)
    stops = {s["stop_id"]: s for s in rows(z, "stops.txt")}
    seq = collections.defaultdict(list)
    for st in rows(z, "stop_times.txt"):
        seq[st["trip_id"]].append((int(st["stop_sequence"]), st["stop_id"]))
    ends = collections.Counter()
    for r in seq.values():
        ids = [s for _, s in sorted(r)]
        if any(madrid(stops.get(s, {}).get("stop_name", "")) for s in ids):
            continue
        ends[ids[0]] += 1
        ends[ids[-1]] += 1
    return {s: (stops[s]["stop_name"], float(stops[s]["stop_lat"]), float(stops[s]["stop_lon"]), n)
            for s, n in ends.items()}


def _post(query, requests):
    for attempt in range(4):
        try:
            r = requests.post(OVERPASS, data={"data": query}, headers={"User-Agent": USER_AGENT}, timeout=330)
            if r.status_code == 200:
                return r.json()
            if r.status_code not in (429, 502, 503, 504):
                raise SystemExit(f"Overpass answered HTTP {r.status_code}")
        except ValueError:
            pass
        time.sleep(30 * (attempt + 1))
    raise SystemExit("Overpass did not answer")


def build_ends(zip_path: str, log) -> dict:
    import requests
    ends = end_stops(zip_path)
    log("end stops of trips with no Madrid stop:", len(ends))
    found: dict = {}
    items = sorted(ends.items(), key=lambda kv: -kv[1][3])
    for i in range(0, len(items), 16):
        query = "[out:json][timeout:300];"
        for sid, (_, la, lo, _) in items[i:i + 16]:
            query += (f'make mark id="{sid}";out;is_in({la},{lo})->.a;'
                      f'area.a["boundary"="administrative"]["admin_level"~"^(2|7|8)$"];out tags;')
        cur, lv = None, {}

        def flush():
            if cur is None:
                return
            portugal = (lv.get("2") or {}).get("ISO3166-1") == "PT"
            found[cur] = (lv.get("7") if portugal else lv.get("8")) or lv.get("8") or lv.get("7") or {}
        for el in _post(query, requests).get("elements", []):
            if el.get("type") == "mark":
                flush()
                cur, lv = el["tags"]["id"], {}
            else:
                t = el.get("tags", {})
                lv.setdefault(t.get("admin_level"), t)
        flush()
        log(f"  {min(i + 16, len(items))} of {len(items)}")
        time.sleep(3)
    for name, town in SERVES.items():
        for sid, (sname, *_rest) in ends.items():
            if sname == name:
                res = _post(f'[out:json][timeout:60];area["boundary"="administrative"]["admin_level"="8"]'
                            f'["name"="{town}"];out tags;', requests).get("elements", [])
                if res:
                    found[sid] = dict(res[0].get("tags", {}), _serves=town)
    qids = sorted({t.get("wikidata") for t in found.values() if t.get("wikidata")})
    pops: dict = {}
    for i in range(0, len(qids), 40):
        r = requests.get("https://www.wikidata.org/w/api.php", headers={"User-Agent": USER_AGENT}, timeout=60,
                         params={"action": "wbgetentities", "ids": "|".join(qids[i:i + 40]), "props": "claims",
                                 "format": "json"}).json()
        for qid, ent in r.get("entities", {}).items():
            best = None
            for c in ent.get("claims", {}).get("P1082", []):
                try:
                    amount = int(float(c["mainsnak"]["datavalue"]["value"]["amount"]))
                except (KeyError, TypeError, ValueError):
                    continue
                when = ((c.get("qualifiers", {}).get("P585") or [{}])[0].get("datavalue", {})
                        .get("value", {}).get("time", ""))
                key = (c.get("rank") == "preferred", when)
                if best is None or key > best[0]:
                    best = (key, amount, when[1:11])
            if best:
                pops[qid] = (best[1], best[2])
    out = {}
    review = []
    for sid, (name, _, _, trips) in sorted(ends.items()):
        t = found.get(sid) or {}
        wd = pops.get(t.get("wikidata") or "")
        try:
            osm_pop = int(str(t.get("population", "")).replace(" ", "").replace(",", ""))
        except ValueError:
            osm_pop = None
        if wd and (osm_pop is None or osm_pop / 10 <= wd[0] <= osm_pop * 10):
            pop, src, as_of = wd[0], "wikidata", wd[1]
        elif osm_pop is not None:
            pop, src, as_of = osm_pop, "osm", t.get("population:date")
        else:
            pop, src, as_of = None, None, None
        town = t.get("name")
        out[sid] = {"stop": name, "trips": trips, "municipality": town, "admin_level": t.get("admin_level"),
                    "wikidata": t.get("wikidata"), "population": pop, "population_source": src, "as_of": as_of}
        if t.get("_serves"):
            out[sid]["serves"] = t["_serves"]
        if wd and osm_pop is not None and src == "osm":
            review.append(f"Wikidata implausible: {name}: {wd[0]} against OSM {osm_pop}")
        if not town or town.split(" ")[0].lower() not in name.lower():
            review.append(f"station name without its municipality: {name} -> {town} ({pop})")
        if pop is None:
            review.append(f"no population: {name} ({town})")
    for line in review:
        log("REVIEW", line)
    log("end stops", len(out), "with a population", sum(1 for v in out.values() if v["population"]))
    return {"v": lines_mod.DATA_VERSION, "meta": {
        "built": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "timetable": os.path.basename(zip_path),
        "sources": "municipality: OpenStreetMap boundaries (ODbL 1.0); population: Wikidata P1082 (CC0), "
                   "else OpenStreetMap"}, "stops": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("pull")
    p1.add_argument("out")
    p2 = sub.add_parser("lines")
    p2.add_argument("osm")
    p2.add_argument("timetable")
    p2.add_argument("--out", default=str(DATA / "renfe_spain_lines.json.gz"))
    p2.add_argument("--report")
    p3 = sub.add_parser("ends")
    p3.add_argument("timetable")
    p3.add_argument("--out", default=str(DATA / "renfe_spain_ends.json"))
    p3.add_argument("--report")
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
    elif a.cmd == "lines":
        out = build_lines(a.osm, a.timetable, log)
        raw, gz = write_gz(out, a.out)
        log("wrote", a.out, "json", raw, "bytes, gzip", gz, "bytes")
    else:
        out = build_ends(a.timetable, log)
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        log("wrote", a.out)


if __name__ == "__main__":
    main()
