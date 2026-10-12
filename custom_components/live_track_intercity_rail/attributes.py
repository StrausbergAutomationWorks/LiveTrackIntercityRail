"""Train record -> geo_location attributes. The ONE place that mapping lives.

No Home Assistant imports. An ALLOWLIST, as in Live Track Commuter Rail, so a
key added to a record somewhere else cannot reach the map by accident, and a
key missing here is visible in one place (06_MAP_CONTRACT.md: an integration
must not emit a name from the contract meaning something else).
"""

from __future__ import annotations

from typing import Any

from .const import MAP_LAYER

# Copied when present. Absent stays absent: never None, never a sentinel (D0).
PASSTHROUGH = (
    "train",
    "line_name",
    "observed_at",
    "last_seen",
    "previous_latitude",
    "previous_longitude",
    "previous_observed_at",
    "segment_duration_s",
    "course_deg",
    "icon_rotation_deg",
    "icon_rotation_basis",
    "position_jump",
    "stalled",
    "delay_min",
    # D4c: this railroad's own definition of late (operators/base.py).
    "late_threshold_min",
    "very_late_threshold_min",
    # D4c-status: a word in the delay badge's place ("Customs", border.py).
    "marker_status",
    "next_stop",
    "arrival_estimated_at",
    # D3: "estimated" when the position was moved along the train's route
    # from the source's fix, which then rides in fix_latitude/fix_longitude
    # (projection.py); "observed" when it is the fix.
    "position_source",
    "fix_latitude",
    "fix_longitude",
    # D3c-v route hint: the line from the last drawn position to this one.
    "track_path",
    # D2: the speed the SOURCE reported, in km/h. Only an adapter whose
    # source carries a real one sets it (Amtraker's Amtrak velocity is real,
    # 220 of 248 measured; its Brightline velocity is always zero, 05 B8.4).
    "speed_kmh",
    # D4 display helper: the source's own eight-point direction (05 B8.2).
    "heading_octant",
    "marker_color",
    "marker_label_color",
    "marker_label_outline_color",
    "marker_arrow_color",
    "marker_arrow_outline_color",
    "marker_ring_color",
    "marker_ring_width",
    # D4a: the marker's shape; "star" draws a star in the colours above.
    "marker_shape",
    # D4a-alternate: a second look the card fades to and back (the Maple
    # Leaf, Amtrak's star and VIA's badge; operators/amtrak.py).
    "marker_alternate",
)


def to_attributes(rec: dict[str, Any], operator_id: str) -> dict[str, Any]:
    """extra_state_attributes for one train.

    Never emitted, on purpose:
      heading_deg          no source here reports which way a train FACES (D2)
      max_extrapolation_s  Amtraker's Amtrak positions fail D3b condition 3
                           (median age 226 s; Live Track Amtrak SSOT 3.1).
                           An estimated position (position_source) is moved
                           along its route HERE; a consumer must not move it
                           again (D3: extrapolating an estimate)
      object_ids           a train or trip id is none of D11's keys
      z_index_offset       retired; map_layer replaces it (D10)
    """
    attrs: dict[str, Any] = {
        "identity": rec["vehicle_id"],
        "marker_label": rec["marker_label"],
        "in_service": rec["in_service"],
        "operator": operator_id,
        "map_layer": MAP_LAYER,
    }
    for key in PASSTHROUGH:
        value = rec.get(key)
        if value is not None:
            attrs[key] = value
    return attrs
