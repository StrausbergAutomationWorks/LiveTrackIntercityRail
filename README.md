# Live Track Intercity Rail

**Amtrak train data from [Amtraker](https://amtraker.com), licensed under the
[Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/).**

Live intercity passenger trains on your Home Assistant map. Pick the railroad
you want to watch; every train it reports appears as a `geo_location` entity
and moves as the railroad's data source updates. Add more railroads one at a
time.

This integration is not sponsored by, affiliated with, or operated by any of
the railroads it shows, or by Amtraker. It is original work, MIT-licensed.

## Status

**0.1.0**, the first release. It runs live on its development instance with
every railroad below.

## Requirements

- Home Assistant 2026.11 or later.
- A key of your own for NSW TrainLink (Transport for NSW), V/Line (Transport
  Victoria), NS, Arriva and Keolis (one NS key serves all three) and the
  Swedish railroads (one Trafikverket key serves all fifteen); where to get
  each is in the table below. The other railroads need none.
- Home Assistant installs the Python packages it needs (`saw-livetrack`,
  `gtfs-realtime-bindings` and `tzdata`) the first time the integration loads.

## Installation

### From the Marketplace

Live Track Intercity Rail is not in the Marketplace catalog yet. Add it by its
link:

1. Go to **Settings > Marketplace** and select **Add from link**.
2. Enter `StrausbergAutomationWorks/LiveTrackIntercityRail`. If asked for the
   type, choose **Integration**.
3. Install **Live Track Intercity Rail**.
4. Restart Home Assistant. The Marketplace offers the restart as a repair under
   **Settings > System > Repairs**.

The Marketplace then offers each new release as an update.

### By hand

1. Download the source code of the
   [latest release](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/releases/latest).
2. Copy its `custom_components/live_track_intercity_rail` folder into the
   `custom_components` folder of your Home Assistant configuration directory
   (create that folder if it is not there), so the path ends in
   `custom_components/live_track_intercity_rail/manifest.json`.
3. Restart Home Assistant.

To update by hand, replace the folder with the new release's and restart.

## Supported railroads

| Railroad | Area | Source | Key needed | Terms |
|---|---|---|---|---|
| Amtrak | United States, and its routes into Canada | [Amtraker](https://amtraker.com), a community API relaying Amtrak's own train tracking | No | ODC-By v1.0, attribution required: see [amtraker.com](https://amtraker.com) |
| Brightline | Florida | [Brightline's own GTFS and GTFS-Realtime](https://www.gobrightline.com) | No | None published |
| NSW TrainLink, regional trains | New South Wales, and its routes into Queensland, Victoria and the ACT | [Transport for NSW](https://opendata.transport.nsw.gov.au/) | Yes, your own, free | CC BY 4.0, Transport for NSW attributed: see [its data licence](https://opendata.transport.nsw.gov.au/datalicence) |
| Journey Beyond: The Ghan, the Ghan Expedition, Indian Pacific, Great Southern, The Overland | Adelaide to Darwin, Sydney to Perth, Adelaide to Brisbane, Adelaide to Melbourne | Journey Beyond's published timetables, transcribed into `data/journey_beyond_timetable.json` and shipped with the integration: no live positions exist, so every train is drawn from its timetable, and nothing is fetched | No | None published for the timetables; credited "Timetable: Journey Beyond (journeybeyondrail.com.au)". The file covers departures to 29 December 2027. Its route lines are built from [OpenStreetMap](https://www.openstreetmap.org/copyright) and shipped in `data/journey_beyond_lines.json.gz`: © OpenStreetMap contributors, ODbL 1.0 |
| Queensland Rail Travel: Spirit of Queensland, Spirit of the Outback, Tilt Train (Rockhampton and Bundaberg), Westlander, Inlander, Kuranda Scenic Railway, Gulflander | Queensland | [QRT's Service Updates page](https://www.queenslandrailtravel.com.au/serviceupdates): your Home Assistant reads the times that page shows, the list of today's trains at most every 5 minutes and each train out at most every 5 minutes. No live positions are published, so every train is drawn from its times | No | [Queensland Rail's copyright page](https://www.queenslandrailtravel.com.au/copyright); nothing of QRT's ships with the integration. Credited "Service updates: Queensland Rail Travel (queenslandrailtravel.com.au)". Its route lines are built from [OpenStreetMap](https://www.openstreetmap.org/copyright) and shipped in `data/qrt_lines.json.gz`: © OpenStreetMap contributors, ODbL 1.0 |
| WA Trains: the Australind, the Prospector, the MerredinLink and the AvonLink | Western Australia: Perth to Bunbury, Kalgoorlie, Merredin and Northam | The Public Transport Authority's published timetable, read from transperth.wa.gov.au. No live positions are published, so every train is drawn from its timetable, with no delay | No | [The Public Transport Authority's licence](https://www.transperth.wa.gov.au/About/Spatial-Data-Access) (not CC BY). Credited "Timetable data available free of charge from www.transperth.wa.gov.au" |
| V/Line, long-distance trains (its commuter lines are in Live Track Commuter Rail) | Victoria, and its route into New South Wales | [Transport Victoria](https://opendata.transport.vic.gov.au/) | Yes, your own, free | CC BY 4.0, Transport Victoria attributed: see [the dataset](https://discover.data.vic.gov.au/dataset/gtfs-realtime) |
| Renfe (Spain): AVE, Avlo, Alvia, Avant, Euromed, Intercity, MD, Regional | Spain, and its routes into France and Portugal | [Renfe's own GTFS-Realtime and timetable](https://data.renfe.com/) | No | CC BY 4.0, Renfe attributed. Its route lines are built from [OpenStreetMap](https://www.openstreetmap.org/copyright) and shipped in `data/renfe_spain_lines.json.gz`: © OpenStreetMap contributors, ODbL 1.0. End stations' municipalities and populations in `data/renfe_spain_ends.json`: municipalities from OpenStreetMap boundaries (© OpenStreetMap contributors, ODbL 1.0), populations from Wikidata property P1082 (CC0), else OpenStreetMap |
| Renfe Regionals (Catalunya): R11-R17 | Catalonia | [Renfe's own GTFS-Realtime](https://data.renfe.com/) | No | CC BY 4.0, Renfe attributed |
| VIA Rail | Canada | [VIA Rail's own train status and GTFS](https://www.viarail.ca/en/developer-resources) | No | Its GTFS: Open Government Licence - Canada 2.0 |
| VR | Finland | [Fintraffic Digitraffic](https://www.digitraffic.fi/en/) | No | CC BY 4.0, Fintraffic attributed |
| Vy: F, RE, RX and R lines | Norway, and its routes into Sweden | [Entur](https://developer.entur.org) | No | [NLOD 2.0](https://data.norge.no/nlod/en/2.0): "Contains data under the Norwegian licence for Open Government data (NLOD) distributed by Entur". End-station populations in `data/norway_ends.json`: Statistics Norway, table 04859, CC BY 4.0 |
| Go-Ahead Norge: F5 and R50 | Southern Norway | [Entur](https://developer.entur.org) | No | NLOD 2.0, as Vy |
| SJ Nord: F6, F7 and R60-R75 | Norway: Oslo to Trondheim (Dovrebanen), Trondheim to Bodø (Nordlandsbanen), and around Trondheim | [Entur](https://developer.entur.org)'s estimated timetable. SJ Nord publishes no positions, so every train is drawn from its expected times | No | NLOD 2.0, as Vy |
| Sweden: SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget, Värmlandstrafik, Tågab and Inlandsbanan, one entry each (SL Pendeltåg, Västtågen's pendeltåg and Arlanda Express are in Live Track Commuter Rail) | Sweden | [Trafikverket's open API](https://data.trafikverket.se) | Yes, your own, free: register at [data.trafikverket.se](https://data.trafikverket.se/oauth2/Account/register); one key serves every Swedish railroad | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/); credited "Data: Trafikverket (trafikverket.se), CC0". Sweden publishes no route shapes, so each station pair's line is built from [OpenStreetMap](https://www.openstreetmap.org/copyright) and shipped in `data/sweden_lines.json.gz`: © OpenStreetMap contributors, ODbL 1.0. End-city populations in `data/sweden_ends.json`: Statistics Sweden (SCB) and Trafikverket, both CC0 1.0 |
| Irish Rail: InterCity trains and the Enterprise (its commuter trains are in Live Track Commuter Rail) | Ireland, and Dublin to Belfast | [Irish Rail's realtime API](https://api.irishrail.ie/realtime/index.htm?realtime_irishrail) and the [National Transport Authority's timetable](https://www.transportforireland.ie/transitData/PT_Data.html). Irish Rail reports a train only as it passes signalling points, so every train is drawn from its timetable and its latest reported delay | No | Irish Rail publishes no terms; the timetable is CC BY 4.0, National Transport Authority. Credited "Data: Irish Rail (irishrail.ie); timetable: National Transport Authority, CC BY 4.0, provided as is" |
| NS (Intercity), and the regional trains of Arriva and Keolis (Arriva, RRReis, Blauwnet); NS's Sprinters are in Live Track Commuter Rail | The Netherlands | [NS's vehicle feed](https://apiportal.ns.nl/); timetable and delays from [OVapi](https://gtfs.ovapi.nl/) | Yes, your own, from the [NS API portal](https://apiportal.ns.nl/); one key serves all three | The NS API portal's terms; OVapi's timetable and delays CC0. Credited "Data: NS (apiportal.ns.nl); timetable and delays: OVapi (gtfs.ovapi.nl), CC0" |

Renfe's long-distance feed also carries Rodalies' regional trains (R11-R17). With both Renfe railroads set up,
Renfe (Spain) leaves those trains to Renfe Regionals (Catalunya), so each is drawn once.

Read each source's terms before you use its data; they bind you, as the
person receiving it. Amtraker's attribution travels with every entity this
integration creates, so it appears wherever a card shows entity attribution.

## Setup

Settings → Devices & services → Add integration → **Live Track Intercity
Rail**. Choose a region, then a railroad, and enter your key if it needs one. Options: the poll interval (default
30 s). The source is read once per interval however many Live Track
integrations that use Amtraker are installed.

## What appears

* **One `geo_location` entity per train**, named `<railroad> train <id>`. Its
  state is the distance from your home in km.
* `marker_label` is the **train number**.
* Each entity carries `observed_at` (when its position was true) where the
  source dates it and, between two observed positions, `previous_latitude`,
  `previous_longitude`, `previous_observed_at` and `segment_duration_s`, so a
  map card can move the marker between real fixes. Where the railroad's timetable gives a
  line, the train is moved along it between fixes and says so: `position_source: estimated`,
  with the fix beside it in `fix_latitude` and `fix_longitude`.
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

## Data sources

Every live source is read at runtime, by your Home Assistant; nothing from a
live feed is in this repository. The table above links each railroad's terms,
and each train credits its source in its `attribution` attribute. By
installing this integration you use these services, and their terms apply to
you. What the repository does ship, and the credit each file owes:

| File | What it holds | Source and licence |
|---|---|---|
| `data/journey_beyond_timetable.json` | Journey Beyond's departures to 29 December 2027, transcribed by hand from its published timetables and booking calendar (`tools/journey_beyond_source.json`) | Journey Beyond, no terms published. Credited "Timetable: Journey Beyond (journeybeyondrail.com.au)" |
| `data/journey_beyond_lines.json.gz`, `data/qrt_lines.json.gz`, `data/renfe_spain_lines.json.gz`, `data/sweden_lines.json.gz` | route lines, built by `tools/journey_beyond.py`, `tools/qrt_lines.py`, `tools/renfe_spain_lines.py` and `tools/sweden_lines.py` | © OpenStreetMap contributors. Derived from [OpenStreetMap](https://www.openstreetmap.org/copyright) and offered under the [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/) |
| `data/renfe_spain_ends.json` | the municipality and population of each end station of Renfe's long-distance trips | municipalities: OpenStreetMap boundaries, © OpenStreetMap contributors, ODbL 1.0; populations: Wikidata property P1082, CC0, else OpenStreetMap |
| `data/sweden_ends.json` | the population of each Swedish trip's end city | Statistics Sweden (SCB), Statistiska tätorter 2023, CC0 1.0; Trafikverket's stations, CC0 1.0 |
| `data/norway_ends.json` | the population of each Norwegian trip's end city | Statistics Norway, table 04859, CC BY 4.0 |

## Licence

Code: MIT, see `LICENSE`. The files in `data/` keep their sources' licences,
listed above, and the bundled map card in `frontend/` its own (see
[LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)).

## Acknowledgement

StrausbergAutomationWorks pays its respect to Elders past and present and acknowledges the contributions of First Nations (Aboriginal and Torres Strait Islander) peoples.
