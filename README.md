# Live Track Intercity Rail

**Amtrak train data from [Amtraker](https://amtraker.com), licensed under the
[Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/).**

Live intercity passenger trains on your Home Assistant map. Pick the railroad
you want to watch; every train it reports appears as a `geo_location` entity
and moves as the railroad's data source updates. Add more railroads one at a
time.

This integration is not sponsored by, affiliated with, or operated by any of
the railroads it shows, or by Amtraker. It is original work, MIT-licensed.

## Supported railroads

| Railroad | Area | Source | Key needed | Terms |
|---|---|---|---|---|
| Amtrak | United States, and its routes into Canada | [Amtraker](https://amtraker.com), a community API relaying Amtrak's own train tracking | No | ODC-By v1.0, attribution required: see [amtraker.com](https://amtraker.com) |

Read each source's terms before you use its data; they bind you, as the
person receiving it. Amtraker's attribution travels with every entity this
integration creates, so it appears wherever a card shows entity attribution.

## Setup

Settings → Devices & services → Add integration → **Live Track Intercity
Rail**. Choose a region, then a railroad. Options: the poll interval (default
30 s). The source is read once per interval however many Live Track
integrations that use Amtraker are installed.

## What appears

* **One `geo_location` entity per train**, named `<railroad> train <id>`. Its
  state is the distance from your home in km.
* `marker_label` is the **train number**.
* Each entity carries `observed_at` (when its position was true) where the
  source dates it and, between two observed positions, `previous_latitude`,
  `previous_longitude`, `previous_observed_at` and `segment_duration_s`, so a
  map card can move the marker between real fixes. Nothing is extrapolated.
* `course_deg` while the train moves, from two observed positions; at rest it
  is left out, and `icon_rotation_deg` with `icon_rotation_basis: held` keeps
  the last direction for the marker's arrow.
* `next_stop` and `arrival_estimated_at` (ISO 8601 UTC), `delay_min` at the
  next stop, `line_name` (the route's name) and `speed_kmh` (as reported) when
  the source carries them; absent otherwise.
* One count sensor per railroad: **Trains in service**.

## Map card

Trains are drawn by [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
(`custom:live-track-map-card`), the one map every Live Track integration
renders on. It shows each railroad's colours and pictures, labels a train with
its `marker_label`, and slides it between real fixes along the track.

**The card is installed with the integration.** This integration carries a
released copy of the card, serves it, and registers it as a dashboard resource
when Home Assistant starts; there is nothing to download or copy into `www`.
Every Live Track integration does the same, and they keep exactly one resource
row between them: the highest card version any of them carries, never a
downgrade. A card you installed through HACS is left alone. Removing the last
railroad of this integration hands the row to another Live Track integration,
or removes it if none is left. See the card's README, section
[Live Track](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).

If your dashboards' resources are set in YAML (`lovelace: resource_mode: yaml`),
nothing can be registered for you. A Repairs issue then gives the exact line to
add; it looks like this, with the integration's own address in place of the
placeholders:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_intercity_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

If the integration's files are removed (through HACS, say) while its railroads
are still set up, and no other Live Track integration is installed, nothing is
left to tidy the row: remove it in Settings > Dashboards > Resources. To
install the card by hand instead, follow the card's README; the resource row
of a hand-installed copy under `/local/` is pointed at an integration's copy
only when that copy is a newer release.

Give it the trains with
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities),
filtering on `domain: geo_location` and
`attributes: {source: live_track_intercity_rail}`.

Any other map card that shows `geo_location` entities shows the trains too,
as plain markers.
