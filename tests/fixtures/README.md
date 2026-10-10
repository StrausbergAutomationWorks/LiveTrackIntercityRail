# Test fixtures

`amtraker_amtrak_20261009.json.gz`: Amtrak rows from Amtraker's `/v3/trains`,
21 polls 120 s apart on 2026-10-09 (08:22-09:02 UTC), trimmed to the fields
the adapter reads. One poll is the source's own outage: Amtraker answered
with no Amtrak train at all. Rebuilt with `bin\ltir_amtk_fixture.py` from the
raw capture, which stays on the maintainer's disk.

Data from [Amtraker](https://amtraker.com), licensed under the
[Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/).

`amtrak_geometry_20261009.json.gz`: Amtrak's GTFS static feed
(`https://content.amtrak.com/content/gtfs/GTFS.zip`, feed_version 20261009,
valid 2026-10-10 to 2026-10-16) distilled by `geometry.distill` (route lines
simplified to 15 m), then cut to the 11 train numbers and 187 station codes
the Amtraker fixture uses: 15 of the feed's 149 route lines. Rebuilt with
`bin\ltir_geo_fixture.py`. Source: Amtrak.

`brightline_rt_20261009.json.gz`: Brightline's own GTFS-Realtime
(`https://feed.gobrightline.com/position_updates.pb` and `trip_updates.pb`),
180 polls 60 s apart on 2026-10-09 (16:20-19:19 UTC), each the raw protobuf
file as served, base64: its positions file and the latest trip-updates file
at or before it. Taken from a capture polled every 30 s, one poll per minute
kept. Rebuilt with `bin\ltir_bl_fixture.py` from the raw capture, which stays
on the maintainer's disk.

`brightline_geometry_20261003.json.gz`: Brightline's GTFS static feed
(`https://feed.gobrightline.com/bl_gtfs.zip`, fetched 2026-10-03 16:18 UTC;
no `feed_info.txt`) distilled by `geometry.distill`, whole: 6 stops, 107
train numbers, 2 route lines. Rebuilt with `bin\ltir_bl_fixture.py`.
Source: Brightline. Brightline publishes no terms for these feeds.
