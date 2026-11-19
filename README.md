# Live Track Intercity Rail

**English** · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · [Gaeilge](README.ga.md) · [All languages](#languages)

**Intercity trains for Home Assistant, on one map.** Live Track Intercity
Rail puts every train of the intercity and long-distance railroads you choose
on your Home Assistant map: where it is, its number, whether it is late by the
railroad's own rule, and its next stop. Each railroad is added on its own,
from its own published data.

> **Live Track Intercity Rail is one module of Live Track**, a family of Home
> Assistant integrations that draw everything that moves, and the weather it
> moves through, on one shared map: aircraft, ships, trains and weather.
> Install it on its own, or beside the other modules
> ([list below](#part-of-live-track-the-other-modules)).

> **Growing, and open to ideas.** Live Track Intercity Rail covers 33
> railroads in 9 countries on 3 continents today, and we are adding more
> railroads and countries. Is yours missing? [Suggest it](#help-it-grow), or
> add it yourself: we will help you do it.

**Status: 0.1.0, the first release.** Added to the Marketplace by link
([below](#install-it-step-by-step)); it is not in the Marketplace's catalog
yet.

Original work by StrausbergAutomationWorks. Not affiliated with, or endorsed
by, Amtrak, Amtraker, Brightline, VIA Rail, Fintraffic, VR, Transport for NSW,
NSW TrainLink, Transport Victoria, V/Line, Queensland Rail, Journey Beyond,
the Public Transport Authority of Western Australia, Transwa, Renfe, Rodalies
de Catalunya, Entur, Vy, Go-Ahead Norge, SJ Nord, Trafikverket, SJ, VR
Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen,
Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget,
Värmlandstrafik, Tågab, Inlandsbanan, Irish Rail, the National Transport
Authority (Ireland), NS, Arriva, Keolis, OVapi, or any other railroad.

---

## Contents

1. [Everything it does](#everything-it-does)
2. [Where it works](#where-it-works)
3. [Part of Live Track: the other modules](#part-of-live-track-the-other-modules)
4. [Before you start](#before-you-start)
5. [Install it, step by step](#install-it-step-by-step)
6. [Set it up, step by step](#set-it-up-step-by-step)
7. [Free keys that switch on more, step by step](#free-keys-that-switch-on-more-step-by-step)
8. [Put the map on a dashboard](#put-the-map-on-a-dashboard)
9. [Use it in automations](#use-it-in-automations)
10. [Everything on the map, in detail](#everything-on-the-map-in-detail)
11. [All the entities it creates](#all-the-entities-it-creates)
12. [What it sends and downloads](#what-it-sends-and-downloads)
13. [Help it grow](#help-it-grow)
14. [Languages](#languages)
15. [Credits and licences](#credits-and-licences)
16. [Keywords](#keywords)

---

## Everything it does

### On the map, with nothing to set up

You add a **railroad**: you choose a country, then one of its intercity
railroads. Everything below then appears for that railroad. Add the
integration again for each other railroad you want.

| What | Where | From |
|---|---|---|
| **Trains in service**: one marker per train, labelled with its train number or its line, in the railroad's own colours, turned to the direction it runs | every railroad | each railroad's own published data |
| **Lateness**: a train shows as late or very late by the railroad's own rule; where a railroad publishes no rule, by how far the train runs | every railroad that reports delays | each railroad's own feed |
| **Next stop and its time**: the station a train calls at next, and when it is expected there | every railroad whose feed or timetable says so | each railroad's own feed and timetable |
| **Trains that follow the tracks**: between two reports a train moves along its own line at its last speed, not straight across | every railroad whose line is known | each railroad's timetable, or lines shipped with the integration |
| **Trains from the timetable**: where a railroad publishes no positions, each train is placed on its line by its times, and marked as an estimate | Journey Beyond, Queensland Rail Travel and WA Trains (Australia), SJ Nord (Norway); Irish Rail with its latest delay | each railroad's timetable or times |
| **Pictures for some trains**: the Santa Claus Express and a summer cottage (Finland), the animals of Journey Beyond's trains, a picture for each Queensland Rail Travel line | Finland, Australia | drawn for this integration |
| **Stopped at the border**: a train standing at a United States and Canada border crossing shows "Customs" in place of its delay | Amtrak trains to and from Canada | Amtrak's positions |
| **One count per railroad**: trains in service | every railroad | the same data |

### Switched on by your own free key or account

| Free key or account | What it adds |
|---|---|
| **Transport for NSW Open Data** key | NSW TrainLink's regional trains (New South Wales, Australia) |
| **Transport Victoria Open Data** key | V/Line's long-distance trains (Victoria, Australia) |
| **NS API portal** key | NS Intercity, Arriva's and Keolis's regional trains (the Netherlands); one key serves all three |
| **Trafikverket** key | the 15 Swedish railroads; one key serves all fifteen |

Each takes a few minutes to get: [step by step below](#free-keys-that-switch-on-more-step-by-step).
The other 13 railroads need no key.

---

## Where it works

| Region | What you get | From | Needs |
|---|---|---|---|
| **Australia**: across the country | Journey Beyond: The Ghan, The Ghan Expedition, Indian Pacific, Great Southern, The Overland, from the timetable only ([why](#journey-beyond-australia)) | Journey Beyond | nothing |
| **Australia**: New South Wales | NSW TrainLink's regional trains (XPT and Xplorer), also into Queensland, Victoria and the Australian Capital Territory | Transport for NSW | a free key |
| **Australia**: Queensland | Queensland Rail Travel: Spirit of Queensland, Spirit of the Outback, Tilt Train, Westlander, Inlander, Kuranda Scenic Railway, Gulflander, from their published times ([why](#queensland-rail-travel-australia)) | Queensland Rail Travel | nothing |
| **Australia**: Victoria | V/Line's long-distance trains (its commuter lines are in Live Track Commuter Rail), also into New South Wales | Transport Victoria | a free key |
| **Australia**: Western Australia | WA Trains: the Australind, the Prospector, the MerredinLink and the AvonLink, from the timetable only ([why](#wa-trains-western-australia-australia)) | Public Transport Authority of Western Australia | nothing |
| **Europe**: Finland | VR's long-distance trains | Fintraffic Digitraffic | nothing |
| **Europe**: Ireland | Irish Rail's InterCity trains, and the Enterprise from Dublin to Belfast (United Kingdom) | Irish Rail, National Transport Authority | nothing |
| **Europe**: Netherlands | NS Intercity, and the regional trains of Arriva (Arriva, RRReis, Blauwnet) and Keolis (Blauwnet, RRReis); NS's Sprinters are in Live Track Commuter Rail | NS, OVapi | a free key |
| **Europe**: Norway | Vy's F, RE, RX and R lines (F1 also into Sweden), Go-Ahead Norge's F5 and R50, SJ Nord's F6, F7 and R60 to R75 | Entur | nothing |
| **Europe**: Spain | Renfe's AVE, Avlo, Alvia, Avant, Euromed, Intercity, MD and Regional trains, also into France and Portugal; Rodalies de Catalunya's regional lines R11 to R17 | Renfe | nothing |
| **Europe**: Sweden | SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget, Värmlandstrafik, Tågab and Inlandsbanan, one railroad each | Trafikverket | a free key |
| **North America**: Canada | VIA Rail, every route | VIA Rail | nothing |
| **North America**: United States | Amtrak, every route, also into Canada | Amtraker | nothing |
| **North America**: United States | Brightline (Florida) | Brightline | nothing |

Not on the list? [Tell us](#help-it-grow). Where someone publishes the data
openly, we will look at adding it.

⚠ **A train is only as good as its railroad's data.** Some railroads report a
train every few seconds, some every few minutes, some only as it passes
signals, and some publish no positions at all. Each railroad's limits are
under [Everything on the map, in detail](#everything-on-the-map-in-detail).

⚠ **It is not the railroad's official information.** Before you travel, check
the railroad's own app or website.

---

## Part of Live Track: the other modules

Live Track is a set of Home Assistant integrations, one per kind of moving
thing, all drawn on the same map card. Each works on its own; together they
make one live picture. They share the map card and a Python library
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
so installing another one adds no requests to a source another already reads.

| Module | What it puts on the map | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aircraft overhead from ADS-B, with routes and type icons | released |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | ships and boats from AIS, near you or anywhere | released |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | commuter trains in North America, Europe and Australia | released |
| **Live Track Intercity Rail** | intercity and long-distance trains in North America, Europe and Australia (this module) | released |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | immigration and federal law-enforcement aircraft and vessels, from public lists | released |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | weather, storms and natural hazards | released |
| Live Track Stations | departure boards and "time to leave" alerts for every station | planned |
| Live Track Satellites | satellites passing overhead | planned |
| Live Track Freight Trains | freight and work trains where railways publish them | planned |
| Live Track Transit | city buses, trams, ferries and metro | planned |
| Live Track Intercity Buses | intercity and regional coaches | planned |
| Live Track Commuter Buses | commuter buses | planned |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | the shared map card every module draws on | released, installed with each module |

Everything is free and open source. Nothing is held back for sponsors.

---

## Before you start

* **Home Assistant** 2026.11 or later.
* **The Marketplace** (HACS) in your Home Assistant, to install and update it
  the easy way. Without it you can copy the files by hand.
* **Internet access** for Home Assistant: every train comes from its
  railroad's own published data.
* **Optional: auto-entities** from the Marketplace, to put the markers on the
  map (see [Put the map on a dashboard](#put-the-map-on-a-dashboard)).
* Nothing to pay. 13 of the 33 railroads need no account; the other 20 need a
  free key of your own, and four keys cover all of them
  ([above](#switched-on-by-your-own-free-key-or-account)).
* Home Assistant installs the Python packages it needs (`saw-livetrack`,
  `gtfs-realtime-bindings` and `tzdata`) by itself the first time the
  integration loads.

---

## Install it, step by step

### From the Marketplace (recommended)

Live Track Intercity Rail is not in the Marketplace's catalog yet. Add it by
its link:

1. In Home Assistant, open **Settings → Marketplace** (HACS).
2. Choose **Add from link** (or the three-dot menu → **Custom repositories**).
3. Enter `StrausbergAutomationWorks/LiveTrackIntercityRail`. If asked for the
   type, choose **Integration**.
4. Find **Live Track Intercity Rail** in the list and choose **Download** or
   **Install**.
5. **Restart Home Assistant**: **Settings → System → Repairs** offers the
   restart, or use **Settings → System → Restart**.

The Marketplace then offers each new release as an update.

### By hand

1. Download the source code of the
   [latest release](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/releases/latest).
2. Copy its `custom_components/live_track_intercity_rail` folder into the
   `custom_components` folder of your Home Assistant configuration folder
   (create `custom_components` if it is not there).
3. Restart Home Assistant.

To update by hand, replace the folder with the new release's and restart.

---

## Set it up, step by step

1. Open **Settings → Devices & services**.
2. Choose **Add integration** (bottom right) and search for **Live Track
   Intercity Rail**.
3. **Region**: choose the country of the railroad. Only countries with at
   least one railroad are listed. Choose **Submit**.
4. **Railroad**: choose the railroad. Choose **Submit**.
5. **API key**: only for NSW TrainLink, V/Line, the three Dutch railroads and
   the fifteen Swedish railroads. Paste your key
   ([how to get one](#free-keys-that-switch-on-more-step-by-step)) and choose
   **Submit**. The other railroads skip this step.

That is all. The trains appear within a minute or two. Where a railroad's
lines come from its timetable, the trains start to follow their lines once
the timetable has downloaded, which can take a few minutes the first time. To
watch another railroad, add the integration again. The same railroad twice
is refused.

### Change what it shows: the options

Open **Settings → Devices & services → Live Track Intercity Rail →
Configure** (the cog) on the railroad you want to change. There is one
option:

| Option | What it does | Default |
|---|---|---|
| **Poll interval** | how often the railroad's source is read, 15 to 600 seconds. A shorter interval than the source's own refresh shows nothing more | set by railroad: 15 seconds for Renfe (Spain) and the three Dutch railroads; 60 seconds for Brightline, NSW TrainLink, Irish Rail and SJ Nord; 30 seconds for the others |

---

## Free keys that switch on more, step by step

Twenty railroads ask each user for their own key, from four providers. Every
one of these keys is free, and each person who installs Live Track Intercity
Rail gets their own. You paste the key when the setup dialog asks for it
([step 5 above](#set-it-up-step-by-step)). Only the key is asked for: no
password and no secret. The key is stored in Home Assistant with the
integration, sent only to its own provider, and never written to the log. If
the provider refuses it for ten minutes, Home Assistant asks you for a new
one.

### Transport for NSW (NSW TrainLink, New South Wales, Australia)

1. Open <https://opendata.transport.nsw.gov.au/>, choose **Register**, create
   an account, and log in.
2. Choose your user profile icon, then **API Tokens**.
3. Type a name for the key and choose **CREATE API TOKEN**. Copy the key at
   once: the site shows it only once.
4. Paste it into **API key** when you add NSW TrainLink. Paste the key alone:
   Live Track Intercity Rail adds the word `apikey` itself.

### Transport Victoria (V/Line, Victoria, Australia)

1. Open <https://opendata.transport.vic.gov.au/>, choose **Login**, then
   **Sign up**.
2. Enter your details and choose **Create Account**. Enter the code from the
   email you receive and choose **Confirm**.
3. The portal asks for an authenticator app on your phone: scan the QR code
   with it, enter the app's code and choose **Confirm**. Then sign in with
   your email, your password and the app's code.
4. Choose **My Account** → **Profile** → **API tokens**. Your key is already
   there. Paste it into **API key** when you add V/Line.

### NS (NS, Arriva and Keolis, the Netherlands)

1. Open <https://apiportal.ns.nl/>, choose **Inloggen** (sign in), then
   **Externe bezoeker** (external visitor).
2. Fill in the form and send it. An email confirms the registration. The APIs
   can take up to 5 minutes to appear in the portal.
3. Open the page of the **Virtual Train API** (NS's train positions). Under
   **Related Products**, open its product, give your subscription a name, and
   choose **Subscribe**.
4. When NS has approved the subscription, your key is on your profile page.
   Paste it into **API key** when you add NS, Arriva or Keolis. One key serves
   all three.

### Trafikverket (the 15 Swedish railroads)

1. Open <https://data.trafikverket.se/oauth2/Account/register>.
2. Fill in **Email**, **Displayname**, **Password** and **Confirm password**,
   tick **Accept license and Agreement**, and choose **Register**.
3. Open <https://data.trafikverket.se/get-started> and choose **Create key**,
   under **Create a key**. Sign in with the account you made, and create the
   key.
4. Paste it into **API key** when you add a Swedish railroad. One key serves
   all fifteen.

---

## Put the map on a dashboard

The map is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
the card every Live Track module draws on. **It is installed with Live Track
Intercity Rail**: nothing to download, nothing to copy, no resource to add.

1. Open a dashboard, choose the pencil (**Edit dashboard**), then **Add card**.
2. Scroll to the bottom and choose **Manual**.
3. Paste this, and choose **Save**:

```yaml
type: custom:auto-entities
card:
  type: custom:live-track-map-card
filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_intercity_rail
      options:
        display: attribute
        attribute: marker_label
        position_transition: auto
  exclude:
    - state: unavailable
```

The markers need [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
from the Marketplace. With other Live Track modules installed, add one more
`- domain: geo_location` filter for each of their sources
(`live_track_commuter_rail`, `live_track_aircraft` and so on).

**On the map:**

* Each train is a marker in its railroad's colours, labelled with its train
  number or line. Amtrak's trains are stars, VIA Rail's carry the maple leaf,
  Irish Rail's InterCity trains are shamrocks, and some trains are pictures
  (each railroad below says which).
* On most railroads the colours swap with the direction: one way leaving the
  main city, the other way toward it.
* An arrow shows the direction the train runs. A train standing still keeps
  its last direction. Pictures stay upright and have no arrow.
* **Point at** a train to see its railroad, number, line and where it runs.
  **Click** it for all its details, its next stop and its delay included.

If your dashboards' resources are set in YAML (`lovelace: resource_mode: yaml`),
nothing can be registered for you: a **Repairs** issue then gives the exact
lines to add to `configuration.yaml`. They look like this, with the
integration's own address in place of the placeholders:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_intercity_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Every Live Track module carries a copy of the card and registers it when Home
Assistant starts. Together they keep exactly one row in **Settings →
Dashboards → Resources**: the newest card version any of them carries, never
an older one. A card you installed yourself through the Marketplace is left
alone. When you remove this module's last railroad, the row passes to another
Live Track module, or is removed if none is left. If the integration's files
are removed while its railroads are still set up, and no other Live Track
module is installed, remove the row yourself in **Settings → Dashboards →
Resources**.

**To install the card by hand instead**, follow the steps in the
[card's README](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
A row you made yourself for a copy under `/local/` is pointed at this
module's copy only when this module's copy is a newer release.

Any other map card that shows `geo_location` entities shows the trains too,
as plain markers.

---

## Use it in automations

Everything is an ordinary Home Assistant entity, so the automation editor
works with it, no code needed.

**A phone notification when your railroad's data stops** (the trains then
leave the map):

1. **Settings → Automations & scenes → Create automation → Create new
   automation**.
2. **When**: **Add trigger** → **Entity** → **State changed**. Choose the
   railroad's **Trains in service** entity, and under **To (optional)** choose
   **Unavailable**.
3. **Then do**: **Add action**, search for your phone's notification action
   (it carries your phone's name), and enter a message, for example:

   ```text
   No intercity trains on the map: the railroad's data has stopped
   ```

4. **Save**.

**Other ideas:** a light that turns on when an Amtrak train is within 2 km
(1.2 miles) of your home in the United States, from the markers' distance; a
dashboard count of the trains VR runs in Finland through the day; a message
when Queensland Rail Travel's first train of the day sets out (Australia),
from **Trains in service** rising above 0.

---

## Everything on the map, in detail

### Trains

Each train is one marker. Its state is its distance from your home, in
kilometres. The marker appears when the railroad reports the train, or when
its timetable says it is running, and is removed when the train leaves the
railroad's data or its run is over.

* **Between two reports** a train moves along its own line toward its next
  stop: at the speed the railroad reports, or, where it reports none, at the
  speed between its last two reports. It never passes its next stop, and
  stops moving 30 minutes after the last report. A train on a known line is
  drawn on the line; the railroad's own report is kept beside it.
* **If a railroad's data fails**, its trains keep moving on their last good
  report for up to 10 minutes. After that they are unavailable and leave the
  map until the data comes back.
* **Late and very late**: where the railroad publishes its own rule for a
  late train, the integration uses it. Where it publishes none, a train is
  late by how far it runs, using the thresholds of Amtrak Status Maps
  (asm.transitdocs.com). Each railroad below says which.

On each train: `marker_label`, `train`, `line_name`, `observed_at` (when its
report was true), `course_deg` (while it moves), `next_stop` and
`arrival_estimated_at` (where known), `delay_min`, `late_threshold_min` and
`very_late_threshold_min`, `speed_kmh` (where the railroad reports it),
`attribution`, and, between two reports, `previous_latitude`,
`previous_longitude`, `previous_observed_at` and `segment_duration_s`. A
train moved along its line carries `position_source: estimated`, with the
railroad's report in `fix_latitude` and `fix_longitude`.

### Journey Beyond (Australia)

⚠ **Journey Beyond publishes no positions.** Every train is drawn from its
published timetable, transcribed into a file that ships with the integration
(departures to 29 December 2027), so nothing is downloaded. Each train is
placed on its line by its times, marked as an estimate, with no delay: a
late or cancelled train is still drawn on time. Each service is its own
picture (the camel and rider, a bird, a kangaroo, an emu), in its colours
going out and swapped coming back, with no label: point at it to see the
train and its run.

### NSW TrainLink (New South Wales, Australia)

From Transport for NSW's NSW TrainLink feed, with your own key, a new
position about once a minute. The label is the train number. NSW orange with
a white ring leaving Sydney, swapped going to it. The feed has no speed, so a
train moves along its line at the speed between its last two positions. Late
from 11 minutes (NSW TrainLink counts a train on time within 10 minutes),
very late from 30.

### Queensland Rail Travel (Australia)

⚠ **Queensland Rail Travel publishes no positions.** Your Home Assistant reads
the times that Queensland Rail Travel's Service Updates page shows: the list
of today's trains at most every 5 minutes, and each train's times at most
every 5 minutes from 30 minutes before it leaves until 15 minutes after it
arrives. Each train is placed on its line by those times and marked as an
estimate. Each line is its own picture, in its colours leaving Brisbane and
swapped going to it, with the train number in a tag beside it. No late or very
late is shown.

### V/Line (Victoria, Australia)

From Transport Victoria's V/Line feed, with your own key: the long-distance
lines to Albury, Ararat, Bairnsdale, Echuca, Maryborough, Shepparton, Swan
Hill and Warrnambool. The label is the train number. V/Line purple with a
yellow ring leaving Melbourne, swapped going to it. The feed has no speed, so
a train moves at the speed between its last two positions; after 10 minutes
with no new position it is timed to its next stop. Late from 11 minutes on
the long lines and 6 on the short ones (V/Line's own list), very late from
30.

### WA Trains (Western Australia, Australia)

⚠ **No live positions are published.** Every train is drawn from the timetable
of the Public Transport Authority of Western Australia: placed along its line
by its scheduled times, marked as an estimate, with no delay. The timetable
is checked once a day. The label is the route's first three letters: AUS
(Australind, purple), PRO (Prospector, orange), MER (MerredinLink, green) and
AVO (AvonLink, green), the same both ways.

### VR (Finland)

From Fintraffic's Digitraffic, a new position about every 30 seconds. The
label is the train type and number, as VR writes it (`IC 23`). VR green with a
dark ring leaving Helsinki, swapped going to it. The data has no direction,
so the arrow follows the line. Late from 6 minutes (VR counts a train late
when it is more than five minutes late), very late from 12.

* **The Santa Claus Express**, from the first Sunday of Advent to 6 January:
  a snowman going north, a reindeer coming back, with no number. From 12
  minutes late the figure turns round every few seconds.
* **The summer cottage**, from Midsummer Eve to 31 July: every VR
  long-distance train is drawn as a cottage, with its number beside it.

### Irish Rail (Ireland)

From Irish Rail's live service and the National Transport Authority's
timetable. ⚠ Irish Rail reports a train only as it passes signalling points a
few minutes apart, so each train is drawn from its timetable and its latest
delay, moved along its route. The label is the train number without its
letter (A700 shows 700). An InterCity train is a green shamrock with an orange
outline and number leaving Dublin, the colours swapped going to it. The
Enterprise is a silver disc with a red outer ring, a magenta band and a
magenta number; going to Dublin the disc is magenta. Late from 10 minutes
(the National Transport Authority's rule), very late from 20.

### NS, Arriva and Keolis (the Netherlands)

From NS's vehicle data, with your own key, a new position about every 10
seconds. This feed reports a train's own speed and direction, and both are
passed on. The next stop and the delay come from OVapi's timetable; the track
is NS's own map of its lines, downloaded once a day. The label is the train
number. NS's trains are yellow with an NS blue ring; Arriva's and Keolis's
trains have the map card's own look for now. Late from 3 minutes (NS's own
definition), very late from 10.

### Vy, Go-Ahead Norge and SJ Nord (Norway)

From Entur, each railroad its own entry. The label is the line code (F4,
RE10, R50). The line's own colour with a white ring leaving Oslo S (on a trip
that does not reach Oslo S, its larger end city), swapped going to it. Entur
publishes no speed and no direction, so a train moves at the speed between
its last two positions, and the arrow follows its line. In Oslo's long
tunnels a train whose positions stop is moved along its line until they come
back. ⚠ **SJ Nord publishes no positions:** each of its trains is placed on its
line by its expected times. Late from 4 minutes, and from 6 on the F lines
and the lines to Göteborg (Sweden), the rule of Bane NOR and Vy; very late
at twice that.

### Renfe (Spain) and Renfe Regionals (Catalunya, Spain)

**Renfe (Spain)** reads Renfe's long-distance feed, a new position about every
15 seconds. The label is the train number; the service (AVE, Avlo, Alvia and
so on) is in the hover box. AVE navy, Avlo turquoise, every other service
Renfe purple, each filled leaving Madrid (on a trip that does not reach
Madrid, its larger end city) and swapped going to it. Renfe publishes no
route lines, so the lines are built from OpenStreetMap and shipped with the
integration. Renfe publishes no rule for a late train, so a train is late by
the length of its trip: from 10 minutes up to 400 km (250 miles), 15 up to
560 km (350 miles), 20 up to 725 km (450 miles), 25 up to 885 km (550
miles), 30 beyond; very late at twice that.

**Renfe Regionals (Catalunya)** draws Rodalies de Catalunya's regional lines
R11 to R17. The label is the train number, in the line's own colour, filled
leaving Barcelona and swapped going to it. Outside Barcelona a position is
the last station a train passed, so the train is timed between stations by
the timetable and its delay. Late from 10 minutes, very late from 20, by the
length of the longest line. With both Renfe railroads set up, each train is
drawn once.

### The Swedish railroads (Sweden)

From Trafikverket, with your own key (one key for all fifteen). The label is
the train number on the ticket; the brand, number and end stations are in the
hover box. Each brand has its own colours, swapped going to Stockholm C (on a
trip that does not reach Stockholm C, its larger end city). Trafikverket gives
a speed on about half its positions; the other trains move at the speed
between their last two positions. Sweden publishes no route lines, so the
lines are built from OpenStreetMap and shipped with the integration. Late
from 6 minutes (Trafikverket counts a train on time to 5 minutes 59
seconds), very late from 12.

### VIA Rail (Canada)

From VIA Rail's own train-status data. Each train is a disc with the maple
leaf and a band in its route group's colour (Atlantic, Western, Ontario and
Quebec, Prince Rupert, Churchill, Sudbury to White River, Montréal scenic),
with the train number in an upright tag. Odd numbers have a yellow disc, even
numbers a disc in the band's colour. A train with no new position moves
toward its next stop to arrive at VIA's own estimate. VIA publishes no rule
for a late train, so a train is late from 10 minutes on the Québec City to
Windsor corridor and from 60 elsewhere (Amtrak Status Maps' values for VIA),
very late at twice that.

### Amtrak (United States)

Amtrak publishes no open live data. Amtraker relays Amtrak's own train
tracking, with a new position every 3 to 5 minutes, and the integration moves
each train along its line at the speed Amtrak reports. Each train is a star
with its number across it, in its route's colours (the Northeast routes,
Cascades, Pacific Surfliner, Acela and more), else the flag star. The Maple
Leaf (New York to Toronto) changes slowly between Amtrak's star and VIA's
badge. A train standing at the border at Lacolle, Rouses Point or Niagara
Falls shows "Customs" in place of its delay. Late from 16 minutes (Amtrak
counts a train on time within 15 minutes), very late from 30. The same train
number can run on two or three days at once, so each run is its own marker.

### Brightline (United States)

From Brightline's own feed, a new position about every 60 seconds. The label
is the trip number, in black outlined white, on a disc in the colour of the
train's destination, with a black ring. A position more than 5 minutes old is
not used. The feed has no speed, so a train moves at the speed between its
last two positions. Brightline publishes no rule for a late train, so a train
is late from 10 minutes, very late from 20, by the length of its trip.

---

## All the entities it creates

For each railroad:

| Entity | What it is |
|---|---|
| `sensor.<railroad>_trains_in_service` | **Trains in service**: how many trains the railroad is running on the map now. For Amtrak: `sensor.amtrak_trains_in_service` |
| `geo_location.<railroad>_train_…` | one per train (`geo_location.amtrak_train_5_17`); it comes and goes with the train. Each carries `source: live_track_intercity_rail`, and its state is its distance from your home in kilometres |

A marker's entity ID comes from the railroad and the run, never from its
label: `geo_location.amtrak_train_5_17` is Amtrak's train 5 that set out on
the 17th of the month, so a train keeps the same entity ID for its whole run,
and another run of the same number gets its own. The marker is removed when
the run leaves the railroad's data or ends. The markers have no unique ID, as
no Live Track map marker has, so they cannot be renamed, hidden or given an
area in the interface. The sensor has a unique ID and can be renamed.

Attributes that change at every poll, the markers' positions and times, are
recorded in Home Assistant's history, as for any entity. The sensor has no
attributes, so it costs little to keep, and it is the record of how many
trains ran on a day. To keep the markers out of history, add this to
`configuration.yaml`, then restart:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_train_*
```

If your `configuration.yaml` already has a `recorder:` section, add only the
pattern `geo_location.*_train_*` to it, under `exclude:` and `entity_globs:`.
The pattern matches this module's train markers only. A map card set to draw
history then has no trail to draw.

---

## What it sends and downloads

**About your location.** Nothing. Your home's position is used only inside
your Home Assistant, to give each train's distance. Your key, where a railroad
needs one, is sent only to that railroad's provider. Nothing else about you is
sent anywhere. Each service sees your internet address, as any website does.

**How much.** Each live source is read at each poll, at the railroad's own
interval by default (**Poll interval**, 15 to 600 seconds), or less often
where the table says so. Where several Live Track modules or railroads read
the same source, one shared client reads it once for all of them. Measured on
19 November 2026, 02:44 to 02:49 UTC:

| Railroad | Live data, one read | Timetable and lines |
|---|---|---|
| Journey Beyond (Australia) | none: nothing is downloaded | none: its timetable and lines ship with the integration |
| NSW TrainLink (Australia) | 124 KB from two feeds, at most once every 55 seconds | 40 MB, when changed, checked daily |
| Queensland Rail Travel (Australia) | the list, 5.5 KB, every 5 minutes; each running train's times, 6 to 8 KB, every 5 minutes | none: its lines ship with the integration |
| V/Line (Australia) | 14 KB from two feeds | 58 MB (V/Line's part of Transport Victoria's 311 MB file, read alone), when changed, checked daily |
| WA Trains (Australia) | none: no live feed exists | 28 MB, when changed, checked daily |
| VR (Finland) | 1.4 KB compressed for the positions; the day's trains, 0.5 MB compressed the first time, then only the changes, once a minute | 3.1 MB, every day |
| Irish Rail (Ireland) | 0.2 KB, at most once every 55 seconds | 6.6 MB, when changed, checked daily; the station list, 46 KB, once a week |
| NS, Arriva, Keolis (the Netherlands) | 1.5 KB, at most once every 9 seconds; delays from OVapi, 5.3 MB, every 5 minutes and only when changed | OVapi's timetable, 267 MB, at most once a week and only when changed; NS's track map, 1.3 MB, every day |
| Vy, Go-Ahead Norge, SJ Nord (Norway) | Vy 510 KB from two feeds, Go-Ahead Norge 7 KB, SJ Nord 0.7 KB once a minute | Vy 67 MB, Go-Ahead Norge 20 MB, SJ Nord 26 MB, when changed, checked daily |
| Renfe (Spain) | 2.1 KB from two feeds | 0.7 MB, every day; its lines ship with the integration |
| Renfe Regionals (Catalunya, Spain) | 0.2 KB from two feeds that carry all of Renfe's local networks | 16 MB, every day |
| The Swedish railroads (Sweden) | 474 KB the first time, then 5 to 9 KB of changes | none; the station list, 0.15 MB, every day; the lines ship with the integration |
| VIA Rail (Canada) | 353 KB, sent compressed as 33 KB | 1.0 MB, once a week |
| Amtrak (United States) | 1.2 MB, sent compressed as 113 KB | 18.6 MB, once a week |
| Brightline (United States) | 1.3 KB from two feeds | 29 KB, once a week |

⚠ When this was measured it was day in Australia, evening in North America
and night in Europe. A live feed is at its smallest at night: in the day the
European feeds are larger than the table shows.

**After an error.** The trains keep moving on the last good data for up to 10
minutes; then they are marked unavailable until the source answers. A
timetable that fails to download is tried again later, and the copy you have
stays in use. If a provider keeps refusing your key for ten minutes, Home
Assistant asks for a new one.

**On disk.** Timetables and route lines are kept in Home Assistant's
`.storage` folder under names beginning `saw_`, shared with the other Live
Track modules that read the same railroad. If you remove Live Track Intercity
Rail and no other Live Track module uses them, you can delete them by hand.

---

## Help it grow

Live Track Intercity Rail is still growing. We add railroads and countries as
we find them, and we want to know what you would like next.

### Suggest something

Is your country or railroad missing? Is something wrong, or hard to
understand? Tell us whichever way is easier for you:

* [**Fill in a short form**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=en.yml)
  in English. You need a free GitHub account.
* **Write an email** to
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  No account needed.

Either way, it helps to tell us:

* what you would like to see, and where in the world;
* a link to where the data is published, if you know one (an open-data page,
  a public feed, a service's website): not needed, but it helps;
* your Home Assistant language, if the problem is the wording or a
  translation.

Write in English or in your own language, whichever is easier for you.

### Add it yourself, with our help

If you would like to add something yourself, we will help you do it, from
the first question to the finished release. You do not need to be a
developer to start:

* **A translation.** The words in the setup dialog are a short list of
  phrases in one text file. We will show you which file and which lines.
* **A new railroad.** Tell us where the data is published. We can write the
  code together, or look over yours.
* **Testing where you live.** Install it, look at your part of the map, and
  tell us what is right and what is not.
* **A fix to this README.** If a step did not match what you saw, tell us
  what you saw.

[**Tell us what you have in mind**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=en.yml)
or write to
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
and we will reply with the next steps.

---

## Languages

This README: **English**, [Deutsch](README.de.md), [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md),
[Suomi](README.fi.md), [Svenska](README.sv.md),
[Norsk bokmål](README.nb.md), [Gaeilge](README.ga.md). Each translated README
is complete. None has yet been read by a native speaker. If one of these
languages is yours, please tell us whether its README reads well: see
[Help it grow](#help-it-grow).

The setup dialog and the options are in English only for now, whatever your
Home Assistant language. A translation of them is welcome:
[we will help you make one](#add-it-yourself-with-our-help).

Found a mistake in a translation, or need another language? Tell us at
<https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues>, or
[translate it with our help](#add-it-yourself-with-our-help).

---

## Credits and licences

Every live source is read at runtime, by your Home Assistant; nothing from a
live feed is in this repository. Each train credits its source in its
`attribution` attribute. Each source's terms bind you, as the person
receiving its data.

* **Amtraker** (amtraker.com), relaying Amtrak's train tracking (United
  States): data under the
  [Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/),
  attribution required. **Amtrak**'s own timetable for the route lines.
* **Brightline** (United States): its GTFS and GTFS-Realtime feeds; Brightline
  publishes no terms.
* **VIA Rail** (Canada): its train-status data, for which VIA publishes no
  terms; its timetable under the Open Government Licence - Canada 2.0
  ([developer resources](https://www.viarail.ca/en/developer-resources)).
* **Fintraffic / digitraffic.fi** (Finland): data under CC BY 4.0.
* **Transport for NSW** (Australia): data under CC BY 4.0
  ([data licence](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australia): data under CC BY 4.0
  ([open data](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Queensland Rail Travel** (Australia): the times its Service Updates page
  shows, read by your Home Assistant; see
  [Queensland Rail's copyright page](https://www.queenslandrailtravel.com.au/copyright).
  Nothing of Queensland Rail Travel's ships with the integration.
* **Journey Beyond** (Australia): its published timetables, transcribed into
  `data/journey_beyond_timetable.json`; Journey Beyond publishes no terms for
  them.
* **Public Transport Authority of Western Australia**: timetable data
  available free of charge from www.transperth.wa.gov.au
  ([spatial data access](https://www.transperth.wa.gov.au/About/Spatial-Data-Access);
  not CC BY).
* **Renfe** (Spain): data under CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)).
* **Entur** (Norway): contains data under the Norwegian licence for Open
  Government data ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)) distributed
  by Entur.
* **Trafikverket** (Sweden): data under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Ireland): live data; Irish Rail publishes no terms. Timetable
  from the [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Ireland), CC BY 4.0, provided as is.
* **NS** (the Netherlands): vehicle data and track map, with your own key, under
  the [NS API portal](https://apiportal.ns.nl/)'s terms. Timetable and delays
  from [OVapi](https://gtfs.ovapi.nl/), CC0.
* **Files shipped in `data/`**: route lines for Journey Beyond, Queensland
  Rail Travel, Renfe (Spain) and Sweden, built from
  [OpenStreetMap](https://www.openstreetmap.org/copyright), © OpenStreetMap
  contributors, under the
  [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/);
  the end-station municipalities of Renfe's trips (OpenStreetMap, ODbL 1.0)
  and their populations (Wikidata property P1082, CC0, else OpenStreetMap);
  Swedish end-city populations from Statistics Sweden (SCB) and Trafikverket,
  both CC0 1.0; Norwegian end-city populations from Statistics Norway, table
  04859, CC BY 4.0.
* **The map card** is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, a copy of [ha-map-card](https://github.com/nathan-gs/ha-map-card) by
  nathan-gs, MIT, shipped in `frontend/`. Its map tiles and their credits are
  in its README.

None of these organisations made or endorsed this integration.

**Code**: MIT, in [LICENSE](LICENSE). The files in `data/` keep their
sources' licences, listed above.

**For developers:** each railroad is one module in
`custom_components/live_track_intercity_rail/operators/`, reading a source
adapter in `sources/`; the shipped route lines are rebuilt with the scripts in
`tools/` (`journey_beyond.py`, `qrt_lines.py`, `renfe_spain_lines.py`,
`sweden_lines.py`). The tests run with
`python -m unittest discover -s tests`.

**Acknowledgement.** StrausbergAutomationWorks pays its respect to Elders past
and present and acknowledges the contributions of First Nations (Aboriginal
and Torres Strait Islander) peoples.

---

## Keywords

Home Assistant trains · Home Assistant train tracker · live train map ·
intercity rail · long-distance trains · GTFS-Realtime · Amtrak · Amtraker ·
Brightline · VIA Rail · trains en temps réel · VR · kaukojunat · NSW
TrainLink · XPT · V/Line · The Ghan · Indian Pacific · Spirit of Queensland ·
Transwa · Renfe · AVE · Avlo · Alvia · Rodalies · trenes en tiempo real · Vy ·
SJ Nord · tog i sanntid · SJ · Snälltåget · Öresundståg · tåg i realtid ·
Irish Rail · Enterprise · traenacha beo · NS Intercity · Arriva · treinen live ·
Zugverkehr · treni in tempo reale · togtrafik · 火车实时地图 · geo_location ·
map card · Lovelace · HACS · Marketplace · Live Track · LiveTrack ·
StrausbergAutomationWorks
