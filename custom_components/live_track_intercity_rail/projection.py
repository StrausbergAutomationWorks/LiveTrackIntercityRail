"""Fleet's published trains, each moved along its route to now. No HA imports.

The coordinator runs this in the executor after Fleet: Fleet decides what is
published and tracks the REAL fixes; this only changes where a published
train is drawn, and says so (06_MAP_CONTRACT.md D3, `position_source`).

A record whose position is an estimate:
* `latitude`/`longitude` are the estimate; `position_source` is "estimated";
* `fix_latitude`/`fix_longitude` are the source's fix it was moved from, and
  `observed_at` stays that fix's time, so the recorder keeps the real track
  and nothing claims the estimate was observed;
* `previous_*` and `segment_duration_s` are DROPPED: they describe the slide
  between two observed fixes (D3c), and a card catching up a marker seen for
  the first time would slide it from the last fix toward the estimate in a
  straight line, the thing the estimate exists to avoid.
Every other train in service carries `position_source: "observed"`.

A train with a line is drawn ON it (Lee 2026-10-09 20:38, "snap so train
stays on the tracks"), so a fix even a metre off its line is "estimated" from
the moment it arrives; "observed" is a fix exactly on its line, or a train
with no line at all.
"""

from __future__ import annotations

from typing import Any

from .geometry import MAX_HORIZON_S, Projector
from .sources.base import AIM_ETA_KEY, HELD_SPEED_KEY, TIMED_AFTER_KEY, Snapshot

ESTIMATED = "estimated"
OBSERVED = "observed"
# Below this reported speed a train is at rest: no course_deg (D3c-iii), and
# its picture is HELD at its line's bearing (D4, icon_rotation_basis "held").
MOVING_KMH = 1.0
SEGMENT_KEYS = ("previous_latitude", "previous_longitude", "previous_observed_at",
                "segment_duration_s")


def apply(projector: Projector | None, snap: Snapshot, result: dict[str, Any],
          now: float, derive_speed: bool = False, timed: bool = False,
          horizon: float | None = None) -> dict[str, int]:
    """Move each published train in `result` along its route, in place.
    Returns {"estimated": n, "observed": n} for diagnostics.

    derive_speed: the source reports no speed (Brightline); a train moves at
    the speed of its last two fixes along its line (Projector.fix_speed), and
    that speed decides moving or at rest. It is never published as
    speed_kmh, which is the speed the SOURCE reported (D2).

    timed: a fix past the horizon moves toward the next stop arriving at the
    source's estimate for it (Operator.timed_without_fix, VIA;
    geometry.Projector.estimate). horizon: when, by railroad
    (Operator.timed_after_s); None, geometry.MAX_HORIZON_S."""
    counts = {ESTIMATED: 0, OBSERVED: 0}
    if projector is not None:
        for vid in result.get("departed") or ():
            projector.forget(vid)
    obs = {o.vehicle_id: o for o in snap.observations}
    for vid, rec in (result.get("vehicles") or {}).items():
        o = obs.get(vid)
        if o is None or not rec.get("in_service"):
            continue
        fix = (rec.get("latitude"), rec.get("longitude"))
        est = None
        extra = snap.extras.get(vid) or {}
        # A HELD fix (the source has no position now; VIA) keeps the speed it
        # was reported with for the estimate, never published (D2: speed_kmh
        # is what the source reports now).
        kmh = extra.get("speed_kmh", extra.get(HELD_SPEED_KEY))
        # Only a record standing at this poll's own fix is moved: anything
        # else is a position Fleet chose (a held one), and Fleet's call stands.
        if projector is not None and o.train and fix == (o.lat, o.lon):
            est = projector.estimate(
                # The train number, or the key the source names for its line
                # (VR: the number on its departure date; Snapshot.route_keys).
                vid, snap.route_keys.get(vid, o.train), fix,
                o.observed_at.timestamp() if o.observed_at is not None else None,
                snap.stop_codes.get(vid),
                kmh / 3.6 if kmh is not None else None,
                now, derive_speed=derive_speed,
                # The source's own aim where it gives one (AIM_ETA_KEY; None
                # holds the train where it was last drawn), else the next stop's.
                eta=(extra[AIM_ETA_KEY] if AIM_ETA_KEY in extra
                     else (snap.next_stops.get(vid) or (None, None))[1]),
                horizon=extra.get(TIMED_AFTER_KEY, MAX_HORIZON_S if horizon is None else horizon),
                # An aim the source gives is ahead of the train (Norway's tunnel push).
                toward_stop=extra.get(AIM_ETA_KEY) is not None,
                # Not a train standing at a platform with an unchanged fix: it
                # would creep toward its next stop before it leaves. A held
                # fix (no position now) or a train reported moving.
                timed=timed and (HELD_SPEED_KEY in extra
                                 or (kmh is not None and kmh >= MOVING_KMH)))
            if kmh is None and derive_speed and est is not None:
                derived = projector.fix_speed(vid)
                if derived is not None:
                    kmh = derived * 3.6
        crs = projector.course(vid) if est is not None else None
        path = projector.path(vid) if est is not None else None
        if path is not None:
            # The line it moved along since the last poll: the card slides
            # along it instead of across (06_MAP_CONTRACT.md D3c-v).
            rec["track_path"] = path
        if crs is not None:
            # The line's bearing, the way the train is going: what the marker
            # moves along. Replaces Fleet's chord between two fixes 3-5
            # minutes apart (geometry.Projector.course, measured there).
            if kmh is not None and kmh >= MOVING_KMH:
                rec["course_deg"] = crs
                rec["icon_rotation_basis"] = "course"
            else:
                rec.pop("course_deg", None)
                rec["icon_rotation_basis"] = "held"
            rec["icon_rotation_deg"] = crs
        if est is None or est == fix:
            rec["position_source"] = OBSERVED
            counts[OBSERVED] += 1
            continue
        rec["fix_latitude"], rec["fix_longitude"] = fix
        rec["latitude"], rec["longitude"] = est
        rec["position_source"] = ESTIMATED
        for key in SEGMENT_KEYS:
            rec.pop(key, None)
        counts[ESTIMATED] += 1
    return counts
