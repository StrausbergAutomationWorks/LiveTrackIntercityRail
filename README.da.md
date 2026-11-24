# Live Track Intercity Rail

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · **Dansk** · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · [Gaeilge](README.ga.md) · [Alle sprog](#sprog)

**Intercitytog til Home Assistant, på ét kort.** Live Track Intercity Rail
sætter hvert tog fra de intercity- og fjerntogsjernbaner, du vælger, på dit
Home Assistant-kort: hvor det er, dets nummer, om det er forsinket efter
jernbanens egen regel, og dets næste stop. Hver jernbane tilføjes for sig, ud
fra dens egne offentliggjorte data.

> **Live Track Intercity Rail er ét modul i Live Track**, en familie af Home
> Assistant-integrationer, der tegner alt, hvad der bevæger sig, og vejret, det
> bevæger sig igennem, på ét fælles kort: fly, skibe, tog og vejr. Installer
> det alene eller ved siden af de andre moduler
> ([liste nedenfor](#en-del-af-live-track-de-andre-moduler)).

> **I vækst, og åben for idéer.** Live Track Intercity Rail dækker i dag 33
> jernbaner i 9 lande på 3 kontinenter, og vi tilføjer flere jernbaner og
> lande. Mangler din? [Foreslå den](#hjælp-den-med-at-vokse), eller tilføj den
> selv: vi hjælper dig med det.

**Status: 0.1.3, udgivet.** I Markedspladsens katalog ([installér den
nedenfor](#installation-trin-for-trin)).

Originalt værk af StrausbergAutomationWorks. Ikke tilknyttet eller godkendt
af Amtrak, Amtraker, Brightline, VIA Rail, Fintraffic, VR, Transport for NSW,
NSW TrainLink, Transport Victoria, V/Line, Queensland Rail, Journey Beyond,
Public Transport Authority of Western Australia, Transwa, Renfe, Rodalies de
Catalunya, Entur, Vy, Go-Ahead Norge, SJ Nord, Trafikverket, SJ, VR
Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen,
Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget,
Värmlandstrafik, Tågab, Inlandsbanan, Irish Rail, National Transport
Authority (Irland), NS, Arriva, Keolis, OVapi eller nogen anden jernbane.

---

## Indhold

1. [Alt, hvad den gør](#alt-hvad-den-gør)
2. [Hvor den virker](#hvor-den-virker)
3. [En del af Live Track: de andre moduler](#en-del-af-live-track-de-andre-moduler)
4. [Før du begynder](#før-du-begynder)
5. [Installation, trin for trin](#installation-trin-for-trin)
6. [Opsætning, trin for trin](#opsætning-trin-for-trin)
7. [Gratis nøgler, der slår mere til, trin for trin](#gratis-nøgler-der-slår-mere-til-trin-for-trin)
8. [Sæt kortet på et dashboard](#sæt-kortet-på-et-dashboard)
9. [Brug den i automatiseringer](#brug-den-i-automatiseringer)
10. [Alt på kortet i detaljer](#alt-på-kortet-i-detaljer)
11. [Alle entiteter, den opretter](#alle-entiteter-den-opretter)
12. [Hvad den sender og henter](#hvad-den-sender-og-henter)
13. [Hjælp den med at vokse](#hjælp-den-med-at-vokse)
14. [Sprog](#sprog)
15. [Tak og licenser](#tak-og-licenser)
16. [Nøgleord](#nøgleord)

---

## Alt, hvad den gør

### På kortet, uden at du skal sætte noget op

Du tilføjer en **jernbane**: du vælger et land og derefter en af dets
intercityjernbaner. Alt nedenfor vises så for den jernbane. Tilføj
integrationen igen for hver anden jernbane, du vil have.

| Hvad | Hvor | Fra |
|---|---|---|
| **Tog i drift**: én markør pr. tog, med togets nummer eller linje som etiket, i jernbanens egne farver, drejet i den retning, det kører | hver jernbane | hver jernbanes egne offentliggjorte data |
| **Forsinkelse**: et tog vises som forsinket eller meget forsinket efter jernbanens egen regel; hvor en jernbane ikke offentliggør nogen regel, efter hvor langt toget kører | hver jernbane, der melder forsinkelser | hver jernbanes eget feed |
| **Næste stop og tidspunktet**: den station, toget standser ved som det næste, og hvornår det ventes der | hver jernbane, hvis feed eller køreplan siger det | hver jernbanes eget feed og køreplan |
| **Tog, der følger sporet**: mellem to meldinger kører et tog langs sin egen linje med sin seneste fart, ikke i lige linje | hver jernbane, hvis linje er kendt | hver jernbanes køreplan, eller linjer, der følger med integrationen |
| **Tog fra køreplanen**: hvor en jernbane ikke offentliggør positioner, placeres hvert tog på sin linje efter sine tider og markeres som et skøn | Journey Beyond, Queensland Rail Travel og WA Trains (Australien), SJ Nord (Norge); Irish Rail med sin seneste forsinkelse | hver jernbanes køreplan eller tider |
| **Billeder for nogle tog**: Julemandens ekspres og et sommerhus (Finland), dyrene fra Journey Beyonds tog, et billede for hver af Queensland Rail Travels linjer | Finland, Australien | tegnet til denne integration |
| **Holder ved grænsen**: et tog, der holder ved en grænseovergang mellem USA og Canada, viser "Customs" i stedet for sin forsinkelse | Amtraks tog til og fra Canada | Amtraks positioner |
| **Én optælling pr. jernbane**: tog i drift | hver jernbane | de samme data |

### Slået til med din egen gratis nøgle eller konto

| Gratis nøgle eller konto | Hvad den tilføjer |
|---|---|
| Nøgle fra **Transport for NSW Open Data** | NSW TrainLinks regionaltog (New South Wales, Australien) |
| Nøgle fra **Transport Victoria Open Data** | V/Lines fjerntog (Victoria, Australien) |
| Nøgle fra **NS' API-portal** | NS Intercity samt Arrivas og Keolis' regionaltog (Nederlandene); én nøgle gælder for alle tre |
| Nøgle fra **Trafikverket** | de 15 svenske jernbaner; én nøgle gælder for alle femten |

Hver nøgle tager et par minutter at få: [trin for trin nedenfor](#gratis-nøgler-der-slår-mere-til-trin-for-trin).
De øvrige 13 jernbaner kræver ingen nøgle.

---

## Hvor den virker

| Region | Hvad du får | Fra | Kræver |
|---|---|---|---|
| **Australien**: hele landet | Journey Beyond: The Ghan, The Ghan Expedition, Indian Pacific, Great Southern, The Overland, kun fra køreplanen ([hvorfor](#journey-beyond-australien)) | Journey Beyond | intet |
| **Australien**: New South Wales | NSW TrainLinks regionaltog (XPT og Xplorer), også ind i Queensland, Victoria og Australian Capital Territory | Transport for NSW | en gratis nøgle |
| **Australien**: Queensland | Queensland Rail Travel: Spirit of Queensland, Spirit of the Outback, Tilt Train, Westlander, Inlander, Kuranda Scenic Railway, Gulflander, ud fra deres offentliggjorte tider ([hvorfor](#queensland-rail-travel-australien)) | Queensland Rail Travel | intet |
| **Australien**: Victoria | V/Lines fjerntog (nærbanelinjerne er i Live Track Commuter Rail), også ind i New South Wales | Transport Victoria | en gratis nøgle |
| **Australien**: Western Australia | WA Trains: Australind, Prospector, MerredinLink og AvonLink, kun fra køreplanen ([hvorfor](#wa-trains-western-australia-australien)) | Public Transport Authority of Western Australia | intet |
| **Europa**: Finland | VR's fjerntog | Fintraffic Digitraffic | intet |
| **Europa**: Irland | Irish Rails InterCity-tog, og Enterprise fra Dublin til Belfast (Storbritannien) | Irish Rail, National Transport Authority | intet |
| **Europa**: Nederlandene | NS Intercity samt regionaltogene fra Arriva (Arriva, RRReis, Blauwnet) og Keolis (Blauwnet, RRReis); NS' Sprinter-tog er i Live Track Commuter Rail | NS, OVapi | en gratis nøgle |
| **Europa**: Norge | Vys F-, RE-, RX- og R-linjer (F1 også ind i Sverige), Go-Ahead Norges F5 og R50, SJ Nords F6, F7 og R60 til R75 | Entur | intet |
| **Europa**: Spanien | Renfes AVE-, Avlo-, Alvia-, Avant-, Euromed-, Intercity-, MD- og Regional-tog, også ind i Frankrig og Portugal; Rodalies de Catalunyas regionallinjer R11 til R17 | Renfe | intet |
| **Europa**: Sverige | SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget, Värmlandstrafik, Tågab og Inlandsbanan, hver som sin egen jernbane; Öresundståg også ind i Danmark | Trafikverket | en gratis nøgle |
| **Nordamerika**: Canada | VIA Rail, alle ruter | VIA Rail | intet |
| **Nordamerika**: USA | Amtrak, alle ruter, også ind i Canada | Amtraker | intet |
| **Nordamerika**: USA | Brightline (Florida) | Brightline | intet |

Står det ikke på listen? [Fortæl os det](#hjælp-den-med-at-vokse). Hvor
nogen offentliggør dataene åbent, ser vi på at tilføje det.

⚠ **Et tog er kun så godt som dets jernbanes data.** Nogle jernbaner melder et
tog med få sekunders mellemrum, nogle med få minutters mellemrum, nogle kun når
det passerer signaler, og nogle offentliggør slet ingen positioner. Hver
jernbanes begrænsninger står under
[Alt på kortet i detaljer](#alt-på-kortet-i-detaljer).

⚠ **Det er ikke jernbanens officielle information.** Tjek jernbanens egen app
eller hjemmeside, før du rejser.

---

## En del af Live Track: de andre moduler

Live Track er en række Home Assistant-integrationer, én for hver slags ting,
der bevæger sig, alle tegnet på det samme kortkort. Hver virker for sig;
sammen giver de ét levende billede. De deler kortkortet og et Python-bibliotek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
så installerer du endnu et modul, kommer der ingen ekstra forespørgsler til en
kilde, som et andet allerede læser.

| Modul | Hvad det sætter på kortet | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | fly over dig via ADS-B, med ruter og typeikoner | udgivet |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | skibe og både via AIS, nær dig eller hvor som helst | udgivet |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | nærbanetog i Nordamerika, Europa og Australien | udgivet |
| **Live Track Intercity Rail** | intercity- og fjerntog i Nordamerika, Europa og Australien (dette modul) | udgivet |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | fly og skibe fra udlændinge- og føderale ordensmyndigheder, fra offentlige lister | udgivet |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | vejr, storme og naturfarer | udgivet |
| Live Track Stations | afgangstavler og "tid til at gå"-påmindelser for hver station | planlagt |
| Live Track Satellites | satellitter, der passerer over dig | planlagt |
| Live Track Freight Trains | gods- og arbejdstog, hvor jernbaner offentliggør dem | planlagt |
| Live Track Transit | bybusser, sporvogne, færger og metro | planlagt |
| Live Track Intercity Buses | fjern- og regionalbusser | planlagt |
| Live Track Commuter Buses | pendlerbusser | planlagt |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | det fælles kortkort, som hvert modul tegner på | udgivet, installeres med hvert modul |

Alt er gratis og open source. Intet holdes tilbage til sponsorer.

---

## Før du begynder

* **Home Assistant** 2026.11 eller nyere.
* **Markedspladsen** (HACS) i din Home Assistant, så du kan installere og
  opdatere den på den nemme måde. Uden den kan du kopiere filerne i hånden.
* **Internetadgang** for Home Assistant: hvert tog kommer fra dets jernbanes
  egne offentliggjorte data.
* **Valgfrit: auto-entities** fra Markedspladsen, til at sætte markørerne på
  kortet (se [Sæt kortet på et dashboard](#sæt-kortet-på-et-dashboard)).
* Intet at betale. 13 af de 33 jernbaner kræver ingen konto; de øvrige 20
  kræver din egen gratis nøgle, og fire nøgler dækker dem alle
  ([ovenfor](#slået-til-med-din-egen-gratis-nøgle-eller-konto)).
* Home Assistant installerer selv de Python-pakker, den har brug for
  (`saw-livetrack`, `gtfs-realtime-bindings` og `tzdata`), første gang
  integrationen indlæses.

---

## Installation, trin for trin

### Fra Markedspladsen (anbefalet)

1. Åbn **Indstillinger → Markedspladsen** (HACS) i Home Assistant.
2. Søg efter **Live Track Intercity Rail**, og åbn den.
3. Vælg **Download** (eller **Installér**).
4. **Genstart Home Assistant**: **Indstillinger → System → Reparationer**
   tilbyder genstarten, eller brug **Indstillinger → System → Genstart**.

Hvis søgningen ikke finder den, så tilføj den via dens link: vælg **Tilføj fra
link** (eller menuen med de tre prikker → **Brugerdefinerede repositorier**),
skriv `StrausbergAutomationWorks/LiveTrackIntercityRail`, vælg **Integration**,
hvis du bliver spurgt om typen, og fortsæt derefter fra trin 3.

Markedspladsen tilbyder derefter hver ny udgivelse som en opdatering.

### I hånden

1. Hent kildekoden til den
   [seneste udgivelse](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/releases/latest).
2. Kopiér dens mappe `custom_components/live_track_intercity_rail` ind i
   mappen `custom_components` i din Home Assistants konfigurationsmappe (opret
   `custom_components`, hvis den ikke findes).
3. Genstart Home Assistant.

For at opdatere i hånden erstatter du mappen med den nye udgivelses mappe og
genstarter.

---

## Opsætning, trin for trin

1. Åbn **Indstillinger → Enheder & tjenester**.
2. Vælg **Tilføj integration** (nederst til højre), og søg efter **Live Track
   Intercity Rail**.
3. **Region** (region): vælg jernbanens land. Kun lande med mindst én jernbane
   står på listen. Vælg **Indsend**.
4. **Railroad** (jernbane): vælg jernbanen. Vælg **Indsend**.
5. **API key** (API-nøgle): kun for NSW TrainLink, V/Line, de tre
   nederlandske jernbaner og de femten svenske jernbaner. Indsæt din nøgle
   ([sådan får du en](#gratis-nøgler-der-slår-mere-til-trin-for-trin)), og
   vælg **Indsend**. De øvrige jernbaner springer dette trin over.

Det er det hele. Togene vises inden for et minut eller to. Hvor en jernbanes
linjer kommer fra dens køreplan, begynder togene at følge deres linjer, så
snart køreplanen er hentet, hvilket første gang kan tage et par minutter. For
at følge en anden jernbane tilføjer du integrationen igen. Den samme jernbane
to gange afvises.

### Skift, hvad den viser: indstillingerne

Åbn **Indstillinger → Enheder & tjenester → Live Track Intercity Rail →
Konfigurér** (tandhjulet) på den jernbane, du vil ændre. Der er én
indstilling:

| Indstilling | Hvad den gør | Standard |
|---|---|---|
| **Poll interval** (hentningsinterval) | hvor ofte jernbanens kilde læses, 15 til 600 sekunder. Et kortere interval end kildens egen opdatering viser ikke mere | efter jernbane: 15 sekunder for Renfe (Spain) og de tre nederlandske jernbaner; 60 sekunder for Brightline, NSW TrainLink, Irish Rail og SJ Nord; 30 sekunder for de øvrige |

---

## Gratis nøgler, der slår mere til, trin for trin

Tyve jernbaner beder hver bruger om deres egen nøgle, fra fire udbydere. Hver
af disse nøgler er gratis, og hver person, der installerer Live Track
Intercity Rail, får sin egen. Du indsætter nøglen, når opsætningsdialogen beder
om den ([trin 5 ovenfor](#opsætning-trin-for-trin)). Der spørges kun om
nøglen: ingen adgangskode og ingen hemmelighed. Nøglen gemmes i Home Assistant
sammen med integrationen, sendes kun til sin egen udbyder og skrives aldrig i
loggen. Hvis udbyderen afviser den i ti minutter, beder Home Assistant dig om
en ny.

### Transport for NSW (NSW TrainLink, New South Wales, Australien)

1. Åbn <https://opendata.transport.nsw.gov.au/>, vælg **Register**, opret en
   konto, og log ind.
2. Vælg ikonet for din brugerprofil og derefter **API Tokens**.
3. Skriv et navn til nøglen, og vælg **CREATE API TOKEN**. Kopiér nøglen med
   det samme: siden viser den kun én gang.
4. Indsæt den i **API key**, når du tilføjer NSW TrainLink. Indsæt kun
   nøglen: Live Track Intercity Rail sætter selv ordet `apikey` foran.

### Transport Victoria (V/Line, Victoria, Australien)

1. Åbn <https://opendata.transport.vic.gov.au/>, vælg **Login** og derefter
   **Sign up**.
2. Udfyld dine oplysninger, og vælg **Create Account**. Skriv koden fra den
   e-mail, du modtager, og vælg **Confirm**.
3. Portalen beder om en godkendelsesapp på din telefon: scan QR-koden med den,
   skriv appens kode, og vælg **Confirm**. Log derefter ind med din e-mail,
   din adgangskode og appens kode.
4. Vælg **My Account** → **Profile** → **API tokens**. Din nøgle står der
   allerede. Indsæt den i **API key**, når du tilføjer V/Line.

### NS (NS, Arriva og Keolis, Nederlandene)

1. Åbn <https://apiportal.ns.nl/>, vælg **Inloggen** (log ind) og derefter
   **Externe bezoeker** (ekstern besøgende).
2. Udfyld formularen, og send den. En e-mail bekræfter registreringen. Det kan
   tage op til 5 minutter, før API'erne vises i portalen.
3. Åbn siden for **Virtual Train API** (NS' togpositioner). Under **Related
   Products** åbner du dens produkt, giver dit abonnement et navn og vælger
   **Subscribe**.
4. Når NS har godkendt abonnementet, står din nøgle på din profilside. Indsæt
   den i **API key**, når du tilføjer NS, Arriva eller Keolis. Én nøgle
   gælder for alle tre.

### Trafikverket (de 15 svenske jernbaner)

1. Åbn <https://data.trafikverket.se/oauth2/Account/register>.
2. Udfyld **Email**, **Displayname** (visningsnavn), **Password**
   (adgangskode) og **Confirm password**, sæt hak i **Accept license and
   Agreement**, og vælg **Register**.
3. Åbn <https://data.trafikverket.se/get-started>, og vælg **Create key** under
   **Create a key**. Log ind med den konto, du oprettede, og opret nøglen.
4. Indsæt den i **API key**, når du tilføjer en svensk jernbane. Én nøgle
   gælder for alle femten.

---

## Sæt kortet på et dashboard

Kortet er [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
det kort, som hvert Live Track-modul tegner på. **Det installeres med Live
Track Intercity Rail**: intet at hente, intet at kopiere, ingen ressource at
tilføje.

1. Åbn et dashboard, vælg blyanten (**Redigér betjeningspanel**) og derefter
   **Tilføj kort**.
2. Rul helt ned, og vælg **Manuel**.
3. Indsæt dette, og vælg **Gem**:

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

Denne form kræver [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
fra Markedspladsen. Har du andre Live Track-moduler installeret, så tilføj et
filter `- domain: geo_location` mere for hver af deres kilder
(`live_track_commuter_rail`, `live_track_aircraft` og så videre).

**Uden auto-entities:** LiveTrackMapCard kan selv vælge, hvad den viser, med
`entity_filter`. Indsæt dette i stedet; der skal ikke installeres mere:

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

Andre Live Track-moduler kommer i `entity_filter` på samme måde: én regel
`- domain: geo_location` mere for hver kilde.

**På kortet:**

* Hvert tog er en markør i sin jernbanes farver, med sit tognummer eller sin
  linje som etiket. Amtraks tog er stjerner, VIA Rails bærer ahornbladet, Irish
  Rails InterCity-tog er kløverblade, og nogle tog er billeder (hver jernbane
  nedenfor siger hvilke).
* På de fleste jernbaner bytter farverne om med retningen: på én måde ud fra
  den største by, på den anden måde ind mod den.
* En pil viser den retning, toget kører. Et tog, der holder stille, beholder
  sin seneste retning. Billeder står oprejst og har ingen pil.
* **Peg på** et tog for at se dets jernbane, nummer, linje og strækning.
  **Klik** på det for at se alle detaljerne, også dets næste stop og dets
  forsinkelse.

Hvis dine dashboards' ressourcer sættes i YAML (`lovelace: resource_mode: yaml`),
kan intet registreres for dig: en meddelelse under **Reparationer** giver så de
præcise linjer, du skal tilføje i `configuration.yaml`. De ser sådan ud, med
integrationens egen adresse i stedet for pladsholderne:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_intercity_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Hvert Live Track-modul har en kopi af kortet og registrerer den, når Home
Assistant starter. Sammen holder de præcis én række i **Indstillinger →
Betjeningspaneler → Ressourcer**: den nyeste kortversion, som et af dem har,
aldrig en ældre. Et kort, du selv har installeret via Markedspladsen, lades i
fred. Når du fjerner dette moduls sidste jernbane, går rækken videre til et
andet Live Track-modul, eller den fjernes, hvis der ikke er flere. Hvis
integrationens filer fjernes, mens dens jernbaner stadig er sat op, og intet
andet Live Track-modul er installeret, så fjern selv rækken i **Indstillinger
→ Betjeningspaneler → Ressourcer**.

**Vil du hellere installere kortet i hånden**, så følg trinene i
[kortets README](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
En række, du selv har lavet til en kopi under `/local/` eller på en anden
adresse, bliver aldrig ændret eller fjernet. Så længe den indlæser kortet,
overlader alle Live Track-moduler kortet til den, også når et modul har en nyere
udgivelse, og intet under **Reparationer** gør opmærksom på det. Vil du tilbage
til modulets kopi, så fjern din række under **Indstillinger → Betjeningspaneler
→ Ressourcer**, og genstart Home Assistant. Sletter du filen til din kopi, så
fjern også dens række: så længe en række, hvis fil er væk, bliver stående,
tilføjer modulet ingen række af sin egen.

Ethvert andet kort, der viser `geo_location`-entiteter, viser også togene,
som almindelige markører.

---

## Brug den i automatiseringer

Alt er almindelige Home Assistant-entiteter, så automatiseringseditoren
arbejder med dem, uden kode.

**En notifikation på telefonen, når din jernbanes data stopper** (togene
forsvinder så fra kortet):

1. **Indstillinger → Automatiseringer & scener → Tilføj automatisering →
   Opret ny automatisering**.
2. **Når**: **Tilføj udløser** → **Entitet** → **Tilstand ændres**. Vælg
   jernbanens entitet **Trains in service** (tog i drift), og vælg under
   **Til (valgfrit)** **Utilgængelig**.
3. **Så gør**: **Tilføj handling**, søg efter din telefons notifikationshandling
   (den bærer din telefons navn), og skriv en besked, for eksempel:

   ```text
   Ingen intercitytog på kortet: jernbanens data er stoppet
   ```

4. **Gem**.

**Andre idéer:** en lampe, der tænder, når et Amtrak-tog er inden for 2 km
(1,2 miles) af dit hjem i USA, ud fra markørernes afstand; en optælling på
dashboardet af de tog, VR kører i Finland i løbet af dagen; en besked, når
Queensland Rail Travels første tog på dagen kører (Australien), ud fra **Trains
in service**, der stiger over 0.

---

## Alt på kortet i detaljer

### Tog

Hvert tog er én markør. Dens tilstand er dens afstand fra dit hjem, i
kilometer. Markøren vises, når jernbanen melder toget, eller når dets køreplan
siger, at det kører, og fjernes, når toget forsvinder fra jernbanens data,
eller dets tur er slut.

* **Mellem to meldinger** kører et tog langs sin egen linje mod sit næste
  stop: med den fart, jernbanen melder, eller, hvor den ikke melder nogen, med
  farten mellem dets to seneste meldinger. Det kører aldrig forbi sit næste
  stop, og det holder op med at bevæge sig 30 minutter efter den seneste
  melding. Et tog på en kendt linje tegnes på linjen; jernbanens egen melding
  gemmes ved siden af.
* **Hvis en jernbanes data svigter**, bliver dens tog ved med at køre på deres
  seneste gode melding i op til 10 minutter. Derefter er de utilgængelige og
  forsvinder fra kortet, indtil dataene kommer tilbage.
* **Forsinket og meget forsinket**: hvor jernbanen offentliggør sin egen regel
  for et forsinket tog, bruger integrationen den. Hvor den ikke offentliggør
  nogen, er et tog forsinket efter, hvor langt det kører, med tærsklerne fra
  Amtrak Status Maps (asm.transitdocs.com). Hver jernbane nedenfor siger
  hvilken.

På hvert tog: `marker_label`, `train`, `line_name`, `observed_at` (hvornår dets
melding var sand), `course_deg` (mens det kører), `next_stop` og
`arrival_estimated_at` (hvor de kendes), `delay_min`, `late_threshold_min` og
`very_late_threshold_min`, `speed_kmh` (hvor jernbanen melder den),
`attribution`, og mellem to meldinger `previous_latitude`,
`previous_longitude`, `previous_observed_at` og `segment_duration_s`. Et tog,
der flyttes langs sin linje, har `position_source: estimated`, med jernbanens
melding i `fix_latitude` og `fix_longitude`.

### Journey Beyond (Australien)

⚠ **Journey Beyond offentliggør ingen positioner.** Hvert tog tegnes ud fra
dets offentliggjorte køreplan, skrevet af i en fil, der følger med
integrationen (afgange til 29. december 2027), så intet hentes. Hvert tog
placeres på sin linje efter sine tider, markeret som et skøn, uden
forsinkelse: et forsinket eller aflyst tog tegnes stadig til tiden. Hver
forbindelse er sit eget billede (kamelen med rytter, en fugl, en kænguru, en
emu), i sine farver på udturen og byttet om på hjemturen, uden etiket: peg på
det for at se toget og dets tur.

### NSW TrainLink (New South Wales, Australien)

Fra Transport for NSW's NSW TrainLink-feed, med din egen nøgle, en ny position
cirka én gang i minuttet. Etiketten er tognummeret. NSW-orange med en hvid
ring ud fra Sydney, byttet om ind mod byen. Feedet har ingen fart, så et tog
kører langs sin linje med farten mellem dets to seneste positioner. Forsinket
fra 11 minutter (NSW TrainLink regner et tog for rettidigt inden for 10
minutter), meget forsinket fra 30.

### Queensland Rail Travel (Australien)

⚠ **Queensland Rail Travel offentliggør ingen positioner.** Din Home Assistant
læser de tider, som Queensland Rail Travels side Service Updates viser: listen
over dagens tog højst hvert 5. minut, og hvert togs tider højst hvert 5.
minut fra 30 minutter før afgang til 15 minutter efter ankomst. Hvert tog
placeres på sin linje efter de tider og markeres som et skøn. Hver linje er
sit eget billede, i sine farver ud fra Brisbane og byttet om ind mod byen,
med tognummeret i et mærke ved siden af. Forsinket eller meget forsinket vises
ikke.

### V/Line (Victoria, Australien)

Fra Transport Victorias V/Line-feed, med din egen nøgle: fjerntogslinjerne til
Albury, Ararat, Bairnsdale, Echuca, Maryborough, Shepparton, Swan Hill og
Warrnambool. Etiketten er tognummeret. V/Line-lilla med en gul ring ud fra
Melbourne, byttet om ind mod byen. Feedet har ingen fart, så et tog kører med
farten mellem dets to seneste positioner; efter 10 minutter uden ny position
tidsberegnes det frem til næste stop. Forsinket fra 11 minutter på de lange
linjer og 6 på de korte (V/Lines egen liste), meget forsinket fra 30.

### WA Trains (Western Australia, Australien)

⚠ **Der offentliggøres ingen live-positioner.** Hvert tog tegnes ud fra Public
Transport Authority of Western Australias køreplan: placeret langs sin linje
efter sine planlagte tider, markeret som et skøn, uden forsinkelse.
Køreplanen tjekkes én gang om dagen. Etiketten er rutens tre første bogstaver:
AUS (Australind, lilla), PRO (Prospector, orange), MER (MerredinLink, grøn)
og AVO (AvonLink, grøn), ens i begge retninger.

### VR (Finland)

Fra Fintraffics Digitraffic, en ny position cirka hvert 30. sekund. Etiketten
er togtypen og nummeret, som VR skriver det (`IC 23`). VR-grøn med en mørk
ring ud fra Helsinki, byttet om ind mod byen. Dataene har ingen retning, så
pilen følger linjen. Forsinket fra 6 minutter (VR regner et tog for forsinket,
når det er mere end fem minutter forsinket), meget forsinket fra 12.

* **Julemandens ekspres**, fra første søndag i advent til 6. januar: en
  snemand på vej nordpå, et rensdyr på vej tilbage, uden nummer. Fra 12
  minutters forsinkelse vender figuren sig om med få sekunders mellemrum.
* **Sommerhuset**, fra sankthansaften til 31. juli: hvert af VR's fjerntog
  tegnes som et sommerhus, med sit nummer ved siden af.

### Irish Rail (Irland)

Fra Irish Rails live-trafik og National Transport Authoritys køreplan. ⚠ Irish
Rail melder kun et tog, når det passerer signalpunkter, der ligger nogle
minutter fra hinanden, så hvert tog tegnes ud fra sin køreplan og sin seneste
forsinkelse, flyttet langs sin strækning. Etiketten er tognummeret uden
bogstav (A700 viser 700). Et InterCity-tog er et grønt kløverblad med orange
kant og nummer ud fra Dublin, med farverne byttet om ind mod byen. Enterprise
er en sølvskive med en rød yderring, et magenta bånd og et magenta nummer; mod
Dublin er skiven magenta. Forsinket fra 10 minutter (National Transport
Authoritys regel), meget forsinket fra 20.

### NS, Arriva og Keolis (Nederlandene)

Fra NS' køretøjsdata, med din egen nøgle, en ny position cirka hvert 10.
sekund. Dette feed melder togets egen fart og retning, og begge bliver givet
videre. Næste stop og forsinkelsen kommer fra OVapis køreplan; sporet er NS'
eget kort over sine linjer, hentet én gang om dagen. Etiketten er
tognummeret. NS' tog er gule med en NS-blå ring; Arrivas og Keolis' tog har
indtil videre kortkortets eget udseende. Forsinket fra 3 minutter (NS' egen
definition), meget forsinket fra 10.

### Vy, Go-Ahead Norge og SJ Nord (Norge)

Fra Entur, hver jernbane sin egen post. Etiketten er linjekoden (F4, RE10,
R50). Linjens egen farve med en hvid ring ud fra Oslo S (på en tur, der ikke
når Oslo S, dens største endeby), byttet om ind mod den. Entur offentliggør
hverken fart eller retning, så et tog kører med farten mellem dets to seneste
positioner, og pilen følger dets linje. I Oslos lange tunneler flyttes et tog,
hvis positioner stopper, langs sin linje, indtil de kommer tilbage. ⚠ **SJ
Nord offentliggør ingen positioner:** hvert af dets tog placeres på sin linje
efter sine forventede tider. Forsinket fra 4 minutter, og fra 6 på F-linjerne
og linjerne til Göteborg (Sverige), Bane NOR's og Vys regel; meget forsinket
ved det dobbelte.

### Renfe (Spain) og Renfe Regionals (Catalunya, Spanien)

**Renfe (Spain)** læser Renfes fjerntogsfeed, en ny position cirka hvert 15.
sekund. Etiketten er tognummeret; tjenesten (AVE, Avlo, Alvia og så videre)
står i boksen, når du peger. AVE marineblå, Avlo turkis, alle andre tjenester
Renfe-lilla, hver udfyldt ud fra Madrid (på en tur, der ikke når Madrid, dens
største endeby) og byttet om ind mod byen. Renfe offentliggør ingen
rutelinjer, så linjerne er bygget ud fra OpenStreetMap og følger med
integrationen. Renfe offentliggør ingen regel for et forsinket tog, så et tog
er forsinket efter turens længde: fra 10 minutter op til 400 km (250 miles),
15 op til 560 km (350 miles), 20 op til 725 km (450 miles), 25 op til 885 km
(550 miles), 30 derover; meget forsinket ved det dobbelte.

**Renfe Regionals (Catalunya)** tegner Rodalies de Catalunyas regionallinjer
R11 til R17. Etiketten er tognummeret, i linjens egen farve, udfyldt ud fra
Barcelona og byttet om ind mod byen. Uden for Barcelona er en position den
seneste station, toget passerede, så toget tidsberegnes mellem stationerne med
køreplanen og sin forsinkelse. Forsinket fra 10 minutter, meget forsinket fra
20, efter den længste linjes længde. Med begge Renfe-jernbaner sat op tegnes
hvert tog én gang.

### De svenske jernbaner (Sverige)

Fra Trafikverket, med din egen nøgle (én nøgle til alle femten). Etiketten er
tognummeret på billetten; mærket, nummeret og endestationerne står i boksen,
når du peger. Hvert mærke har sine egne farver, byttet om mod Stockholm C (på
en tur, der ikke når Stockholm C, dens største endeby). Trafikverket giver en
fart på cirka halvdelen af sine positioner; de øvrige tog kører med farten
mellem deres to seneste positioner. Sverige offentliggør ingen rutelinjer, så
linjerne er bygget ud fra OpenStreetMap og følger med integrationen. Forsinket
fra 6 minutter (Trafikverket regner et tog for rettidigt op til 5 minutter og
59 sekunder), meget forsinket fra 12.

### VIA Rail (Canada)

Fra VIA Rails egne togstatusdata. Hvert tog er en skive med ahornbladet og et
bånd i farven for dets rutegruppe (Atlantic, Western, Ontario og Quebec,
Prince Rupert, Churchill, Sudbury til White River, Montréal scenic), med
tognummeret i et oprejst mærke. Ulige numre har en gul skive, lige numre en
skive i båndets farve. Et tog uden ny position kører mod sit næste stop, så
det ankommer til VIA's eget skøn. VIA offentliggør ingen regel for et
forsinket tog, så et tog er forsinket fra 10 minutter på korridoren Québec
City til Windsor og fra 60 andre steder (Amtrak Status Maps' værdier for VIA),
meget forsinket ved det dobbelte.

### Amtrak (USA)

Amtrak offentliggør ingen åbne live-data. Amtraker videregiver Amtraks egen
togsporing, med en ny position hvert 3. til 5. minut, og integrationen flytter
hvert tog langs sin linje med den fart, Amtrak melder. Hvert tog er en stjerne
med sit nummer hen over, i sin rutes farver (de nordøstlige ruter, Cascades,
Pacific Surfliner, Acela og flere), ellers flagstjernen. Maple Leaf (New York
til Toronto) skifter langsomt mellem Amtraks stjerne og VIA's emblem. Et tog,
der holder ved grænsen ved Lacolle, Rouses Point eller Niagara Falls, viser
"Customs" i stedet for sin forsinkelse. Forsinket fra 16 minutter (Amtrak
regner et tog for rettidigt inden for 15 minutter), meget forsinket fra 30.
Det samme tognummer kan køre på to eller tre dage på én gang, så hver tur er
sin egen markør.

### Brightline (USA)

Fra Brightlines eget feed, en ny position cirka hvert 60. sekund. Etiketten er
turnummeret, i sort med hvid kant, på en skive i farven for togets
bestemmelsessted, med en sort ring. En position, der er mere end 5 minutter
gammel, bruges ikke. Feedet har ingen fart, så et tog kører med farten mellem
dets to seneste positioner. Brightline offentliggør ingen regel for et
forsinket tog, så et tog er forsinket fra 10 minutter, meget forsinket fra 20,
efter turens længde.

---

## Alle entiteter, den opretter

For hver jernbane:

| Entitet | Hvad den er |
|---|---|
| `sensor.<jernbane>_trains_in_service` | **Trains in service** (tog i drift): hvor mange tog jernbanen kører på kortet lige nu. For Amtrak: `sensor.amtrak_trains_in_service` |
| `geo_location.<jernbane>_train_…` | én pr. tog (`geo_location.amtrak_train_5_17`); den kommer og går med toget. Hver har `source: live_track_intercity_rail`, og dens tilstand er dens afstand fra dit hjem i kilometer |

En markørs entitets-ID kommer fra jernbanen og turen, aldrig fra dens etiket:
`geo_location.amtrak_train_5_17` er Amtraks tog 5, der kørte den 17. i
måneden, så et tog beholder det samme entitets-ID hele turen, og en anden tur
med det samme nummer får sit eget. Markøren fjernes, når turen forsvinder fra
jernbanens data eller slutter. Markørerne har intet unikt ID, ligesom ingen
Live Track-kortmarkør har, så de kan ikke omdøbes, skjules eller tildeles et
område i brugerfladen. Sensoren har et unikt ID og kan omdøbes.

Attributter, der ændrer sig ved hver hentning, markørernes positioner og
tider, gemmes i Home Assistants historik, som for enhver entitet. Sensoren har
ingen attributter, så den koster lidt at gemme, og den er optegnelsen over,
hvor mange tog der kørte på en dag. For at holde markørerne ude af historikken
tilføjer du dette i `configuration.yaml` og genstarter:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_train_*
```

Har din `configuration.yaml` allerede en `recorder:`-sektion, så tilføj kun
mønstret `geo_location.*_train_*` til den, under `exclude:` og
`entity_globs:`. Mønstret rammer kun dette moduls togmarkører. Et kort, der er
sat til at tegne historik, har så intet spor at tegne.

---

## Hvad den sender og henter

**Om din placering.** Intet. Dit hjems position bruges kun inde i din Home
Assistant, til at give hvert togs afstand. Din nøgle, hvor en jernbane kræver
en, sendes kun til den jernbanes udbyder. Intet andet om dig sendes nogen
steder hen. Hver tjeneste ser din internetadresse, som enhver hjemmeside gør.

**Hvor meget.** Hver live-kilde læses ved hver hentning, som standard med
jernbanens eget interval (**Poll interval**, 15 til 600 sekunder), eller
sjældnere, hvor tabellen siger det. Hvor flere Live Track-moduler eller
jernbaner læser den samme kilde, læser én fælles klient den én gang for dem
alle. Målt den 19. november 2026, 02:44 til 02:49 UTC:

| Jernbane | Live-data, én læsning | Køreplan og linjer |
|---|---|---|
| Journey Beyond (Australien) | intet: der hentes intet | intet: køreplanen og linjerne følger med integrationen |
| NSW TrainLink (Australien) | 124 KB fra to feeds, højst én gang hvert 55. sekund | 40 MB, når den ændres, tjekket dagligt |
| Queensland Rail Travel (Australien) | listen, 5,5 KB, hvert 5. minut; hvert kørende togs tider, 6 til 8 KB, hvert 5. minut | intet: linjerne følger med integrationen |
| V/Line (Australien) | 14 KB fra to feeds | 58 MB (V/Lines del af Transport Victorias fil på 311 MB, læst for sig), når den ændres, tjekket dagligt |
| WA Trains (Australien) | intet: der findes intet live-feed | 28 MB, når den ændres, tjekket dagligt |
| VR (Finland) | 1,4 KB komprimeret for positionerne; dagens tog, 0,5 MB komprimeret første gang, derefter kun ændringerne, én gang i minuttet | 3,1 MB, hver dag |
| Irish Rail (Irland) | 0,2 KB, højst én gang hvert 55. sekund | 6,6 MB, når den ændres, tjekket dagligt; stationslisten, 46 KB, én gang om ugen |
| NS, Arriva, Keolis (Nederlandene) | 1,5 KB, højst én gang hvert 9. sekund; forsinkelser fra OVapi, 5,3 MB, hvert 5. minut og kun, når de ændres | OVapis køreplan, 267 MB, højst én gang om ugen og kun, når den ændres; NS' sporkort, 1,3 MB, hver dag |
| Vy, Go-Ahead Norge, SJ Nord (Norge) | Vy 510 KB fra to feeds, Go-Ahead Norge 7 KB, SJ Nord 0,7 KB én gang i minuttet | Vy 67 MB, Go-Ahead Norge 20 MB, SJ Nord 26 MB, når de ændres, tjekket dagligt |
| Renfe (Spain) | 2,1 KB fra to feeds | 0,7 MB, hver dag; linjerne følger med integrationen |
| Renfe Regionals (Catalunya, Spanien) | 0,2 KB fra to feeds, der bærer alle Renfes lokale net | 16 MB, hver dag |
| De svenske jernbaner (Sverige) | 474 KB første gang, derefter 5 til 9 KB ændringer | intet; stationslisten, 0,15 MB, hver dag; linjerne følger med integrationen |
| VIA Rail (Canada) | 353 KB, sendt komprimeret som 33 KB | 1,0 MB, én gang om ugen |
| Amtrak (USA) | 1,2 MB, sendt komprimeret som 113 KB | 18,6 MB, én gang om ugen |
| Brightline (USA) | 1,3 KB fra to feeds | 29 KB, én gang om ugen |

⚠ Da dette blev målt, var det dag i Australien, aften i Nordamerika og nat i
Europa. Et live-feed er mindst om natten: om dagen er de europæiske feeds
større, end tabellen viser.

**Efter en fejl.** Togene bliver ved med at køre på de seneste gode data i op
til 10 minutter; derefter markeres de som utilgængelige, indtil kilden svarer.
En køreplan, der ikke kan hentes, forsøges igen senere, og den kopi, du har,
bliver ved med at blive brugt. Hvis en udbyder bliver ved med at afvise din
nøgle i ti minutter, beder Home Assistant om en ny.

**På disken.** Køreplaner og rutelinjer gemmes i Home Assistants mappe
`.storage` under navne, der begynder med `saw_`, delt med de andre Live
Track-moduler, der læser den samme jernbane. Hvis du fjerner Live Track
Intercity Rail, og intet andet Live Track-modul bruger dem, kan du slette dem
i hånden.

---

## Hjælp den med at vokse

Live Track Intercity Rail vokser stadig. Vi tilføjer jernbaner og lande,
efterhånden som vi finder dem, og vi vil gerne vide, hvad du kunne tænke dig
næste gang.

### Foreslå noget

Mangler dit land eller din jernbane? Er noget forkert eller svært at forstå?
Fortæl os det på den måde, der er nemmest for dig:

* [**Udfyld en kort formular**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=da.yml)
  på dansk. Du skal have en gratis GitHub-konto.
* **Skriv en e-mail** til
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Ingen konto nødvendig.

Uanset hvad hjælper det, hvis du fortæller os:

* hvad du gerne vil se, og hvor i verden;
* et link til, hvor dataene offentliggøres, hvis du kender et (en side med
  åbne data, et offentligt feed, en tjenestes hjemmeside): ikke nødvendigt,
  men det hjælper;
* din Home Assistants sprog, hvis problemet er formuleringen eller en
  oversættelse.

Skriv på engelsk eller på dit eget sprog, hvad der er nemmest for dig.

### Tilføj det selv, med vores hjælp

Vil du selv tilføje noget, hjælper vi dig med det, fra det første spørgsmål
til den færdige udgivelse. Du behøver ikke være udvikler for at begynde:

* **En oversættelse.** Teksterne i opsætningsdialogen er en kort liste af
  sætninger i én tekstfil. Vi viser dig hvilken fil og hvilke linjer.
* **En ny jernbane.** Fortæl os, hvor dataene offentliggøres. Vi kan skrive
  koden sammen eller se din igennem.
* **Test, hvor du bor.** Installer den, se på din del af kortet, og fortæl os,
  hvad der er rigtigt, og hvad der ikke er.
* **En rettelse til denne README.** Hvis et trin ikke passede med det, du så,
  så fortæl os, hvad du så.

[**Fortæl os, hvad du har i tankerne**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=da.yml)
eller skriv til
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
så svarer vi med de næste skridt.

---

## Sprog

Denne README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), [Español](README.es.md),
[Italiano](README.it.md), **Dansk**, [Suomi](README.fi.md),
[Svenska](README.sv.md), [Norsk bokmål](README.nb.md),
[Gaeilge](README.ga.md). Hver oversat README er komplet. Ingen af dem er endnu
læst af en, der har sproget som modersmål. Er et af disse sprog dit, så fortæl
os, om dets README læser godt: se [Hjælp den med at vokse](#hjælp-den-med-at-vokse).

Opsætningsdialogen og indstillingerne er indtil videre kun på engelsk, uanset
hvilket sprog din Home Assistant bruger. Taler du et andet sprog, kan du selv
oversætte dem: det er en kort liste med sætninger i én fil, og [vi hjælper dig
med det](#tilføj-det-selv-med-vores-hjælp).

Har du fundet en fejl i en oversættelse, eller har du brug for et andet sprog?
Fortæl os det på <https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues>,
eller [oversæt det med vores hjælp](#tilføj-det-selv-med-vores-hjælp).

---

## Tak og licenser

Hver live-kilde læses, mens integrationen kører, af din Home Assistant; intet
fra et live-feed ligger i dette repository. Hvert tog krediterer sin kilde i
sin attribut `attribution`. Hver kildes vilkår binder dig, som den, der
modtager dens data.

* **Amtraker** (amtraker.com), der videregiver Amtraks togsporing (USA): data
  under [Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/),
  kreditering påkrævet. **Amtraks** egen køreplan for rutelinjerne.
* **Brightline** (USA): dens GTFS- og GTFS-Realtime-feeds; Brightline
  offentliggør ingen vilkår.
* **VIA Rail** (Canada): dens togstatusdata, som VIA ikke offentliggør vilkår
  for; dens køreplan under Open Government Licence - Canada 2.0
  ([developer resources](https://www.viarail.ca/en/developer-resources)).
* **Fintraffic / digitraffic.fi** (Finland): data under CC BY 4.0.
* **Transport for NSW** (Australien): data under CC BY 4.0
  ([datalicens](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australien): data under CC BY 4.0
  ([åbne data](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Queensland Rail Travel** (Australien): de tider, dens side Service Updates
  viser, læst af din Home Assistant; se
  [Queensland Rails ophavsretsside](https://www.queenslandrailtravel.com.au/copyright).
  Intet fra Queensland Rail Travel følger med integrationen.
* **Journey Beyond** (Australien): dens offentliggjorte køreplaner, skrevet af
  i `data/journey_beyond_timetable.json`; Journey Beyond offentliggør ingen
  vilkår for dem.
* **Public Transport Authority of Western Australia**: køreplansdata, der kan
  fås gratis fra www.transperth.wa.gov.au
  ([spatial data access](https://www.transperth.wa.gov.au/About/Spatial-Data-Access);
  ikke CC BY).
* **Renfe** (Spanien): data under CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)).
* **Entur** (Norge): indeholder data under den norske licens for åbne
  offentlige data ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)), distribueret
  af Entur.
* **Trafikverket** (Sverige): data under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Irland): live-data; Irish Rail offentliggør ingen vilkår.
  Køreplan fra [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Irland), CC BY 4.0, leveret som den er.
* **NS** (Nederlandene): køretøjsdata og sporkort, med din egen nøgle, under
  vilkårene for [NS' API-portal](https://apiportal.ns.nl/). Køreplan og
  forsinkelser fra [OVapi](https://gtfs.ovapi.nl/), CC0.
* **Filer, der følger med i `data/`**: rutelinjer for Journey Beyond,
  Queensland Rail Travel, Renfe (Spain) og Sverige, bygget ud fra
  [OpenStreetMap](https://www.openstreetmap.org/copyright), © OpenStreetMaps
  bidragydere, under
  [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/);
  kommunerne for endestationerne på Renfes ture (OpenStreetMap, ODbL 1.0) og
  deres indbyggertal (Wikidata-egenskab P1082, CC0, ellers OpenStreetMap);
  indbyggertal for svenske endebyer fra Statistiska centralbyrån (SCB) og
  Trafikverket, begge CC0 1.0; indbyggertal for norske endebyer fra Statistisk
  sentralbyrå, tabel 04859, CC BY 4.0.
* **Kortkortet** er [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, en kopi af [ha-map-card](https://github.com/nathan-gs/ha-map-card) af
  nathan-gs, MIT, der følger med i `frontend/`. Dets kortfliser og deres
  kreditering står i dets README.

Ingen af disse organisationer har lavet eller godkendt denne integration.

**Kode**: MIT, i [LICENSE](LICENSE). Filerne i `data/` beholder deres kilders
licenser, nævnt ovenfor.

**For udviklere:** hver jernbane er ét modul i
`custom_components/live_track_intercity_rail/operators/`, som læser en
kildeadapter i `sources/`; de medfølgende rutelinjer bygges igen med scripts i
`tools/` (`journey_beyond.py`, `qrt_lines.py`, `renfe_spain_lines.py`,
`sweden_lines.py`). Testene køres med `python -m unittest discover -s tests`.

---

## Nøgleord

Home Assistant tog · Home Assistant togsporing · live togkort · intercitytog ·
fjerntog · togtrafik · tog i realtid · GTFS-Realtime · Amtrak · Amtraker ·
Brightline · VIA Rail · trains en temps réel · VR · kaukojunat · NSW
TrainLink · XPT · V/Line · The Ghan · Indian Pacific · Spirit of Queensland ·
Transwa · Renfe · AVE · Avlo · Alvia · Rodalies · trenes en tiempo real · Vy ·
SJ Nord · tog i sanntid · SJ · Snälltåget · Öresundståg · tåg i realtid ·
Irish Rail · Enterprise · traenacha beo · NS Intercity · Arriva · treinen live ·
Zugverkehr · treni in tempo reale · 火车实时地图 · geo_location · kortkort ·
Lovelace · HACS · Markedspladsen · Live Track · LiveTrack ·
StrausbergAutomationWorks

---

**Anerkendelse.** StrausbergAutomationWorks anerkender de oprindelige folk i
alle de lande og farvande, dette kort dækker, over hele verden, og viser sin
respekt for deres ældste, fortidens og nutidens.
