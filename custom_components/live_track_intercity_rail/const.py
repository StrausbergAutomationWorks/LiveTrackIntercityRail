"""Constants for Live Track Intercity Rail. No Home Assistant imports."""

# ! PERMANENT from the first install (05_SHARED_LESSONS.md A1). Confirmed by
# Lee 2026-10-03 (SSOT section 1).
DOMAIN = "live_track_intercity_rail"

# Config entry keys. One config entry per railroad; the entry's unique_id is
# the operator id, so the same railroad cannot be added twice and no two
# entries ever publish the same train (06_MAP_CONTRACT.md D1).
CONF_OPERATOR = "operator"
CONF_REGION = "region"
CONF_SCAN_INTERVAL = "scan_interval"
# A user's own key, for a source that wants one (Operator.needs_key). Redacted from
# diagnostics.
CONF_API_KEY = "api_key"

DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 15
MAX_SCAN_INTERVAL = 600

USER_AGENT = (
    "LiveTrackIntercityRail/0.1.1 "
    "(+https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)"
)

# How long a failed source is ridden out on its last good answer before the
# trains go unavailable (and the dashboard, which excludes unavailable
# entities, drops them). It was 2 failed polls (Commuter Rail's figure): on
# 2026-10-09 17:19:14 CDT Amtraker failed 3 polls running and every Amtrak
# marker vanished for 31 s (Lee: "All of the icons just disappeared"). Ten
# minutes is a choice: trains keep moving along their lines meanwhile
# (sources/base.py hold_last), and every one still carries its fix's
# observed_at, so a stale answer reads as stale.
SOURCE_GAP_S = 600

# The shared map's layer name (06_MAP_CONTRACT.md D10). Every vehicle here is
# a train. The card owns the number.
MAP_LAYER = "rail"
