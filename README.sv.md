# Live Track Intercity Rail

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Suomi](README.fi.md) · **Svenska** · [Norsk bokmål](README.nb.md) · [Gaeilge](README.ga.md) · [Alla språk](#språk)

**Fjärrtåg i Home Assistant, på en karta.** Live Track Intercity Rail sätter
varje tåg från de intercity- och fjärrtågsjärnvägar du väljer på din Home
Assistant-karta: var det är, dess nummer, om det är försenat enligt
järnvägens egen regel, och dess nästa uppehåll. Varje järnväg läggs till för
sig, från sina egna publicerade data.

> **Live Track Intercity Rail är en modul i Live Track**, en familj av Home
> Assistant-integrationer som ritar allt som rör sig, och vädret det rör sig
> genom, på en gemensam karta: flygplan, fartyg, tåg och väder. Installera
> den ensam eller bredvid de andra modulerna
> ([lista nedan](#en-del-av-live-track-de-andra-modulerna)).

> **Växer, och öppen för idéer.** Live Track Intercity Rail täcker i dag 33
> järnvägar i 9 länder på 3 kontinenter, och vi lägger till fler järnvägar
> och länder. Saknas din? [Föreslå den](#hjälp-den-att-växa), eller lägg
> till den själv: vi hjälper dig med det.

**Status: 0.1.3, utgiven.** I Marknadsplatsens katalog ([installera den
nedan](#installera-den-steg-för-steg)).

Originalarbete av StrausbergAutomationWorks. Inte knutet till, eller
godkänt av, Amtrak, Amtraker, Brightline, VIA Rail, Fintraffic, VR,
Transport for NSW, NSW TrainLink, Transport Victoria, V/Line, Queensland
Rail, Journey Beyond, kollektivtrafikmyndigheten i Västaustralien (Public
Transport Authority of Western Australia), Transwa, Renfe, Rodalies de
Catalunya, Entur, Vy, Go-Ahead Norge, SJ Nord, Trafikverket, SJ, VR
Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen,
Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget,
Värmlandstrafik, Tågab, Inlandsbanan, Irish Rail, Irlands
transportmyndighet (National Transport Authority), NS, Arriva, Keolis,
OVapi eller någon annan järnväg.

---

## Innehåll

1. [Allt den gör](#allt-den-gör)
2. [Var den fungerar](#var-den-fungerar)
3. [En del av Live Track: de andra modulerna](#en-del-av-live-track-de-andra-modulerna)
4. [Innan du börjar](#innan-du-börjar)
5. [Installera den, steg för steg](#installera-den-steg-för-steg)
6. [Ställ in den, steg för steg](#ställ-in-den-steg-för-steg)
7. [Gratis nycklar som slår på mer, steg för steg](#gratis-nycklar-som-slår-på-mer-steg-för-steg)
8. [Lägg kartan på en kontrollpanel](#lägg-kartan-på-en-kontrollpanel)
9. [Använd den i automatiseringar](#använd-den-i-automatiseringar)
10. [Allt på kartan, i detalj](#allt-på-kartan-i-detalj)
11. [Alla entiteter den skapar](#alla-entiteter-den-skapar)
12. [Vad den skickar och laddar ner](#vad-den-skickar-och-laddar-ner)
13. [Hjälp den att växa](#hjälp-den-att-växa)
14. [Språk](#språk)
15. [Tack och licenser](#tack-och-licenser)
16. [Sökord](#sökord)

---

## Allt den gör

### På kartan, utan något att ställa in

Du lägger till en **järnväg**: du väljer ett land och sedan en av dess
intercityjärnvägar. Allt nedan visas sedan för den järnvägen. Lägg till
integrationen igen för varje annan järnväg du vill ha.

| Vad | Var | Från |
|---|---|---|
| **Tåg i trafik**: en markör per tåg, märkt med tågnumret eller linjen, i järnvägens egna färger, vänd åt det håll tåget går | varje järnväg | varje järnvägs egna publicerade data |
| **Försening**: ett tåg visas som försenat eller mycket försenat enligt järnvägens egen regel; där en järnväg inte publicerar någon regel, efter hur långt tåget går | varje järnväg som rapporterar förseningar | varje järnvägs eget flöde |
| **Nästa uppehåll och dess tid**: stationen där tåget stannar härnäst, och när det väntas dit | varje järnväg vars flöde eller tidtabell anger det | varje järnvägs eget flöde och tidtabell |
| **Tåg som följer spåret**: mellan två rapporter rör sig ett tåg längs sin egen linje i sin senaste hastighet, inte rakt över | varje järnväg vars linje är känd | varje järnvägs tidtabell, eller linjer som följer med integrationen |
| **Tåg från tidtabellen**: där en järnväg inte publicerar några positioner placeras varje tåg på sin linje efter sina tider och märks som en uppskattning | Journey Beyond, Queensland Rail Travel och WA Trains (Australien), SJ Nord (Norge); Irish Rail med sin senaste försening | varje järnvägs tidtabell eller tider |
| **Bilder för vissa tåg**: Tomtetåget och en sommarstuga (Finland), djuren på Journey Beyonds tåg, en bild för varje linje hos Queensland Rail Travel | Finland, Australien | ritade för den här integrationen |
| **Stopp vid gränsen**: ett tåg som står vid en gränsövergång mellan USA och Kanada visar "Customs" (tull) i stället för sin försening | Amtraks tåg till och från Kanada | Amtraks positioner |
| **Ett antal per järnväg**: tåg i trafik | varje järnväg | samma data |

### Påslaget med din egen gratis nyckel eller ditt eget konto

| Gratis nyckel eller konto | Vad den lägger till |
|---|---|
| Nyckel till **Transport for NSW Open Data** | NSW TrainLinks regionaltåg (New South Wales, Australien) |
| Nyckel till **Transport Victoria Open Data** | V/Lines fjärrtåg (Victoria, Australien) |
| Nyckel till **NS API portal** | NS Intercity, Arrivas och Keolis regionaltåg (Nederländerna); en nyckel räcker till alla tre |
| Nyckel till **Trafikverket** | de 15 svenska järnvägarna; en nyckel räcker till alla femton |

Var och en tar några minuter att skaffa: [steg för steg nedan](#gratis-nycklar-som-slår-på-mer-steg-för-steg).
De andra 13 järnvägarna behöver ingen nyckel.

---

## Var den fungerar

| Region | Vad du får | Från | Behöver |
|---|---|---|---|
| **Australien**: hela landet | Journey Beyond: The Ghan, The Ghan Expedition, Indian Pacific, Great Southern, The Overland, bara från tidtabellen ([varför](#journey-beyond-australien)) | Journey Beyond | ingenting |
| **Australien**: New South Wales | NSW TrainLinks regionaltåg (XPT och Xplorer), även in i Queensland, Victoria och Australian Capital Territory | Transport for NSW | en gratis nyckel |
| **Australien**: Queensland | Queensland Rail Travel: Spirit of Queensland, Spirit of the Outback, Tilt Train, Westlander, Inlander, Kuranda Scenic Railway, Gulflander, från sina publicerade tider ([varför](#queensland-rail-travel-australien)) | Queensland Rail Travel | ingenting |
| **Australien**: Victoria | V/Lines fjärrtåg (dess pendellinjer finns i Live Track Commuter Rail), även in i New South Wales | Transport Victoria | en gratis nyckel |
| **Australien**: Västaustralien | WA Trains: Australind, Prospector, MerredinLink och AvonLink, bara från tidtabellen ([varför](#wa-trains-västaustralien-australien)) | kollektivtrafikmyndigheten i Västaustralien | ingenting |
| **Europa**: Finland | VR:s fjärrtåg | Fintraffic Digitraffic | ingenting |
| **Europa**: Irland | Irish Rails InterCity-tåg, och Enterprise från Dublin till Belfast (Förenade kungariket) | Irish Rail, National Transport Authority | ingenting |
| **Europa**: Nederländerna | NS Intercity, och regionaltågen hos Arriva (Arriva, RRReis, Blauwnet) och Keolis (Blauwnet, RRReis); NS Sprinter finns i Live Track Commuter Rail | NS, OVapi | en gratis nyckel |
| **Europa**: Norge | Vys linjer F, RE, RX och R (F1 även in i Sverige), Go-Ahead Norges F5 och R50, SJ Nords F6, F7 och R60 till R75 | Entur | ingenting |
| **Europa**: Spanien | Renfes tåg AVE, Avlo, Alvia, Avant, Euromed, Intercity, MD och Regional, även in i Frankrike och Portugal; Rodalies de Catalunyas regionallinjer R11 till R17 | Renfe | ingenting |
| **Europa**: Sverige | SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget, Värmlandstrafik, Tågab och Inlandsbanan, en järnväg var; Öresundståg även in i Danmark | Trafikverket | en gratis nyckel |
| **Nordamerika**: Kanada | VIA Rail, varje linje | VIA Rail | ingenting |
| **Nordamerika**: USA | Amtrak, varje linje, även in i Kanada | Amtraker | ingenting |
| **Nordamerika**: USA | Brightline (Florida) | Brightline | ingenting |

Finns den inte på listan? [Säg till](#hjälp-den-att-växa). Där någon
publicerar data öppet tittar vi på att lägga till det.

⚠ **Ett tåg är bara så bra som järnvägens data.** Vissa järnvägar rapporterar
ett tåg med några sekunders mellanrum, vissa med några minuters, vissa bara
när det passerar signaler, och vissa publicerar inga positioner alls. Varje
järnvägs begränsningar står under
[Allt på kartan, i detalj](#allt-på-kartan-i-detalj).

⚠ **Det är inte järnvägens officiella information.** Kontrollera järnvägens
egen app eller webbplats innan du reser.

---

## En del av Live Track: de andra modulerna

Live Track är en uppsättning Home Assistant-integrationer, en för varje sorts
sak som rör sig, alla ritade på samma kartkort. Var och en fungerar ensam;
tillsammans blir de en levande bild. De delar kartkortet och ett
Python-bibliotek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
så att installera en till lägger inga förfrågningar till en källa som en annan
redan läser.

| Modul | Vad den visar på kartan | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | flygplan ovanför dig via ADS-B, med rutter och typikoner | utgiven |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | fartyg och båtar via AIS, nära dig eller var som helst | utgiven |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | pendeltåg i Nordamerika, Europa och Australien | utgiven |
| **Live Track Intercity Rail** | intercity- och fjärrtåg i Nordamerika, Europa och Australien (den här modulen) | utgiven |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | flygplan och fartyg som används av immigrations- och federala polismyndigheter, från offentliga listor | utgiven |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | väder, stormar och naturrisker | utgiven |
| Live Track Stations | avgångstavlor och "dags att gå"-aviseringar för varje station | planerad |
| Live Track Satellites | satelliter som passerar ovanför | planerad |
| Live Track Freight Trains | godståg och arbetståg där järnvägar publicerar dem | planerad |
| Live Track Transit | stadsbussar, spårvagnar, färjor och tunnelbana | planerad |
| Live Track Intercity Buses | fjärr- och regionbussar | planerad |
| Live Track Commuter Buses | pendelbussar | planerad |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | det gemensamma kartkortet som varje modul ritar på | utgivet, installeras med varje modul |

Allt är gratis och öppen källkod. Inget hålls tillbaka för sponsorer.

---

## Innan du börjar

* **Home Assistant** 2026.11 eller senare.
* **Marknadsplatsen** (HACS) i din Home Assistant, för att installera och
  uppdatera den på det enkla sättet. Utan den kan du kopiera filerna för
  hand.
* **Internetåtkomst** för Home Assistant: varje tåg kommer från sin järnvägs
  egna publicerade data.
* **Valfritt: auto-entities** från Marknadsplatsen, för att lägga markörerna
  på kartan (se [Lägg kartan på en kontrollpanel](#lägg-kartan-på-en-kontrollpanel)).
* Inget att betala. 13 av de 33 järnvägarna behöver inget konto; de andra 20
  behöver en egen gratis nyckel, och fyra nycklar täcker dem alla
  ([ovan](#påslaget-med-din-egen-gratis-nyckel-eller-ditt-eget-konto)).
* Home Assistant installerar själv de Python-paket den behöver
  (`saw-livetrack`, `gtfs-realtime-bindings` och `tzdata`) första gången
  integrationen laddas.

---

## Installera den, steg för steg

### Från Marknadsplatsen (rekommenderas)

1. Öppna **Inställningar → Marknadsplatsen** (HACS) i Home Assistant.
2. Sök efter **Live Track Intercity Rail** och öppna den.
3. Välj **Ladda ner** (eller **Installera**).
4. **Starta om Home Assistant**: **Inställningar → System → Lagningar**
   erbjuder omstarten, eller använd **Inställningar → System → Starta om**.

Om sökningen inte hittar den, lägg till den via dess länk: välj **Lägg till från
länk** (eller trepunktsmenyn → **Anpassade förråd**), ange
`StrausbergAutomationWorks/LiveTrackIntercityRail`, välj **Integration** om du
får frågan om typ och fortsätt sedan från steg 3.

Marknadsplatsen erbjuder sedan varje ny version som en uppdatering.

### För hand

1. Ladda ner källkoden för den
   [senaste versionen](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/releases/latest).
2. Kopiera dess mapp `custom_components/live_track_intercity_rail` till
   mappen `custom_components` i din Home Assistants konfigurationsmapp (skapa
   `custom_components` om den inte finns).
3. Starta om Home Assistant.

För att uppdatera för hand, ersätt mappen med den nya versionens och starta
om.

---

## Ställ in den, steg för steg

1. Öppna **Inställningar → Enheter och tjänster**.
2. Välj **Lägg till integration** (nere till höger) och sök efter **Live
   Track Intercity Rail**.
3. **Region** (region): välj järnvägens land. Bara länder med minst en
   järnväg visas. Välj **Bekräfta**.
4. **Railroad** (järnväg): välj järnvägen. Välj **Bekräfta**.
5. **API key** (API-nyckel): bara för NSW TrainLink, V/Line, de tre
   nederländska järnvägarna och de femton svenska järnvägarna. Klistra in din
   nyckel ([så skaffar du en](#gratis-nycklar-som-slår-på-mer-steg-för-steg))
   och välj **Bekräfta**. De andra järnvägarna hoppar över det här steget.

Det är allt. Tågen visas inom en minut eller två. Där en järnvägs linjer
kommer från dess tidtabell börjar tågen följa sina linjer när tidtabellen har
laddats ner, vilket kan ta några minuter första gången. För att följa en
annan järnväg, lägg till integrationen igen. Samma järnväg två gånger
avvisas.

### Ändra vad den visar: alternativen

Öppna **Inställningar → Enheter och tjänster → Live Track Intercity Rail →
Konfigurera** (kugghjulet) på den järnväg du vill ändra. Det finns ett
alternativ:

| Alternativ | Vad det gör | Standard |
|---|---|---|
| **Poll interval** (avfrågningsintervall) | hur ofta järnvägens källa läses, 15 till 600 sekunder. Ett kortare intervall än källans egen uppdatering visar inget mer | satt per järnväg: 15 sekunder för Renfe (Spain) och de tre nederländska järnvägarna; 60 sekunder för Brightline, NSW TrainLink, Irish Rail och SJ Nord; 30 sekunder för de andra |

---

## Gratis nycklar som slår på mer, steg för steg

Tjugo järnvägar ber varje användare om en egen nyckel, från fyra
leverantörer. Varje sådan nyckel är gratis, och var och en som installerar
Live Track Intercity Rail skaffar sin egen. Du klistrar in nyckeln när
inställningsdialogen ber om den ([steg 5 ovan](#ställ-in-den-steg-för-steg)).
Bara nyckeln efterfrågas: inget lösenord och ingen hemlighet. Nyckeln sparas
i Home Assistant tillsammans med integrationen, skickas bara till sin egen
leverantör och skrivs aldrig till loggen. Om leverantören avvisar den i tio
minuter ber Home Assistant dig om en ny.

### Transport for NSW (NSW TrainLink, New South Wales, Australien)

1. Öppna <https://opendata.transport.nsw.gov.au/>, välj **Register**, skapa
   ett konto och logga in.
2. Välj ikonen för din användarprofil och sedan **API Tokens**.
3. Skriv ett namn på nyckeln och välj **CREATE API TOKEN**. Kopiera nyckeln
   direkt: webbplatsen visar den bara en gång.
4. Klistra in den i **API key** när du lägger till NSW TrainLink. Klistra in
   bara nyckeln: Live Track Intercity Rail lägger själv till ordet `apikey`.

### Transport Victoria (V/Line, Victoria, Australien)

1. Öppna <https://opendata.transport.vic.gov.au/>, välj **Login** och sedan
   **Sign up**.
2. Fyll i dina uppgifter och välj **Create Account**. Skriv in koden från
   mejlet du får och välj **Confirm**.
3. Portalen kräver en autentiseringsapp i din telefon: skanna QR-koden med
   den, skriv in appens kod och välj **Confirm**. Logga sedan in med din
   e-postadress, ditt lösenord och appens kod.
4. Välj **My Account** → **Profile** → **API tokens**. Din nyckel finns redan
   där. Klistra in den i **API key** när du lägger till V/Line.

### NS (NS, Arriva och Keolis, Nederländerna)

1. Öppna <https://apiportal.ns.nl/>, välj **Inloggen** (logga in) och sedan
   **Externe bezoeker** (extern besökare).
2. Fyll i formuläret och skicka det. Ett mejl bekräftar registreringen.
   API:erna kan ta upp till 5 minuter att visas i portalen.
3. Öppna sidan för **Virtual Train API** (NS tågpositioner). Under **Related
   Products**, öppna dess produkt, ge din prenumeration ett namn och välj
   **Subscribe**.
4. När NS har godkänt prenumerationen finns din nyckel på din profilsida.
   Klistra in den i **API key** när du lägger till NS, Arriva eller Keolis.
   En nyckel räcker till alla tre.

### Trafikverket (de 15 svenska järnvägarna)

1. Öppna <https://data.trafikverket.se/oauth2/Account/register>.
2. Fyll i **Email**, **Displayname**, **Password** och **Confirm password**,
   kryssa i **Accept license and Agreement** och välj **Register**.
3. Öppna <https://data.trafikverket.se/get-started> och välj **Create key**,
   under **Create a key**. Logga in med kontot du skapade och skapa nyckeln.
4. Klistra in den i **API key** när du lägger till en svensk järnväg. En
   nyckel räcker till alla femton.

---

## Lägg kartan på en kontrollpanel

Kartan är [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
kortet som varje Live Track-modul ritar på. **Den installeras med Live Track
Intercity Rail**: inget att ladda ner, inget att kopiera, ingen resurs att
lägga till.

1. Öppna en kontrollpanel, välj pennan (**Redigera kontrollpanel**) och sedan
   **Lägg till kort**.
2. Rulla längst ner och välj **Manuell**.
3. Klistra in detta och välj **Spara**:

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

Den här formen behöver [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
från Marknadsplatsen. Med andra Live Track-moduler installerade, lägg till
ytterligare ett `- domain: geo_location`-filter för var och en av deras
källor (`live_track_commuter_rail`, `live_track_aircraft` och så vidare).

**Utan auto-entities:** LiveTrackMapCard kan själv välja vad det visar, med
`entity_filter`. Klistra in det här i stället; inget mer behöver installeras:

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

Andra Live Track-moduler läggs i `entity_filter` på samma sätt: en regel
`- domain: geo_location` till för varje källa.

**På kartan:**

* Varje tåg är en markör i järnvägens färger, märkt med tågnumret eller
  linjen. Amtraks tåg är stjärnor, VIA Rails bär lönnlövet, Irish Rails
  InterCity-tåg är klöverblad, och vissa tåg är bilder (varje järnväg nedan
  säger vilka).
* På de flesta järnvägar byter färgerna plats med riktningen: en sort när
  tåget lämnar huvudorten, den andra på väg mot den.
* En pil visar åt vilket håll tåget går. Ett tåg som står stilla behåller sin
  senaste riktning. Bilder står upprätt och har ingen pil.
* **Peka på** ett tåg för att se dess järnväg, nummer, linje och var det går.
  **Klicka** på det för alla detaljer, nästa uppehåll och försening
  inräknade.

Om dina kontrollpanelers resurser är inställda i YAML
(`lovelace: resource_mode: yaml`) kan inget registreras åt dig: ett ärende
under **Lagningar** ger då de exakta raderna att lägga till i
`configuration.yaml`. De ser ut så här, med integrationens egen adress i
stället för platshållarna:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_intercity_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Varje Live Track-modul har en kopia av kortet och registrerar den när Home
Assistant startar. Tillsammans håller de exakt en rad i **Inställningar →
Kontrollpaneler → Resurser**: den nyaste kortversionen som någon av dem har,
aldrig en äldre. Ett kort som du själv installerat via Marknadsplatsen lämnas
ifred. När du tar bort den här modulens sista järnväg går raden över till en
annan Live Track-modul, eller tas bort om ingen finns kvar. Om
integrationens filer tas bort medan dess järnvägar fortfarande är inställda,
och ingen annan Live Track-modul är installerad, ta bort raden själv i
**Inställningar → Kontrollpaneler → Resurser**.

**För att i stället installera kortet för hand**, följ stegen i
[kortets README](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
En rad som du själv har skapat för en kopia under `/local/` eller på någon annan
adress ändras eller tas aldrig bort. Så länge den läser in kortet överlåter
varje Live Track-modul kortet åt den, även när en modul har en nyare version,
och ingenting under **Lagningar** talar om det. För att gå tillbaka till
modulens kopia tar du bort din rad under **Inställningar → Kontrollpaneler →
Resurser** och startar om Home Assistant. Om du tar bort filen för din kopia, ta
bort dess rad också: så länge en rad vars fil är borta står kvar lägger modulen
inte till någon egen rad.

Alla andra kartkort som visar `geo_location`-entiteter visar också tågen,
som vanliga markörer.

---

## Använd den i automatiseringar

Allt är vanliga Home Assistant-entiteter, så automatiseringsredigeraren
fungerar med dem, ingen kod behövs.

**En avisering till telefonen när din järnvägs data slutar komma** (tågen
lämnar då kartan):

1. **Inställningar → Automatiseringar och scener → Skapa automatisering →
   Skapa ny automatisering**.
2. **När**: **Lägg till utlösare** → **Entitet** → **Tillstånd ändrat**. Välj
   järnvägens entitet **Trains in service** (tåg i trafik), och under **Till
   (valfritt)** välj **Otillgänglig**.
3. **Gör då**: **Lägg till åtgärd**, sök efter din telefons
   aviseringsåtgärd (den bär din telefons namn) och skriv ett meddelande,
   till exempel:

   ```text
   Inga fjärrtåg på kartan: järnvägens data har slutat komma
   ```

4. **Spara**.

**Andra idéer:** en lampa som tänds när ett Amtrak-tåg är inom 2 km (1,2
engelska mil) från ditt hem i USA, utifrån markörernas avstånd; en räknare på
kontrollpanelen över tågen VR kör i Finland under dagen; ett meddelande när
Queensland Rail Travels första tåg för dagen avgår (Australien), när **Trains
in service** stiger över 0.

---

## Allt på kartan, i detalj

### Tåg

Varje tåg är en markör. Dess tillstånd är dess avstånd från ditt hem, i
kilometer. Markören visas när järnvägen rapporterar tåget, eller när dess
tidtabell säger att det går, och tas bort när tåget lämnar järnvägens data
eller dess tur är slut.

* **Mellan två rapporter** rör sig ett tåg längs sin egen linje mot sitt
  nästa uppehåll: i den hastighet järnvägen rapporterar, eller, där den inte
  rapporterar någon, i hastigheten mellan dess två senaste rapporter. Det
  passerar aldrig sitt nästa uppehåll, och slutar röra sig 30 minuter efter
  den senaste rapporten. Ett tåg på en känd linje ritas på linjen;
  järnvägens egen rapport sparas bredvid.
* **Om en järnvägs data fallerar** fortsätter dess tåg att röra sig på sin
  senaste goda rapport i upp till 10 minuter. Därefter är de otillgängliga
  och lämnar kartan tills data kommer tillbaka.
* **Försenat och mycket försenat**: där järnvägen publicerar sin egen regel
  för ett försenat tåg använder integrationen den. Där den inte publicerar
  någon är ett tåg försenat efter hur långt det går, med gränsvärdena från
  Amtrak Status Maps (asm.transitdocs.com). Varje järnväg nedan säger
  vilket.

På varje tåg: `marker_label`, `train`, `line_name`, `observed_at` (när dess
rapport gällde), `course_deg` (medan det rör sig), `next_stop` och
`arrival_estimated_at` (där de är kända), `delay_min`, `late_threshold_min`
och `very_late_threshold_min`, `speed_kmh` (där järnvägen rapporterar den),
`attribution`, och, mellan två rapporter, `previous_latitude`,
`previous_longitude`, `previous_observed_at` och `segment_duration_s`. Ett
tåg som flyttats längs sin linje har `position_source: estimated`, med
järnvägens rapport i `fix_latitude` och `fix_longitude`.

### Journey Beyond (Australien)

⚠ **Journey Beyond publicerar inga positioner.** Varje tåg ritas från dess
publicerade tidtabell, överförd till en fil som följer med integrationen
(avgångar till 29 december 2027), så inget laddas ner. Varje tåg placeras på
sin linje efter sina tider, märkt som en uppskattning, utan försening: ett
försenat eller inställt tåg ritas ändå i tid. Varje tjänst är sin egen bild
(kamelen och ryttaren, en fågel, en känguru, en emu), i sina färger på väg
ut och med färgerna ombytta på väg tillbaka, utan etikett: peka på den för
att se tåget och dess tur.

### NSW TrainLink (New South Wales, Australien)

Från Transport for NSW:s flöde för NSW TrainLink, med din egen nyckel, en ny
position ungefär en gång i minuten. Etiketten är tågnumret. NSW-orange med en
vit ring när tåget lämnar Sydney, ombytt på väg dit. Flödet har ingen
hastighet, så ett tåg rör sig längs sin linje i hastigheten mellan sina två
senaste positioner. Försenat från 11 minuter (NSW TrainLink räknar ett tåg
som i tid inom 10 minuter), mycket försenat från 30.

### Queensland Rail Travel (Australien)

⚠ **Queensland Rail Travel publicerar inga positioner.** Din Home Assistant
läser tiderna som Queensland Rail Travels sida Service Updates visar: listan
över dagens tåg högst var 5:e minut, och varje tågs tider högst var 5:e
minut från 30 minuter före avgång till 15 minuter efter ankomst. Varje tåg
placeras på sin linje efter de tiderna och märks som en uppskattning. Varje
linje är sin egen bild, i sina färger när tåget lämnar Brisbane och ombytta
på väg dit, med tågnumret i en etikett bredvid. Försenat eller mycket
försenat visas inte.

### V/Line (Victoria, Australien)

Från Transport Victorias flöde för V/Line, med din egen nyckel: fjärrlinjerna
till Albury, Ararat, Bairnsdale, Echuca, Maryborough, Shepparton, Swan Hill
och Warrnambool. Etiketten är tågnumret. V/Line-lila med en gul ring när
tåget lämnar Melbourne, ombytt på väg dit. Flödet har ingen hastighet, så ett
tåg rör sig i hastigheten mellan sina två senaste positioner; efter 10
minuter utan ny position tidsätts det mot sitt nästa uppehåll. Försenat från
11 minuter på de långa linjerna och 6 på de korta (V/Lines egen lista),
mycket försenat från 30.

### WA Trains (Västaustralien, Australien)

⚠ **Inga levande positioner publiceras.** Varje tåg ritas från tidtabellen
hos kollektivtrafikmyndigheten i Västaustralien: placerat längs sin linje
efter sina tidtabellstider, märkt som en uppskattning, utan försening.
Tidtabellen kontrolleras en gång om dagen. Etiketten är linjens tre första
bokstäver: AUS (Australind, lila), PRO (Prospector, orange), MER
(MerredinLink, grön) och AVO (AvonLink, grön), samma i båda riktningarna.

### VR (Finland)

Från Fintraffics Digitraffic, en ny position ungefär var 30:e sekund.
Etiketten är tågtyp och nummer, som VR skriver det (`IC 23`). VR-grön med en
mörk ring när tåget lämnar Helsingfors, ombytt på väg dit. Data har ingen
riktning, så pilen följer linjen. Försenat från 6 minuter (VR räknar ett tåg
som försenat när det är mer än fem minuter sent), mycket försenat från 12.

* **Tomtetåget**, från första söndagen i advent till 6 januari: en snögubbe
  på väg norrut, en ren på väg tillbaka, utan nummer. Från 12 minuters
  försening vänder figuren sig om med några sekunders mellanrum.
* **Sommarstugan**, från midsommarafton till 31 juli: varje fjärrtåg hos VR
  ritas som en stuga, med sitt nummer bredvid.

### Irish Rail (Irland)

Från Irish Rails levande trafikinformation och tidtabellen från Irlands
transportmyndighet (National Transport Authority). ⚠ Irish Rail rapporterar
ett tåg bara när det passerar signalpunkter med några minuters mellanrum, så
varje tåg ritas från sin tidtabell och sin senaste försening, flyttat längs
sin linje. Etiketten är tågnumret utan bokstav (A700 visas som 700). Ett
InterCity-tåg är ett grönt klöverblad med orange kontur och nummer när det
lämnar Dublin, färgerna ombytta på väg dit. Enterprise är en silverskiva med
en röd yttre ring, ett magentafärgat band och ett magentafärgat nummer; på
väg till Dublin är skivan magenta. Försenat från 10 minuter (National
Transport Authoritys regel), mycket försenat från 20.

### NS, Arriva och Keolis (Nederländerna)

Från NS fordonsdata, med din egen nyckel, en ny position ungefär var 10:e
sekund. Det här flödet rapporterar tågets egen hastighet och riktning, och
båda förs vidare. Nästa uppehåll och förseningen kommer från OVapis
tidtabell; spåret är NS egen karta över sina linjer, nerladdad en gång om
dagen. Etiketten är tågnumret. NS tåg är gula med en ring i NS-blått; Arrivas
och Keolis tåg har kartkortets eget utseende tills vidare. Försenat från 3
minuter (NS egen definition), mycket försenat från 10.

### Vy, Go-Ahead Norge och SJ Nord (Norge)

Från Entur, varje järnväg sin egen post. Etiketten är linjekoden (F4, RE10,
R50). Linjens egen färg med en vit ring när tåget lämnar Oslo S (på en tur
som inte når Oslo S, dess större ändpunktsstad), ombytt på väg dit. Entur
publicerar ingen hastighet och ingen riktning, så ett tåg rör sig i
hastigheten mellan sina två senaste positioner och pilen följer dess linje. I
Oslos långa tunnlar flyttas ett tåg vars positioner upphör längs sin linje
tills de kommer tillbaka. ⚠ **SJ Nord publicerar inga positioner:** vart och
ett av dess tåg placeras på sin linje efter sina förväntade tider. Försenat
från 4 minuter, och från 6 på F-linjerna och linjerna till Göteborg
(Sverige), Bane NOR:s och Vys regel; mycket försenat vid det dubbla.

### Renfe (Spain) och Renfe Regionals (Catalunya), Spanien

**Renfe (Spain)** läser Renfes fjärrtrafikflöde, en ny position ungefär var
15:e sekund. Etiketten är tågnumret; tjänsten (AVE, Avlo, Alvia och så
vidare) står i hovringsrutan. AVE marinblå, Avlo turkos, varje annan tjänst
Renfe-lila, var och en fylld när tåget lämnar Madrid (på en tur som inte når
Madrid, dess större ändpunktsstad) och ombytt på väg dit. Renfe publicerar
inga linjesträckningar, så linjerna är byggda från OpenStreetMap och följer
med integrationen. Renfe publicerar ingen regel för ett försenat tåg, så ett
tåg är försenat efter resans längd: från 10 minuter upp till 400 km (250
engelska mil), 15 upp till 560 km (350 engelska mil), 20 upp till 725 km
(450 engelska mil), 25 upp till 885 km (550 engelska mil), 30 därutöver;
mycket försenat vid det dubbla.

**Renfe Regionals (Catalunya)** ritar Rodalies de Catalunyas regionallinjer
R11 till R17. Etiketten är tågnumret, i linjens egen färg, fylld när tåget
lämnar Barcelona och ombytt på väg dit. Utanför Barcelona är en position den
senaste station ett tåg passerade, så tåget tidsätts mellan stationerna efter
tidtabellen och sin försening. Försenat från 10 minuter, mycket försenat från
20, efter den längsta linjens längd. Med båda Renfe-järnvägarna inställda
ritas varje tåg en gång.

### De svenska järnvägarna (Sverige)

Från Trafikverket, med din egen nyckel (en nyckel för alla femton).
Etiketten är tågnumret på biljetten; varumärke, nummer och ändstationer står
i hovringsrutan. Varje varumärke har sina egna färger, ombytta på väg till
Stockholm C (på en tur som inte når Stockholm C, dess större
ändpunktsstad). Trafikverket ger en hastighet på ungefär hälften av sina
positioner; de andra tågen rör sig i hastigheten mellan sina två senaste
positioner. Sverige publicerar inga linjesträckningar, så linjerna är byggda
från OpenStreetMap och följer med integrationen. Försenat från 6 minuter
(Trafikverket räknar ett tåg som i tid till och med 5 minuter 59 sekunder),
mycket försenat från 12.

### VIA Rail (Kanada)

Från VIA Rails egna data om tågstatus. Varje tåg är en skiva med lönnlövet
och ett band i linjegruppens färg (Atlantic, Western, Ontario och Quebec,
Prince Rupert, Churchill, Sudbury till White River, Montréals natursköna
linjer), med tågnumret i en upprätt etikett. Udda nummer har en gul skiva,
jämna en skiva i bandets färg. Ett tåg utan ny position rör sig mot sitt
nästa uppehåll för att komma fram vid VIA:s egen uppskattning. VIA
publicerar ingen regel för ett försenat tåg, så ett tåg är försenat från 10
minuter i korridoren Québec City till Windsor och från 60 på andra håll
(Amtrak Status Maps värden för VIA), mycket försenat vid det dubbla.

### Amtrak (USA)

Amtrak publicerar inga öppna levande data. Amtraker vidarebefordrar Amtraks
egen tågspårning, med en ny position var 3:e till 5:e minut, och
integrationen flyttar varje tåg längs sin linje i den hastighet Amtrak
rapporterar. Varje tåg är en stjärna med sitt nummer tvärs över, i sin linjes
färger (Northeast-linjerna, Cascades, Pacific Surfliner, Acela med flera),
annars flaggstjärnan. Maple Leaf (New York till Toronto) skiftar långsamt
mellan Amtraks stjärna och VIA:s märke. Ett tåg som står vid gränsen vid
Lacolle, Rouses Point eller Niagara Falls visar "Customs" (tull) i stället
för sin försening. Försenat från 16 minuter (Amtrak räknar ett tåg som i tid
inom 15 minuter), mycket försenat från 30. Samma tågnummer kan gå på två
eller tre dagar samtidigt, så varje tur är sin egen markör.

### Brightline (USA)

Från Brightlines eget flöde, en ny position ungefär var 60:e sekund.
Etiketten är turnumret, i svart med vit kontur, på en skiva i färgen för
tågets destination, med en svart ring. En position äldre än 5 minuter
används inte. Flödet har ingen hastighet, så ett tåg rör sig i hastigheten
mellan sina två senaste positioner. Brightline publicerar ingen regel för ett
försenat tåg, så ett tåg är försenat från 10 minuter, mycket försenat från
20, efter resans längd.

---

## Alla entiteter den skapar

För varje järnväg:

| Entitet | Vad den är |
|---|---|
| `sensor.<railroad>_trains_in_service` | **Trains in service** (tåg i trafik): hur många tåg järnvägen kör på kartan just nu. För Amtrak: `sensor.amtrak_trains_in_service` |
| `geo_location.<railroad>_train_…` | en per tåg (`geo_location.amtrak_train_5_17`); den kommer och går med tåget. Var och en har `source: live_track_intercity_rail`, och dess tillstånd är dess avstånd från ditt hem i kilometer |

En markörs entitets-ID kommer från järnvägen och turen, aldrig från dess
etikett: `geo_location.amtrak_train_5_17` är Amtraks tåg 5 som avgick den 17:e
i månaden, så ett tåg behåller samma entitets-ID under hela sin tur, och en
annan tur med samma nummer får ett eget. Markören tas bort när turen lämnar
järnvägens data eller slutar. Markörerna har inget unikt ID (unique ID), lika
lite som någon kartmarkör i Live Track, så de kan inte döpas om, döljas eller
få ett område i gränssnittet. Sensorn har ett unikt ID och kan döpas om.

Attribut som ändras vid varje avfrågning, markörernas positioner och tider,
registreras i Home Assistants historik, som för vilken entitet som helst.
Sensorn har inga attribut, så den kostar lite att behålla, och den är
registret över hur många tåg som gick under en dag. För att hålla markörerna
utanför historiken, lägg till detta i `configuration.yaml` och starta sedan
om:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_train_*
```

Om din `configuration.yaml` redan har en `recorder:`-sektion, lägg bara till
mönstret `geo_location.*_train_*` i den, under `exclude:` och
`entity_globs:`. Mönstret träffar bara den här modulens tågmarkörer. Ett
kartkort som är inställt på att rita historik har då inget spår att rita.

---

## Vad den skickar och laddar ner

**Om din position.** Ingenting. Ditt hems position används bara inne i din
Home Assistant, för att ge varje tågs avstånd. Din nyckel, där en järnväg
behöver en, skickas bara till den järnvägens leverantör. Inget annat om dig
skickas någonstans. Varje tjänst ser din internetadress, som vilken
webbplats som helst.

**Hur mycket.** Varje levande källa läses vid varje avfrågning, med
järnvägens eget intervall som standard (**Poll interval**, 15 till 600
sekunder), eller mer sällan där tabellen säger det. Där flera Live
Track-moduler eller järnvägar läser samma källa läser en gemensam klient den
en gång för dem alla. Uppmätt den 19 november 2026, 02:44 till 02:49 UTC:

| Järnväg | Levande data, en läsning | Tidtabell och linjer |
|---|---|---|
| Journey Beyond (Australien) | ingen: inget laddas ner | ingen: dess tidtabell och linjer följer med integrationen |
| NSW TrainLink (Australien) | 124 kB från två flöden, högst en gång var 55:e sekund | 40 MB, vid ändring, kontrolleras dagligen |
| Queensland Rail Travel (Australien) | listan, 5,5 kB, var 5:e minut; varje gående tågs tider, 6 till 8 kB, var 5:e minut | ingen: dess linjer följer med integrationen |
| V/Line (Australien) | 14 kB från två flöden | 58 MB (V/Lines del av Transport Victorias fil på 311 MB, läst för sig), vid ändring, kontrolleras dagligen |
| WA Trains (Australien) | ingen: inget levande flöde finns | 28 MB, vid ändring, kontrolleras dagligen |
| VR (Finland) | 1,4 kB komprimerat för positionerna; dagens tåg, 0,5 MB komprimerat första gången, sedan bara ändringarna, en gång i minuten | 3,1 MB, varje dag |
| Irish Rail (Irland) | 0,2 kB, högst en gång var 55:e sekund | 6,6 MB, vid ändring, kontrolleras dagligen; stationslistan, 46 kB, en gång i veckan |
| NS, Arriva, Keolis (Nederländerna) | 1,5 kB, högst en gång var 9:e sekund; förseningar från OVapi, 5,3 MB, var 5:e minut och bara vid ändring | OVapis tidtabell, 267 MB, högst en gång i veckan och bara vid ändring; NS spårkarta, 1,3 MB, varje dag |
| Vy, Go-Ahead Norge, SJ Nord (Norge) | Vy 510 kB från två flöden, Go-Ahead Norge 7 kB, SJ Nord 0,7 kB en gång i minuten | Vy 67 MB, Go-Ahead Norge 20 MB, SJ Nord 26 MB, vid ändring, kontrolleras dagligen |
| Renfe (Spain) | 2,1 kB från två flöden | 0,7 MB, varje dag; dess linjer följer med integrationen |
| Renfe Regionals (Catalunya) | 0,2 kB från två flöden som bär alla Renfes lokala nät | 16 MB, varje dag |
| De svenska järnvägarna (Sverige) | 474 kB första gången, sedan 5 till 9 kB ändringar | ingen; stationslistan, 0,15 MB, varje dag; linjerna följer med integrationen |
| VIA Rail (Kanada) | 353 kB, skickat komprimerat som 33 kB | 1,0 MB, en gång i veckan |
| Amtrak (USA) | 1,2 MB, skickat komprimerat som 113 kB | 18,6 MB, en gång i veckan |
| Brightline (USA) | 1,3 kB från två flöden | 29 kB, en gång i veckan |

⚠ När detta mättes var det dag i Australien, kväll i Nordamerika och natt i
Europa. Ett levande flöde är som minst på natten: på dagen är de europeiska
flödena större än tabellen visar.

**Efter ett fel.** Tågen fortsätter att röra sig på senaste goda data i upp
till 10 minuter; sedan markeras de som otillgängliga tills källan svarar. En
tidtabell som inte kan laddas ner försöks igen senare, och kopian du har
fortsätter att användas. Om en leverantör fortsätter att avvisa din nyckel i
tio minuter ber Home Assistant om en ny.

**På disken.** Tidtabeller och linjesträckningar sparas i Home Assistants
mapp `.storage` under namn som börjar med `saw_`, delade med de andra Live
Track-modulerna som läser samma järnväg. Om du tar bort Live Track
Intercity Rail och ingen annan Live Track-modul använder dem kan du ta bort
dem för hand.

---

## Hjälp den att växa

Live Track Intercity Rail växer fortfarande. Vi lägger till banor och länder
när vi hittar dem, och vi vill veta vad du vill ha härnäst.

### Föreslå något

Saknas ditt land eller din bana? Är något fel, eller svårt att förstå? Säg
till på det sätt som är enklast för dig:

* [**Fyll i ett kort formulär**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=sv.yml)
  på svenska. Du behöver ett gratis GitHub-konto.
* **Skicka e-post** till
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Inget konto behövs.

Hur du än gör hjälper det om du berättar:

* vad du vill se, och var i världen;
* en länk till var data publiceras, om du känner till en (en sida med öppna
  data, ett öppet flöde, en tjänsts webbplats): inte nödvändigt, men det
  hjälper;
* språket i din Home Assistant, om problemet är formuleringen eller en
  översättning.

Skriv på engelska eller på ditt eget språk, det som är enklast för dig.

### Lägg till det själv, med vår hjälp

Om du vill lägga till något själv hjälper vi dig, från den första frågan till
den färdiga versionen. Du behöver inte vara utvecklare för att börja:

* **En översättning.** Orden i inställningsdialogen är en kort lista med
  fraser i en textfil. Vi visar vilken fil och vilka rader.
* **En ny bana.** Berätta var data publiceras. Vi kan skriva koden
  tillsammans, eller gå igenom din.
* **Testa där du bor.** Installera den, titta på din del av kartan och säg
  vad som stämmer och vad som inte gör det.
* **En rättelse av den här README-filen.** Om ett steg inte stämde med det du
  såg, berätta vad du såg.

[**Berätta vad du har i tankarna**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=sv.yml)
eller skriv till
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
så svarar vi med nästa steg.

---

## Språk

Den här README-filen: [English](README.md), [Deutsch](README.de.md), [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md), [Español](README.es.md),
[Italiano](README.it.md), [Dansk](README.da.md), [Suomi](README.fi.md), **Svenska**,
[Norsk bokmål](README.nb.md), [Gaeilge](README.ga.md). Varje översatt README-fil
är fullständig. Ingen har ännu lästs av någon med språket som modersmål. Är
svenska ditt modersmål, säg gärna om den här README-filen läses bra: se
[Hjälp den att växa](#hjälp-den-att-växa).

Inställningsdialogen och alternativen finns tills vidare bara på engelska,
oavsett din Home Assistants språk. Talar du ett annat språk kan du själv
översätta dem: det är en kort lista med fraser i en fil, och [vi hjälper dig med
det](#lägg-till-det-själv-med-vår-hjälp).

Hittat ett fel i en översättning, eller behöver du ett annat språk? Säg till
på <https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues>,
eller [översätt med vår hjälp](#lägg-till-det-själv-med-vår-hjälp).

---

## Tack och licenser

Varje levande källa läses vid körning, av din Home Assistant; inget från ett
levande flöde finns i det här förrådet. Varje tåg anger sin källa i sitt
attribut `attribution`. Varje källas villkor binder dig, som den som tar
emot dess data.

* **Amtraker** (amtraker.com), som vidarebefordrar Amtraks tågspårning (USA):
  data under
  [Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/),
  källhänvisning krävs. **Amtraks** egen tidtabell för linjesträckningarna.
* **Brightline** (USA): dess GTFS- och GTFS-Realtime-flöden; Brightline
  publicerar inga villkor.
* **VIA Rail** (Kanada): dess data om tågstatus, för vilka VIA inte
  publicerar några villkor; dess tidtabell under Open Government Licence -
  Canada 2.0 ([developer resources](https://www.viarail.ca/en/developer-resources)).
* **Fintraffic / digitraffic.fi** (Finland): data under CC BY 4.0.
* **Transport for NSW** (Australien): data under CC BY 4.0
  ([datalicens](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australien): data under CC BY 4.0
  ([öppna data](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Queensland Rail Travel** (Australien): tiderna som dess sida Service
  Updates visar, lästa av din Home Assistant; se
  [Queensland Rails upphovsrättssida](https://www.queenslandrailtravel.com.au/copyright).
  Inget från Queensland Rail Travel följer med integrationen.
* **Journey Beyond** (Australien): dess publicerade tidtabeller, överförda
  till `data/journey_beyond_timetable.json`; Journey Beyond publicerar inga
  villkor för dem.
* **Kollektivtrafikmyndigheten i Västaustralien** (Public Transport
  Authority of Western Australia): tidtabellsdata tillgängliga utan kostnad
  från www.transperth.wa.gov.au
  ([spatial data access](https://www.transperth.wa.gov.au/About/Spatial-Data-Access);
  inte CC BY).
* **Renfe** (Spanien): data under CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)).
* **Entur** (Norge): innehåller data under den norska licensen för öppna
  offentliga data ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)),
  distribuerade av Entur.
* **Trafikverket** (Sverige): data under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Irland): levande data; Irish Rail publicerar inga villkor.
  Tidtabell från [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Irland), CC BY 4.0, i befintligt skick.
* **NS** (Nederländerna): fordonsdata och spårkarta, med din egen nyckel,
  under villkoren för [NS API portal](https://apiportal.ns.nl/). Tidtabell
  och förseningar från [OVapi](https://gtfs.ovapi.nl/), CC0.
* **Filer som följer med i `data/`**: linjesträckningar för Journey Beyond,
  Queensland Rail Travel, Renfe (Spain) och Sverige, byggda från
  [OpenStreetMap](https://www.openstreetmap.org/copyright), © OpenStreetMaps
  bidragsgivare, under
  [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/);
  ändstationskommunerna för Renfes turer (OpenStreetMap, ODbL 1.0) och deras
  befolkning (Wikidata-egenskapen P1082, CC0, annars OpenStreetMap); svenska
  ändpunktsstäders befolkning från Statistiska centralbyrån (SCB) och
  Trafikverket, båda CC0 1.0; norska ändpunktsstäders befolkning från
  Statistisk sentralbyrå (Norge), tabell 04859, CC BY 4.0.
* **Kartkortet** är [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, en kopia av [ha-map-card](https://github.com/nathan-gs/ha-map-card)
  av nathan-gs, MIT, som följer med i `frontend/`. Dess kartplattor och deras
  källhänvisningar står i dess README.

Ingen av dessa organisationer har gjort eller godkänt den här integrationen.

**Kod**: MIT, i [LICENSE](LICENSE). Filerna i `data/` behåller sina källors
licenser, listade ovan.

**För utvecklare:** varje järnväg är en modul i
`custom_components/live_track_intercity_rail/operators/`, som läser en
källadapter i `sources/`; de medföljande linjesträckningarna byggs om med
skripten i `tools/` (`journey_beyond.py`, `qrt_lines.py`,
`renfe_spain_lines.py`, `sweden_lines.py`). Testerna körs med
`python -m unittest discover -s tests`.

---

## Sökord

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

**Erkännande.** StrausbergAutomationWorks erkänner urfolken i alla de länder och
vatten som den här kartan täcker, över hela världen, och visar sin respekt för
deras äldste, förr och nu.
