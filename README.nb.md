# Live Track Intercity Rail

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · **Norsk bokmål** · [Gaeilge](README.ga.md) · [Alle språk](#språk)

**Fjerntog i Home Assistant, på ett kart.** Live Track Intercity Rail setter
hvert tog fra de intercity- og fjerntogjernbanene du velger på Home
Assistant-kartet ditt: hvor det er, nummeret, om det er forsinket etter
jernbanens egen regel, og neste stopp. Hver jernbane legges til for seg, fra
sine egne publiserte data.

> **Live Track Intercity Rail er én modul i Live Track**, en familie av Home
> Assistant-integrasjoner som tegner alt som beveger seg, og været det
> beveger seg gjennom, på ett felles kart: fly, skip, tog og vær. Installer
> den alene eller ved siden av de andre modulene
> ([liste nedenfor](#en-del-av-live-track-de-andre-modulene)).

> **Vokser, og åpen for ideer.** Live Track Intercity Rail dekker i dag 33
> jernbaner i 9 land på 3 kontinenter, og vi legger til flere jernbaner og
> land. Mangler din? [Foreslå den](#hjelp-den-å-vokse), eller legg den til
> selv: vi hjelper deg med det.

**Status: 0.1.3, utgitt.** I Marketplace sin katalog ([installer den
nedenfor](#installer-den-trinn-for-trinn)).

Originalt arbeid av StrausbergAutomationWorks. Ikke tilknyttet, eller
godkjent av, Amtrak, Amtraker, Brightline, VIA Rail, Fintraffic, VR,
Transport for NSW, NSW TrainLink, Transport Victoria, V/Line, Queensland
Rail, Journey Beyond, kollektivtrafikkmyndigheten i Vest-Australia (Public
Transport Authority of Western Australia), Transwa, Renfe, Rodalies de
Catalunya, Entur, Vy, Go-Ahead Norge, SJ Nord, Trafikverket, SJ, VR
Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen,
Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget,
Värmlandstrafik, Tågab, Inlandsbanan, Irish Rail, Irlands
transportmyndighet (National Transport Authority), NS, Arriva, Keolis,
OVapi eller noen annen jernbane.

---

## Innhold

1. [Alt den gjør](#alt-den-gjør)
2. [Hvor den virker](#hvor-den-virker)
3. [En del av Live Track: de andre modulene](#en-del-av-live-track-de-andre-modulene)
4. [Før du begynner](#før-du-begynner)
5. [Installer den, trinn for trinn](#installer-den-trinn-for-trinn)
6. [Sett den opp, trinn for trinn](#sett-den-opp-trinn-for-trinn)
7. [Gratis nøkler som slår på mer, trinn for trinn](#gratis-nøkler-som-slår-på-mer-trinn-for-trinn)
8. [Sett kartet på et dashbord](#sett-kartet-på-et-dashbord)
9. [Bruk den i automasjoner](#bruk-den-i-automasjoner)
10. [Alt på kartet, i detalj](#alt-på-kartet-i-detalj)
11. [Alle entitetene den lager](#alle-entitetene-den-lager)
12. [Hva den sender og laster ned](#hva-den-sender-og-laster-ned)
13. [Hjelp den å vokse](#hjelp-den-å-vokse)
14. [Språk](#språk)
15. [Kreditering og lisenser](#kreditering-og-lisenser)
16. [Søkeord](#søkeord)

---

## Alt den gjør

### På kartet, uten noe å sette opp

Du legger til en **jernbane**: du velger et land, og så én av landets
intercityjernbaner. Alt nedenfor vises da for den jernbanen. Legg til
integrasjonen på nytt for hver annen jernbane du vil ha.

| Hva | Hvor | Fra |
|---|---|---|
| **Tog i trafikk**: én markør per tog, merket med tognummeret eller linjen, i jernbanens egne farger, vendt i retningen det går | hver jernbane | hver jernbanes egne publiserte data |
| **Forsinkelse**: et tog vises som forsinket eller svært forsinket etter jernbanens egen regel; der en jernbane ikke publiserer noen regel, etter hvor langt toget går | hver jernbane som melder forsinkelser | hver jernbanes egen strøm |
| **Neste stopp og tiden for det**: stasjonen toget stopper ved neste gang, og når det ventes dit | hver jernbane der strømmen eller ruteplanen sier det | hver jernbanes egen strøm og ruteplan |
| **Tog som følger sporet**: mellom to meldinger beveger et tog seg langs sin egen linje i sin siste fart, ikke rett over | hver jernbane der linjen er kjent | hver jernbanes ruteplan, eller linjer som følger med integrasjonen |
| **Tog fra ruteplanen**: der en jernbane ikke publiserer posisjoner, plasseres hvert tog på linjen sin etter tidene sine og merkes som et anslag | Journey Beyond, Queensland Rail Travel og WA Trains (Australia), SJ Nord (Norge); Irish Rail med sin siste forsinkelse | hver jernbanes ruteplan eller tider |
| **Bilder for noen tog**: Julenissetoget og en sommerhytte (Finland), dyrene på Journey Beyonds tog, ett bilde for hver linje hos Queensland Rail Travel | Finland, Australia | tegnet for denne integrasjonen |
| **Stanset ved grensen**: et tog som står ved en grenseovergang mellom USA og Canada viser "Customs" (toll) i stedet for forsinkelsen | Amtraks tog til og fra Canada | Amtraks posisjoner |
| **Ett antall per jernbane**: tog i trafikk | hver jernbane | de samme dataene |

### Slått på med din egen gratis nøkkel eller konto

| Gratis nøkkel eller konto | Hva den legger til |
|---|---|
| Nøkkel til **Transport for NSW Open Data** | NSW TrainLinks regiontog (New South Wales, Australia) |
| Nøkkel til **Transport Victoria Open Data** | V/Lines fjerntog (Victoria, Australia) |
| Nøkkel til **NS API portal** | NS Intercity, Arrivas og Keolis' regiontog (Nederland); én nøkkel holder til alle tre |
| Nøkkel til **Trafikverket** | de 15 svenske jernbanene; én nøkkel holder til alle femten |

Hver tar noen minutter å skaffe: [trinn for trinn nedenfor](#gratis-nøkler-som-slår-på-mer-trinn-for-trinn).
De andre 13 jernbanene trenger ingen nøkkel.

---

## Hvor den virker

| Region | Hva du får | Fra | Trenger |
|---|---|---|---|
| **Australia**: hele landet | Journey Beyond: The Ghan, The Ghan Expedition, Indian Pacific, Great Southern, The Overland, bare fra ruteplanen ([hvorfor](#journey-beyond-australia)) | Journey Beyond | ingenting |
| **Australia**: New South Wales | NSW TrainLinks regiontog (XPT og Xplorer), også inn i Queensland, Victoria og Australian Capital Territory | Transport for NSW | en gratis nøkkel |
| **Australia**: Queensland | Queensland Rail Travel: Spirit of Queensland, Spirit of the Outback, Tilt Train, Westlander, Inlander, Kuranda Scenic Railway, Gulflander, fra de publiserte tidene ([hvorfor](#queensland-rail-travel-australia)) | Queensland Rail Travel | ingenting |
| **Australia**: Victoria | V/Lines fjerntog (lokaltoglinjene er i Live Track Commuter Rail), også inn i New South Wales | Transport Victoria | en gratis nøkkel |
| **Australia**: Vest-Australia | WA Trains: Australind, Prospector, MerredinLink og AvonLink, bare fra ruteplanen ([hvorfor](#wa-trains-vest-australia-australia)) | kollektivtrafikkmyndigheten i Vest-Australia | ingenting |
| **Europa**: Finland | VRs fjerntog | Fintraffic Digitraffic | ingenting |
| **Europa**: Irland | Irish Rails InterCity-tog, og Enterprise fra Dublin til Belfast (Storbritannia) | Irish Rail, National Transport Authority | ingenting |
| **Europa**: Nederland | NS Intercity, og regiontogene til Arriva (Arriva, RRReis, Blauwnet) og Keolis (Blauwnet, RRReis); NS Sprinter er i Live Track Commuter Rail | NS, OVapi | en gratis nøkkel |
| **Europa**: Norge | Vys F-, RE-, RX- og R-linjer (F1 også inn i Sverige), Go-Ahead Norges F5 og R50, SJ Nords F6, F7 og R60 til R75 | Entur | ingenting |
| **Europa**: Spania | Renfes AVE-, Avlo-, Alvia-, Avant-, Euromed-, Intercity-, MD- og Regional-tog, også inn i Frankrike og Portugal; Rodalies de Catalunyas regionlinjer R11 til R17 | Renfe | ingenting |
| **Europa**: Sverige | SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget, Värmlandstrafik, Tågab og Inlandsbanan, én jernbane hver; Öresundståg også inn i Danmark | Trafikverket | en gratis nøkkel |
| **Nord-Amerika**: Canada | VIA Rail, hver rute | VIA Rail | ingenting |
| **Nord-Amerika**: USA | Amtrak, hver rute, også inn i Canada | Amtraker | ingenting |
| **Nord-Amerika**: USA | Brightline (Florida) | Brightline | ingenting |

Står den ikke på listen? [Si fra](#hjelp-den-å-vokse). Der noen publiserer
dataene åpent, ser vi på å legge den til.

⚠ **Et tog er bare så godt som jernbanens data.** Noen jernbaner melder et
tog med noen sekunders mellomrom, noen med noen minutters, noen bare når det
passerer signaler, og noen publiserer ingen posisjoner i det hele tatt. Hver
jernbanes begrensninger står under
[Alt på kartet, i detalj](#alt-på-kartet-i-detalj).

⚠ **Det er ikke jernbanens offisielle informasjon.** Sjekk jernbanens egen
app eller nettside før du reiser.

---

## En del av Live Track: de andre modulene

Live Track er et sett Home Assistant-integrasjoner, én for hver slags ting som
beveger seg, alle tegnet på det samme kartkortet. Hver virker alene; sammen
blir de ett levende bilde. De deler kartkortet og et Python-bibliotek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
så å installere én til legger ingen forespørsler til en kilde som en annen
allerede leser.

| Modul | Hva den viser på kartet | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | fly over deg via ADS-B, med ruter og typeikoner | utgitt |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | skip og båter via AIS, nær deg eller hvor som helst | utgitt |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | lokaltog i Nord-Amerika, Europa og Australia | utgitt |
| **Live Track Intercity Rail** | intercity- og fjerntog i Nord-Amerika, Europa og Australia (denne modulen) | utgitt |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | fly og fartøy brukt av immigrasjons- og føderale politimyndigheter, fra offentlige lister | utgitt |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | vær, stormer og naturfarer | utgitt |
| Live Track Stations | avgangstavler og "på tide å gå"-varsler for hver stasjon | planlagt |
| Live Track Satellites | satellitter som passerer over deg | planlagt |
| Live Track Freight Trains | godstog og arbeidstog der jernbaner publiserer dem | planlagt |
| Live Track Transit | bybusser, trikker, ferger og T-bane | planlagt |
| Live Track Intercity Buses | ekspress- og regionbusser | planlagt |
| Live Track Commuter Buses | pendlerbusser | planlagt |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | det felles kartkortet hver modul tegner på | utgitt, installeres med hver modul |

Alt er gratis og åpen kildekode. Ingenting holdes tilbake for sponsorer.

---

## Før du begynner

* **Home Assistant** 2026.11 eller nyere.
* **Marketplace** (HACS) i Home Assistant, for å installere og oppdatere den
  på den enkle måten. Uten den kan du kopiere filene for hånd.
* **Internettilgang** for Home Assistant: hvert tog kommer fra jernbanens
  egne publiserte data.
* Ingenting å betale. 13 av de 33 jernbanene trenger ingen konto; de andre 20
  trenger en egen gratis nøkkel, og fire nøkler dekker alle
  ([ovenfor](#slått-på-med-din-egen-gratis-nøkkel-eller-konto)).
* Home Assistant installerer selv Python-pakkene den trenger
  (`saw-livetrack`, `gtfs-realtime-bindings` og `tzdata`) første gang
  integrasjonen lastes.

---

## Installer den, trinn for trinn

### Fra Marketplace (anbefalt)

1. Åpne **Innstillinger → Marketplace** (HACS) i Home Assistant.
2. Søk etter **Live Track Intercity Rail** og åpne den.
3. Velg **Last ned** (eller **Installer**).
4. **Start Home Assistant på nytt**: **Innstillinger → System →
   Reparasjoner** tilbyr omstarten, eller bruk **Innstillinger → System →
   Omstart**.

Hvis søket ikke finner den, legg den til via lenken: velg **Legg til fra lenke**
(eller trepunktsmenyen → **Egendefinerte kodelager**), skriv inn
`StrausbergAutomationWorks/LiveTrackIntercityRail`, velg **Integrasjon** hvis du
blir spurt om typen, og fortsett deretter fra trinn 3.

Marketplace tilbyr deretter hver nye utgivelse som en oppdatering.

### For hånd

1. Last ned kildekoden til den
   [nyeste utgivelsen](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/releases/latest).
2. Kopier mappen `custom_components/live_track_intercity_rail` fra den til
   mappen `custom_components` i Home Assistant-konfigurasjonsmappen din (lag
   `custom_components` hvis den ikke finnes).
3. Start Home Assistant på nytt.

For å oppdatere for hånd, erstatt mappen med den fra den nye utgivelsen og
start på nytt.

---

## Sett den opp, trinn for trinn

1. Åpne **Innstillinger → Enheter og tjenester**.
2. Velg **Legg til integrasjon** (nede til høyre) og søk etter **Live Track
   Intercity Rail**.
3. **Region** (region): velg jernbanens land. Bare land med minst én
   jernbane vises. Velg **Send inn**.
4. **Railroad** (jernbane): velg jernbanen. Velg **Send inn**.
5. **API key** (API-nøkkel): bare for NSW TrainLink, V/Line, de tre
   nederlandske jernbanene og de femten svenske jernbanene. Lim inn nøkkelen
   din ([slik får du en](#gratis-nøkler-som-slår-på-mer-trinn-for-trinn)) og
   velg **Send inn**. De andre jernbanene hopper over dette trinnet.

Det er alt. Togene vises innen et minutt eller to. Der en jernbanes linjer
kommer fra ruteplanen, begynner togene å følge linjene sine når ruteplanen er
lastet ned, noe som kan ta noen minutter første gang. For å følge en annen
jernbane, legg til integrasjonen på nytt. Samme jernbane to ganger avvises.

### Endre hva den viser: alternativene

Åpne **Innstillinger → Enheter og tjenester → Live Track Intercity Rail →
Konfigurer** (tannhjulet) på jernbanen du vil endre. Det finnes ett
alternativ:

| Alternativ | Hva det gjør | Standard |
|---|---|---|
| **Poll interval** (spørreintervall) | hvor ofte jernbanens kilde leses, 15 til 600 sekunder. Et kortere intervall enn kildens egen oppdatering viser ikke mer | satt per jernbane: 15 sekunder for Renfe (Spain) og de tre nederlandske jernbanene; 60 sekunder for Brightline, NSW TrainLink, Irish Rail og SJ Nord; 30 sekunder for de andre |

---

## Gratis nøkler som slår på mer, trinn for trinn

Tjue jernbaner ber hver bruker om en egen nøkkel, fra fire leverandører.
Hver av disse nøklene er gratis, og hver som installerer Live Track
Intercity Rail skaffer sin egen. Du limer inn nøkkelen når oppsettdialogen
ber om den ([trinn 5 ovenfor](#sett-den-opp-trinn-for-trinn)). Bare
nøkkelen etterspørres: ikke passord og ingen hemmelighet. Nøkkelen lagres i
Home Assistant sammen med integrasjonen, sendes bare til sin egen
leverandør, og skrives aldri til loggen. Hvis leverandøren avviser den i ti
minutter, ber Home Assistant deg om en ny.

### Transport for NSW (NSW TrainLink, New South Wales, Australia)

1. Åpne <https://opendata.transport.nsw.gov.au/>, velg **Register**, lag en
   konto og logg inn.
2. Velg ikonet for brukerprofilen din, og så **API Tokens**.
3. Skriv et navn på nøkkelen og velg **CREATE API TOKEN**. Kopier nøkkelen
   med en gang: nettstedet viser den bare én gang.
4. Lim den inn i **API key** når du legger til NSW TrainLink. Lim inn bare
   nøkkelen: Live Track Intercity Rail legger selv til ordet `apikey`.

### Transport Victoria (V/Line, Victoria, Australia)

1. Åpne <https://opendata.transport.vic.gov.au/>, velg **Login**, og så
   **Sign up**.
2. Fyll inn opplysningene dine og velg **Create Account**. Skriv inn koden
   fra e-posten du får og velg **Confirm**.
3. Portalen krever en autentiseringsapp på telefonen: skann QR-koden med den,
   skriv inn appens kode og velg **Confirm**. Logg så inn med e-postadressen,
   passordet og appens kode.
4. Velg **My Account** → **Profile** → **API tokens**. Nøkkelen din ligger
   der allerede. Lim den inn i **API key** når du legger til V/Line.

### NS (NS, Arriva og Keolis, Nederland)

1. Åpne <https://apiportal.ns.nl/>, velg **Inloggen** (logg inn), og så
   **Externe bezoeker** (ekstern besøkende).
2. Fyll ut skjemaet og send det. En e-post bekrefter registreringen. Det kan
   ta opptil 5 minutter før API-ene vises i portalen.
3. Åpne siden for **Virtual Train API** (NS' togposisjoner). Under **Related
   Products**, åpne produktet, gi abonnementet ditt et navn og velg
   **Subscribe**.
4. Når NS har godkjent abonnementet, ligger nøkkelen din på profilsiden. Lim
   den inn i **API key** når du legger til NS, Arriva eller Keolis. Én
   nøkkel holder til alle tre.

### Trafikverket (de 15 svenske jernbanene)

1. Åpne <https://data.trafikverket.se/oauth2/Account/register>.
2. Fyll inn **Email**, **Displayname**, **Password** og **Confirm password**,
   kryss av for **Accept license and Agreement** og velg **Register**.
3. Åpne <https://data.trafikverket.se/get-started> og velg **Create key**,
   under **Create a key**. Logg inn med kontoen du lagde, og lag nøkkelen.
4. Lim den inn i **API key** når du legger til en svensk jernbane. Én nøkkel
   holder til alle femten.

---

## Sett kartet på et dashbord

Kartet er [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
kortet hver Live Track-modul tegner på. **Det installeres med Live Track
Intercity Rail**: ingenting å laste ned, ingenting å kopiere, ingen ressurs å
legge til.

1. Åpne et dashbord, velg blyanten (**Rediger dashbord**), og så **Legg til
   kort**.
2. Rull helt ned og velg **Manuell**.
3. Lim inn dette og velg **Lagre**:

```yaml
type: custom:live-track-map-card
entity_filter:
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

Andre Live Track-moduler legges i `entity_filter` på samme måte: én regel
`- domain: geo_location` til for hver kilde.

**På kartet:**

* Hvert tog er en markør i jernbanens farger, merket med tognummeret eller
  linjen. Amtraks tog er stjerner, VIA Rails bærer lønnebladet, Irish Rails
  InterCity-tog er kløverblader, og noen tog er bilder (hver jernbane
  nedenfor sier hvilke).
* På de fleste jernbaner bytter fargene med retningen: én vei når toget
  forlater hovedbyen, den andre på vei mot den.
* En pil viser retningen toget går. Et tog som står stille, beholder sin
  siste retning. Bilder står oppreist og har ingen pil.
* **Pek på** et tog for å se jernbanen, nummeret, linjen og hvor det går.
  **Klikk** på det for alle detaljene, neste stopp og forsinkelsen
  medregnet.

Hvis ressursene til dashbordene dine er satt i YAML
(`lovelace: resource_mode: yaml`), kan ingenting registreres for deg: en sak
under **Reparasjoner** gir da de nøyaktige linjene som skal inn i
`configuration.yaml`. De ser slik ut, med integrasjonens egen adresse i
stedet for plassholderne:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_intercity_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Hver Live Track-modul har en kopi av kortet og registrerer den når Home
Assistant starter. Sammen holder de nøyaktig én rad i **Innstillinger →
Dashbord → Ressurser**: den nyeste kortversjonen noen av dem har, aldri en
eldre. Et kort du selv har installert via Marketplace, får være i fred. Når
du fjerner denne modulens siste jernbane, går raden over til en annen Live
Track-modul, eller fjernes hvis ingen er igjen. Hvis integrasjonens filer
fjernes mens jernbanene fortsatt er satt opp, og ingen annen Live
Track-modul er installert, fjerner du raden selv i **Innstillinger →
Dashbord → Ressurser**.

**For å installere kortet for hånd i stedet**, følg trinnene i
[kortets README](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
En rad du selv har laget for en kopi under `/local/` eller på en annen adresse,
blir aldri endret eller fjernet. Så lenge den laster kortet, overlater hver Live
Track-modul kortet til den, også når en modul har en nyere utgivelse, og
ingenting under **Reparasjoner** sier fra om det. For å gå tilbake til modulens
kopi fjerner du raden din under **Innstillinger → Dashbord → Ressurser** og
starter Home Assistant på nytt. Hvis du sletter filen til kopien din, fjerner du
også raden: så lenge en rad med en fil som er borte, står igjen, legger modulen
ikke til en egen rad.

Alle andre kartkort som viser `geo_location`-entiteter, viser også togene,
som vanlige markører.

---

## Bruk den i automasjoner

Alt er vanlige Home Assistant-entiteter, så automasjonsredigereren virker med
dem, uten kode.

**Et varsel på telefonen når jernbanens data stopper** (togene forsvinner da
fra kartet):

1. **Innstillinger → Automasjoner og scener → Opprett automasjon → Opprett
   ny automasjon**.
2. **Når**: **Legg til utløser** → **Entitet** → **Tilstand endret**. Velg
   jernbanens entitet **Trains in service** (tog i trafikk), og under **Til
   (valgfritt)** velg **Utilgjengelig**.
3. **Så gjør**: **Legg til handling**, søk etter telefonens varslingshandling
   (den bærer telefonens navn), og skriv en melding, for eksempel:

   ```text
   Ingen fjerntog på kartet: jernbanens data har stoppet
   ```

4. **Lagre**.

**Andre ideer:** et lys som tennes når et Amtrak-tog er innenfor 2 km (1,2
engelske mil) fra hjemmet ditt i USA, ut fra markørenes avstand; et tall på
dashbordet over togene VR kjører i Finland gjennom dagen; en melding når
Queensland Rail Travels første tog for dagen går (Australia), når **Trains in
service** stiger over 0.

---

## Alt på kartet, i detalj

### Tog

Hvert tog er én markør. Tilstanden er avstanden fra hjemmet ditt, i
kilometer. Markøren vises når jernbanen melder toget, eller når ruteplanen
sier at det går, og fjernes når toget forsvinner fra jernbanens data eller
turen er over.

* **Mellom to meldinger** beveger et tog seg langs sin egen linje mot neste
  stopp: i farten jernbanen melder, eller, der den ikke melder noen, i
  farten mellom de to siste meldingene. Det passerer aldri neste stopp, og
  slutter å bevege seg 30 minutter etter siste melding. Et tog på en kjent
  linje tegnes på linjen; jernbanens egen melding beholdes ved siden av.
* **Hvis en jernbanes data svikter**, fortsetter togene å bevege seg på siste
  gode melding i opptil 10 minutter. Etter det er de utilgjengelige og
  forsvinner fra kartet til dataene kommer tilbake.
* **Forsinket og svært forsinket**: der jernbanen publiserer sin egen regel
  for et forsinket tog, bruker integrasjonen den. Der den ikke publiserer
  noen, er et tog forsinket etter hvor langt det går, med terskelverdiene
  fra Amtrak Status Maps (asm.transitdocs.com). Hver jernbane nedenfor sier
  hvilken.

På hvert tog: `marker_label`, `train`, `line_name`, `observed_at` (når
meldingen var riktig), `course_deg` (mens det beveger seg), `next_stop` og
`arrival_estimated_at` (der de er kjent), `delay_min`, `late_threshold_min`
og `very_late_threshold_min`, `speed_kmh` (der jernbanen melder den),
`attribution`, og, mellom to meldinger, `previous_latitude`,
`previous_longitude`, `previous_observed_at` og `segment_duration_s`. Et tog
som er flyttet langs linjen sin, har `position_source: estimated`, med
jernbanens melding i `fix_latitude` og `fix_longitude`.

### Journey Beyond (Australia)

⚠ **Journey Beyond publiserer ingen posisjoner.** Hvert tog tegnes fra den
publiserte ruteplanen, overført til en fil som følger med integrasjonen
(avganger til 29. desember 2027), så ingenting lastes ned. Hvert tog
plasseres på linjen sin etter tidene sine, merket som et anslag, uten
forsinkelse: et forsinket eller innstilt tog tegnes likevel i rute. Hver
tjeneste er sitt eget bilde (kamelen og rytteren, en fugl, en kenguru, en
emu), i sine farger på vei ut og med fargene byttet på vei tilbake, uten
etikett: pek på den for å se toget og turen.

### NSW TrainLink (New South Wales, Australia)

Fra Transport for NSWs strøm for NSW TrainLink, med din egen nøkkel, en ny
posisjon omtrent én gang i minuttet. Etiketten er tognummeret. NSW-oransje med
en hvit ring når toget forlater Sydney, byttet på vei dit. Strømmen har ingen
fart, så et tog beveger seg langs linjen i farten mellom de to siste
posisjonene. Forsinket fra 11 minutter (NSW TrainLink regner et tog som i
rute innen 10 minutter), svært forsinket fra 30.

### Queensland Rail Travel (Australia)

⚠ **Queensland Rail Travel publiserer ingen posisjoner.** Home Assistant
leser tidene som Queensland Rail Travels side Service Updates viser: listen
over dagens tog høyst hvert 5. minutt, og hvert togs tider høyst hvert 5.
minutt fra 30 minutter før avgang til 15 minutter etter ankomst. Hvert tog
plasseres på linjen sin etter disse tidene og merkes som et anslag. Hver
linje er sitt eget bilde, i sine farger når toget forlater Brisbane og
byttet på vei dit, med tognummeret i en lapp ved siden av. Forsinket eller
svært forsinket vises ikke.

### V/Line (Victoria, Australia)

Fra Transport Victorias strøm for V/Line, med din egen nøkkel: fjernlinjene
til Albury, Ararat, Bairnsdale, Echuca, Maryborough, Shepparton, Swan Hill og
Warrnambool. Etiketten er tognummeret. V/Line-lilla med en gul ring når
toget forlater Melbourne, byttet på vei dit. Strømmen har ingen fart, så et
tog beveger seg i farten mellom de to siste posisjonene; etter 10 minutter
uten ny posisjon tidfestes det mot neste stopp. Forsinket fra 11 minutter
på de lange linjene og 6 på de korte (V/Lines egen liste), svært forsinket
fra 30.

### WA Trains (Vest-Australia, Australia)

⚠ **Ingen levende posisjoner publiseres.** Hvert tog tegnes fra ruteplanen
til kollektivtrafikkmyndigheten i Vest-Australia: plassert langs linjen sin
etter ruteplantidene, merket som et anslag, uten forsinkelse. Ruteplanen
sjekkes én gang om dagen. Etiketten er rutens tre første bokstaver: AUS
(Australind, lilla), PRO (Prospector, oransje), MER (MerredinLink, grønn)
og AVO (AvonLink, grønn), de samme begge veier.

### VR (Finland)

Fra Fintraffics Digitraffic, en ny posisjon omtrent hvert 30. sekund.
Etiketten er togtype og nummer, slik VR skriver det (`IC 23`). VR-grønn med
en mørk ring når toget forlater Helsingfors, byttet på vei dit. Dataene har
ingen retning, så pilen følger linjen. Forsinket fra 6 minutter (VR regner et
tog som forsinket når det er mer enn fem minutter sent), svært forsinket fra
12.

* **Julenissetoget**, fra første søndag i advent til 6. januar: en snømann
  på vei nordover, et reinsdyr på vei tilbake, uten nummer. Fra 12 minutters
  forsinkelse snur figuren seg rundt med noen sekunders mellomrom.
* **Sommerhytta**, fra sankthansaften til 31. juli: hvert fjerntog hos VR
  tegnes som en hytte, med nummeret ved siden av.

### Irish Rail (Irland)

Fra Irish Rails levende trafikkinformasjon og ruteplanen fra Irlands
transportmyndighet (National Transport Authority). ⚠ Irish Rail melder et
tog bare når det passerer signalpunkter med noen minutters mellomrom, så
hvert tog tegnes fra ruteplanen og sin siste forsinkelse, flyttet langs
ruten. Etiketten er tognummeret uten bokstav (A700 vises som 700). Et
InterCity-tog er et grønt kløverblad med oransje omriss og nummer når det
forlater Dublin, fargene byttet på vei dit. Enterprise er en sølvskive med en
rød ytre ring, et magenta bånd og et magenta nummer; på vei til Dublin er
skiven magenta. Forsinket fra 10 minutter (National Transport Authoritys
regel), svært forsinket fra 20.

### NS, Arriva og Keolis (Nederland)

Fra NS' kjøretøydata, med din egen nøkkel, en ny posisjon omtrent hvert 10.
sekund. Denne strømmen melder togets egen fart og retning, og begge sendes
videre. Neste stopp og forsinkelsen kommer fra OVapis ruteplan; sporet er
NS' eget kart over linjene, lastet ned én gang om dagen. Etiketten er
tognummeret. NS' tog er gule med en ring i NS-blått; Arrivas og Keolis' tog
har kartkortets eget utseende inntil videre. Forsinket fra 3 minutter (NS'
egen definisjon), svært forsinket fra 10.

### Vy, Go-Ahead Norge og SJ Nord (Norge)

Fra Entur, hver jernbane sin egen oppføring. Etiketten er linjekoden (F4,
RE10, R50). Linjens egen farge med en hvit ring når toget forlater Oslo S
(på en tur som ikke når Oslo S, den største endebyen), byttet på vei dit.
Entur publiserer ingen fart og ingen retning, så et tog beveger seg i farten
mellom de to siste posisjonene, og pilen følger linjen. I Oslos lange
tunneler flyttes et tog som mister posisjonene langs linjen sin til de
kommer tilbake. ⚠ **SJ Nord publiserer ingen posisjoner:** hvert av togene
plasseres på linjen sin etter de forventede tidene. Forsinket fra 4
minutter, og fra 6 på F-linjene og linjene til Göteborg (Sverige), Bane
NORs og Vys regel; svært forsinket ved det dobbelte.

### Renfe (Spain) og Renfe Regionals (Catalunya), Spania

**Renfe (Spain)** leser Renfes fjerntrafikkstrøm, en ny posisjon omtrent
hvert 15. sekund. Etiketten er tognummeret; tjenesten (AVE, Avlo, Alvia og så
videre) står i svevevinduet. AVE marineblå, Avlo turkis, alle andre
tjenester Renfe-lilla, hver fylt når toget forlater Madrid (på en tur som
ikke når Madrid, den største endebyen) og byttet på vei dit. Renfe
publiserer ingen linjetraseer, så linjene er bygget fra OpenStreetMap og
følger med integrasjonen. Renfe publiserer ingen regel for et forsinket tog,
så et tog er forsinket etter reisens lengde: fra 10 minutter opptil 400 km
(250 engelske mil), 15 opptil 560 km (350 engelske mil), 20 opptil 725 km
(450 engelske mil), 25 opptil 885 km (550 engelske mil), 30 utover det;
svært forsinket ved det dobbelte.

**Renfe Regionals (Catalunya)** tegner Rodalies de Catalunyas regionlinjer
R11 til R17. Etiketten er tognummeret, i linjens egen farge, fylt når toget
forlater Barcelona og byttet på vei dit. Utenfor Barcelona er en posisjon
den siste stasjonen toget passerte, så toget tidfestes mellom stasjonene
etter ruteplanen og forsinkelsen. Forsinket fra 10 minutter, svært forsinket
fra 20, etter den lengste linjens lengde. Med begge Renfe-jernbanene satt
opp tegnes hvert tog én gang.

### De svenske jernbanene (Sverige)

Fra Trafikverket, med din egen nøkkel (én nøkkel for alle femten).
Etiketten er tognummeret på billetten; merkevaren, nummeret og
endestasjonene står i svevevinduet. Hver merkevare har sine egne farger,
byttet på vei til Stockholm C (på en tur som ikke når Stockholm C, den
største endebyen). Trafikverket gir en fart på omtrent halvparten av
posisjonene; de andre togene beveger seg i farten mellom de to siste
posisjonene. Sverige publiserer ingen linjetraseer, så linjene er bygget fra
OpenStreetMap og følger med integrasjonen. Forsinket fra 6 minutter
(Trafikverket regner et tog som i rute til og med 5 minutter 59 sekunder),
svært forsinket fra 12.

### VIA Rail (Canada)

Fra VIA Rails egne togstatusdata. Hvert tog er en skive med lønnebladet og
et bånd i rutegruppens farge (Atlantic, Western, Ontario og Quebec, Prince
Rupert, Churchill, Sudbury til White River, Montréals naturskjønne ruter),
med tognummeret i en oppreist lapp. Oddetall har en gul skive, partall en
skive i båndets farge. Et tog uten ny posisjon beveger seg mot neste stopp
for å komme fram ved VIAs eget anslag. VIA publiserer ingen regel for et
forsinket tog, så et tog er forsinket fra 10 minutter i korridoren Québec
City til Windsor og fra 60 andre steder (Amtrak Status Maps' verdier for
VIA), svært forsinket ved det dobbelte.

### Amtrak (USA)

Amtrak publiserer ingen åpne levende data. Amtraker videresender Amtraks
egen togsporing, med en ny posisjon hvert 3. til 5. minutt, og integrasjonen
flytter hvert tog langs linjen i farten Amtrak melder. Hvert tog er en
stjerne med nummeret tvers over, i rutens farger (Northeast-rutene,
Cascades, Pacific Surfliner, Acela med flere), ellers flaggstjernen. Maple
Leaf (New York til Toronto) skifter sakte mellom Amtraks stjerne og VIAs
merke. Et tog som står ved grensen ved Lacolle, Rouses Point eller Niagara
Falls, viser "Customs" (toll) i stedet for forsinkelsen. Forsinket fra 16
minutter (Amtrak regner et tog som i rute innen 15 minutter), svært forsinket
fra 30. Samme tognummer kan gå på to eller tre dager samtidig, så hver tur er
sin egen markør.

### Brightline (USA)

Fra Brightlines egen strøm, en ny posisjon omtrent hvert 60. sekund.
Etiketten er turnummeret, i svart med hvitt omriss, på en skive i fargen til
togets bestemmelsessted, med en svart ring. En posisjon eldre enn 5 minutter
brukes ikke. Strømmen har ingen fart, så et tog beveger seg i farten mellom
de to siste posisjonene. Brightline publiserer ingen regel for et forsinket
tog, så et tog er forsinket fra 10 minutter, svært forsinket fra 20, etter
reisens lengde.

---

## Alle entitetene den lager

For hver jernbane:

| Entitet | Hva den er |
|---|---|
| `sensor.<railroad>_trains_in_service` | **Trains in service** (tog i trafikk): hvor mange tog jernbanen kjører på kartet akkurat nå. For Amtrak: `sensor.amtrak_trains_in_service` |
| `geo_location.<railroad>_train_…` | én per tog (`geo_location.amtrak_train_5_17`); den kommer og går med toget. Hver har `source: live_track_intercity_rail`, og tilstanden er avstanden fra hjemmet ditt i kilometer |

En markørs entitets-ID kommer fra jernbanen og turen, aldri fra etiketten:
`geo_location.amtrak_train_5_17` er Amtraks tog 5 som gikk den 17. i
måneden, så et tog beholder samme entitets-ID hele turen, og en annen tur
med samme nummer får sin egen. Markøren fjernes når turen forsvinner fra
jernbanens data eller slutter. Markørene har ingen unik ID (unique ID), like
lite som noen kartmarkør i Live Track, så de kan ikke gis nytt navn, skjules
eller få et område i grensesnittet. Sensoren har en unik ID og kan gis nytt
navn.

Attributter som endres ved hver spørring, markørenes posisjoner og tider,
registreres i Home Assistants historikk, som for enhver entitet. Sensoren
har ingen attributter, så den koster lite å beholde, og den er registeret
over hvor mange tog som gikk på en dag. For å holde markørene utenfor
historikken, legg dette til i `configuration.yaml` og start på nytt:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_train_*
```

Hvis `configuration.yaml` allerede har en `recorder:`-seksjon, legg bare til
mønsteret `geo_location.*_train_*` i den, under `exclude:` og
`entity_globs:`. Mønsteret treffer bare denne modulens togmarkører. Et
kartkort som er satt til å tegne historikk, har da ikke noe spor å tegne.

---

## Hva den sender og laster ned

**Om posisjonen din.** Ingenting. Hjemmets posisjon brukes bare inne i Home
Assistant, for å gi hvert togs avstand. Nøkkelen din, der en jernbane
trenger en, sendes bare til den jernbanens leverandør. Ingenting annet om deg
sendes noe sted. Hver tjeneste ser internettadressen din, som ethvert
nettsted.

**Hvor mye.** Hver levende kilde leses ved hver spørring, med jernbanens eget
intervall som standard (**Poll interval**, 15 til 600 sekunder), eller
sjeldnere der tabellen sier det. Der flere Live Track-moduler eller
jernbaner leser samme kilde, leser én felles klient den én gang for alle.
Målt 19. november 2026, 02:44 til 02:49 UTC:

| Jernbane | Levende data, én lesing | Ruteplan og linjer |
|---|---|---|
| Journey Beyond (Australia) | ingen: ingenting lastes ned | ingen: ruteplanen og linjene følger med integrasjonen |
| NSW TrainLink (Australia) | 124 kB fra to strømmer, høyst én gang hvert 55. sekund | 40 MB, ved endring, sjekkes daglig |
| Queensland Rail Travel (Australia) | listen, 5,5 kB, hvert 5. minutt; hvert gående togs tider, 6 til 8 kB, hvert 5. minutt | ingen: linjene følger med integrasjonen |
| V/Line (Australia) | 14 kB fra to strømmer | 58 MB (V/Lines del av Transport Victorias fil på 311 MB, lest alene), ved endring, sjekkes daglig |
| WA Trains (Australia) | ingen: det finnes ingen levende strøm | 28 MB, ved endring, sjekkes daglig |
| VR (Finland) | 1,4 kB komprimert for posisjonene; dagens tog, 0,5 MB komprimert første gang, deretter bare endringene, én gang i minuttet | 3,1 MB, hver dag |
| Irish Rail (Irland) | 0,2 kB, høyst én gang hvert 55. sekund | 6,6 MB, ved endring, sjekkes daglig; stasjonslisten, 46 kB, én gang i uken |
| NS, Arriva, Keolis (Nederland) | 1,5 kB, høyst én gang hvert 9. sekund; forsinkelser fra OVapi, 5,3 MB, hvert 5. minutt og bare ved endring | OVapis ruteplan, 267 MB, høyst én gang i uken og bare ved endring; NS' sporkart, 1,3 MB, hver dag |
| Vy, Go-Ahead Norge, SJ Nord (Norge) | Vy 510 kB fra to strømmer, Go-Ahead Norge 7 kB, SJ Nord 0,7 kB én gang i minuttet | Vy 67 MB, Go-Ahead Norge 20 MB, SJ Nord 26 MB, ved endring, sjekkes daglig |
| Renfe (Spain) | 2,1 kB fra to strømmer | 0,7 MB, hver dag; linjene følger med integrasjonen |
| Renfe Regionals (Catalunya) | 0,2 kB fra to strømmer som bærer alle Renfes lokale nett | 16 MB, hver dag |
| De svenske jernbanene (Sverige) | 474 kB første gang, deretter 5 til 9 kB endringer | ingen; stasjonslisten, 0,15 MB, hver dag; linjene følger med integrasjonen |
| VIA Rail (Canada) | 353 kB, sendt komprimert som 33 kB | 1,0 MB, én gang i uken |
| Amtrak (USA) | 1,2 MB, sendt komprimert som 113 kB | 18,6 MB, én gang i uken |
| Brightline (USA) | 1,3 kB fra to strømmer | 29 kB, én gang i uken |

⚠ Da dette ble målt, var det dag i Australia, kveld i Nord-Amerika og natt i
Europa. En levende strøm er minst om natten: på dagen er de europeiske
strømmene større enn tabellen viser.

**Etter en feil.** Togene fortsetter å bevege seg på siste gode data i
opptil 10 minutter; så merkes de som utilgjengelige til kilden svarer. En
ruteplan som ikke lar seg laste ned, prøves igjen senere, og kopien du har,
brukes videre. Hvis en leverandør fortsetter å avvise nøkkelen din i ti
minutter, ber Home Assistant om en ny.

**På disken.** Ruteplaner og linjetraseer lagres i Home Assistants mappe
`.storage` under navn som begynner med `saw_`, delt med de andre Live
Track-modulene som leser samme jernbane. Hvis du fjerner Live Track
Intercity Rail og ingen annen Live Track-modul bruker dem, kan du slette dem
for hånd.

---

## Hjelp den å vokse

Live Track Intercity Rail vokser fortsatt. Vi legger til baner og land når vi
finner dem, og vi vil vite hva du ønsker deg neste gang.

### Foreslå noe

Mangler landet eller banen din? Er noe feil, eller vanskelig å forstå? Si fra
på den måten som er enklest for deg:

* [**Fyll ut et kort skjema**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=nb.yml)
  på norsk. Du trenger en gratis GitHub-konto.
* **Send en e-post** til
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Ingen konto nødvendig.

Uansett hjelper det om du forteller oss:

* hva du vil se, og hvor i verden;
* en lenke til hvor dataene publiseres, hvis du kjenner til en (en side med
  åpne data, en offentlig strøm, en tjenestes nettsted): ikke nødvendig, men
  det hjelper;
* språket i Home Assistant, hvis problemet er ordlyden eller en
  oversettelse.

Skriv på engelsk eller på ditt eget språk, det som er enklest for deg.

### Legg det til selv, med vår hjelp

Hvis du vil legge til noe selv, hjelper vi deg, fra det første spørsmålet til
den ferdige versjonen. Du trenger ikke være utvikler for å begynne:

* **En oversettelse.** Ordene i oppsettdialogen er en kort liste med fraser i
  én tekstfil. Vi viser deg hvilken fil og hvilke linjer.
* **En ny bane.** Fortell oss hvor dataene publiseres. Vi kan skrive koden
  sammen, eller se over din.
* **Testing der du bor.** Installer den, se på din del av kartet, og fortell
  oss hva som stemmer og hva som ikke gjør det.
* **En rettelse av denne README-filen.** Hvis et trinn ikke stemte med det du
  så, fortell oss hva du så.

[**Fortell oss hva du har i tankene**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=nb.yml)
eller skriv til
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
så svarer vi med de neste trinnene.

---

## Språk

Denne README-filen: [English](README.md), [Deutsch](README.de.md), [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md), [Español](README.es.md),
[Italiano](README.it.md), [Dansk](README.da.md), [Suomi](README.fi.md), [Svenska](README.sv.md),
**Norsk bokmål**, [Gaeilge](README.ga.md). Hver oversatte README-fil er
fullstendig. Ingen er ennå lest av noen med språket som morsmål. Er norsk
morsmålet ditt, si gjerne fra om denne README-filen leses godt: se
[Hjelp den å vokse](#hjelp-den-å-vokse).

Oppsettdialogen og alternativene er foreløpig bare på engelsk, uansett språket i
Home Assistant. Snakker du et annet språk, kan du oversette dem selv: det er en
kort liste med setninger i én fil, og [vi hjelper deg med
det](#legg-det-til-selv-med-vår-hjelp).

Funnet en feil i en oversettelse, eller trenger du et annet språk? Si fra på
<https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues>,
eller [oversett med vår hjelp](#legg-det-til-selv-med-vår-hjelp).

---

## Kreditering og lisenser

Hver levende kilde leses mens den kjører, av Home Assistant; ingenting fra en
levende strøm ligger i dette kodelageret. Hvert tog oppgir kilden sin i
attributtet `attribution`. Hver kildes vilkår binder deg, som mottaker av
dataene.

* **Amtraker** (amtraker.com), som videresender Amtraks togsporing (USA):
  data under
  [Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/),
  kildehenvisning kreves. **Amtraks** egen ruteplan for linjetraseene.
* **Brightline** (USA): GTFS- og GTFS-Realtime-strømmene; Brightline
  publiserer ingen vilkår.
* **VIA Rail** (Canada): togstatusdataene, som VIA ikke publiserer vilkår
  for; ruteplanen under Open Government Licence - Canada 2.0
  ([developer resources](https://www.viarail.ca/en/developer-resources)).
* **Fintraffic / digitraffic.fi** (Finland): data under CC BY 4.0.
* **Transport for NSW** (Australia): data under CC BY 4.0
  ([datalisens](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australia): data under CC BY 4.0
  ([åpne data](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Queensland Rail Travel** (Australia): tidene som siden Service Updates
  viser, lest av Home Assistant; se
  [Queensland Rails opphavsrettsside](https://www.queenslandrailtravel.com.au/copyright).
  Ingenting fra Queensland Rail Travel følger med integrasjonen.
* **Journey Beyond** (Australia): de publiserte ruteplanene, overført til
  `data/journey_beyond_timetable.json`; Journey Beyond publiserer ingen
  vilkår for dem.
* **Kollektivtrafikkmyndigheten i Vest-Australia** (Public Transport
  Authority of Western Australia): ruteplandata tilgjengelig uten kostnad
  fra www.transperth.wa.gov.au
  ([spatial data access](https://www.transperth.wa.gov.au/About/Spatial-Data-Access);
  ikke CC BY).
* **Renfe** (Spania): data under CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)).
* **Entur** (Norge): inneholder data under Norsk lisens for offentlige data
  ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)) tilgjengeliggjort av
  Entur.
* **Trafikverket** (Sverige): data under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Irland): levende data; Irish Rail publiserer ingen vilkår.
  Ruteplan fra [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Irland), CC BY 4.0, som den er.
* **NS** (Nederland): kjøretøydata og sporkart, med din egen nøkkel, under
  vilkårene til [NS API portal](https://apiportal.ns.nl/). Ruteplan og
  forsinkelser fra [OVapi](https://gtfs.ovapi.nl/), CC0.
* **Filer som følger med i `data/`**: linjetraseer for Journey Beyond,
  Queensland Rail Travel, Renfe (Spain) og Sverige, bygget fra
  [OpenStreetMap](https://www.openstreetmap.org/copyright),
  © OpenStreetMap-bidragsytere, under
  [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/);
  endestasjonskommunene for Renfes turer (OpenStreetMap, ODbL 1.0) og
  folketallet deres (Wikidata-egenskap P1082, CC0, ellers OpenStreetMap);
  folketall for svenske endebyer fra Statistiska centralbyrån (SCB) og
  Trafikverket, begge CC0 1.0; folketall for norske endebyer fra Statistisk
  sentralbyrå, tabell 04859, CC BY 4.0.
* **Kartkortet** er [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, en kopi av [ha-map-card](https://github.com/nathan-gs/ha-map-card)
  av nathan-gs, MIT, som følger med i `frontend/`. Kartflisene og
  krediteringen av dem står i kortets README.

Ingen av disse organisasjonene har laget eller godkjent denne integrasjonen.

**Kode**: MIT, i [LICENSE](LICENSE). Filene i `data/` beholder kildenes
lisenser, listet ovenfor.

**For utviklere:** hver jernbane er én modul i
`custom_components/live_track_intercity_rail/operators/`, som leser en
kildeadapter i `sources/`; de medfølgende linjetraseene bygges på nytt med
skriptene i `tools/` (`journey_beyond.py`, `qrt_lines.py`,
`renfe_spain_lines.py`, `sweden_lines.py`). Testene kjøres med
`python -m unittest discover -s tests`.

---

## Søkeord

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

---

**Anerkjennelse.** StrausbergAutomationWorks anerkjenner urfolkene i alle land
og farvann som dette kartet dekker, over hele verden, og viser respekt for deres
eldste, før og nå.
