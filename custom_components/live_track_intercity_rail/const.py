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

DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 15
MAX_SCAN_INTERVAL = 600

USER_AGENT = (
    "LiveTrackIntercityRail/0.1.0 "
    "(+https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)"
)

# Ride out this many consecutive failed fetches by serving the last good
# result, so one network blip does not blank every marker. Live Track
# Commuter Rail's figure, carried over.
MAX_TRANSIENT_FAILURES = 2

# The shared map's layer name (06_MAP_CONTRACT.md D10). Every vehicle here is
# a train. The card owns the number.
MAP_LAYER = "rail"
