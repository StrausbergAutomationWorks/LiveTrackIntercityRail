# Live Track Intercity Rail

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · **Nederlands** · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · [Gaeilge](README.ga.md) · [Alle talen](#talen)

**Intercitytreinen voor Home Assistant, op één kaart.** Live Track Intercity
Rail zet elke trein van de intercity- en langeafstandsspoorwegen die je kiest
op je Home Assistant-kaart: waar hij is, zijn nummer, of hij te laat is
volgens de eigen regel van de spoorweg, en zijn volgende halte. Elke spoorweg
voeg je apart toe, op basis van zijn eigen gepubliceerde gegevens.

> **Live Track Intercity Rail is één module van Live Track**, een familie van
> Home Assistant-integraties die alles wat beweegt, en het weer waarin het
> beweegt, op één gedeelde kaart tekenen: vliegtuigen, schepen, treinen en
> weer. Installeer het op zichzelf, of naast de andere modules
> ([lijst hieronder](#onderdeel-van-live-track-de-andere-modules)).

> **Groeiend, en open voor ideeën.** Live Track Intercity Rail dekt vandaag
> 33 spoorwegen in 9 landen op 3 continenten, en we voegen meer spoorwegen en
> landen toe. Ontbreekt de jouwe? [Stel hem voor](#help-het-groeien), of voeg
> hem zelf toe: we helpen je daarbij.

**Status: 0.1.3, uitgebracht.** In de catalogus van de Marktplaats ([installeer
het hieronder](#installeren-stap-voor-stap)).

Origineel werk van StrausbergAutomationWorks. Niet verbonden aan, of
goedgekeurd door, Amtrak, Amtraker, Brightline, VIA Rail, Fintraffic, VR,
Transport for NSW, NSW TrainLink, Transport Victoria, V/Line, Queensland Rail,
Journey Beyond, de Public Transport Authority of Western Australia, Transwa,
Renfe, Rodalies de Catalunya, Entur, Vy, Go-Ahead Norge, SJ Nord,
Trafikverket, SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg,
Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget,
Värmlandstrafik, Tågab, Inlandsbanan, Irish Rail, de National Transport
Authority (Ierland), NS, Arriva, Keolis, OVapi, of welke andere spoorweg dan
ook.

---

## Inhoud

1. [Alles wat het doet](#alles-wat-het-doet)
2. [Waar het werkt](#waar-het-werkt)
3. [Onderdeel van Live Track: de andere modules](#onderdeel-van-live-track-de-andere-modules)
4. [Voordat je begint](#voordat-je-begint)
5. [Installeren, stap voor stap](#installeren-stap-voor-stap)
6. [Instellen, stap voor stap](#instellen-stap-voor-stap)
7. [Gratis sleutels die meer aanzetten, stap voor stap](#gratis-sleutels-die-meer-aanzetten-stap-voor-stap)
8. [De kaart op een dashboard zetten](#de-kaart-op-een-dashboard-zetten)
9. [Gebruiken in automatiseringen](#gebruiken-in-automatiseringen)
10. [Alles op de kaart, in detail](#alles-op-de-kaart-in-detail)
11. [Alle entiteiten die het aanmaakt](#alle-entiteiten-die-het-aanmaakt)
12. [Wat het verstuurt en downloadt](#wat-het-verstuurt-en-downloadt)
13. [Help het groeien](#help-het-groeien)
14. [Talen](#talen)
15. [Vermeldingen en licenties](#vermeldingen-en-licenties)
16. [Trefwoorden](#trefwoorden)

---

## Alles wat het doet

### Op de kaart, zonder iets in te stellen

Je voegt een **spoorweg** toe: je kiest een land, en dan een van zijn
intercityspoorwegen. Alles hieronder verschijnt dan voor die spoorweg. Voeg de
integratie opnieuw toe voor elke andere spoorweg die je wilt.

| Wat | Waar | Van |
|---|---|---|
| **Treinen in dienst**: één marker per trein, met zijn treinnummer of zijn lijn als label, in de eigen kleuren van de spoorweg, gedraaid in de richting waarin hij rijdt | elke spoorweg | de eigen gepubliceerde gegevens van elke spoorweg |
| **Vertraging**: een trein wordt als te laat of zeer te laat getoond volgens de eigen regel van de spoorweg; waar een spoorweg geen regel publiceert, naar de afstand die de trein aflegt | elke spoorweg die vertragingen meldt | de eigen feed van elke spoorweg |
| **Volgende halte en de tijd daarvan**: het station waar een trein als volgende stopt, en wanneer hij daar verwacht wordt | elke spoorweg waarvan de feed of dienstregeling dat zegt | de eigen feed en dienstregeling van elke spoorweg |
| **Treinen die het spoor volgen**: tussen twee meldingen rijdt een trein langs zijn eigen lijn met zijn laatste snelheid, niet in een rechte lijn | elke spoorweg waarvan de lijn bekend is | de dienstregeling van elke spoorweg, of lijnen die met de integratie worden meegeleverd |
| **Treinen uit de dienstregeling**: waar een spoorweg geen posities publiceert, wordt elke trein volgens zijn tijden op zijn lijn geplaatst en als schatting gemarkeerd | Journey Beyond, Queensland Rail Travel en WA Trains (Australië), SJ Nord (Noorwegen); Irish Rail met zijn laatste vertraging | de dienstregeling of de tijden van elke spoorweg |
| **Afbeeldingen voor sommige treinen**: de Kerstmanexpres en een zomerhuisje (Finland), de dieren van de treinen van Journey Beyond, een afbeelding voor elke lijn van Queensland Rail Travel | Finland, Australië | getekend voor deze integratie |
| **Stilstaand aan de grens**: een trein die bij een grensovergang tussen de Verenigde Staten en Canada stilstaat, toont "Customs" in plaats van zijn vertraging | treinen van Amtrak van en naar Canada | de posities van Amtrak |
| **Eén telling per spoorweg**: treinen in dienst | elke spoorweg | dezelfde gegevens |

### Aangezet door je eigen gratis sleutel of account

| Gratis sleutel of account | Wat het toevoegt |
|---|---|
| Sleutel van **Transport for NSW Open Data** | de regionale treinen van NSW TrainLink (New South Wales, Australië) |
| Sleutel van **Transport Victoria Open Data** | de langeafstandstreinen van V/Line (Victoria, Australië) |
| Sleutel van het **NS API-portaal** | NS Intercity en de regionale treinen van Arriva en Keolis (Nederland); één sleutel geldt voor alle drie |
| Sleutel van **Trafikverket** | de 15 Zweedse spoorwegen; één sleutel geldt voor alle vijftien |

Elke sleutel is in een paar minuten te krijgen: [stap voor stap hieronder](#gratis-sleutels-die-meer-aanzetten-stap-voor-stap).
De andere 13 spoorwegen hebben geen sleutel nodig.

---

## Waar het werkt

| Regio | Wat je krijgt | Van | Nodig |
|---|---|---|---|
| **Australië**: het hele land | Journey Beyond: The Ghan, The Ghan Expedition, Indian Pacific, Great Southern, The Overland, alleen uit de dienstregeling ([waarom](#journey-beyond-australië)) | Journey Beyond | niets |
| **Australië**: New South Wales | de regionale treinen van NSW TrainLink (XPT en Xplorer), ook naar Queensland, Victoria en het Australian Capital Territory | Transport for NSW | een gratis sleutel |
| **Australië**: Queensland | Queensland Rail Travel: Spirit of Queensland, Spirit of the Outback, Tilt Train, Westlander, Inlander, Kuranda Scenic Railway, Gulflander, uit hun gepubliceerde tijden ([waarom](#queensland-rail-travel-australië)) | Queensland Rail Travel | niets |
| **Australië**: Victoria | de langeafstandstreinen van V/Line (de forensenlijnen staan in Live Track Commuter Rail), ook naar New South Wales | Transport Victoria | een gratis sleutel |
| **Australië**: Western Australia | WA Trains: de Australind, de Prospector, de MerredinLink en de AvonLink, alleen uit de dienstregeling ([waarom](#wa-trains-western-australia-australië)) | Public Transport Authority of Western Australia | niets |
| **Europa**: Finland | de langeafstandstreinen van VR | Fintraffic Digitraffic | niets |
| **Europa**: Ierland | de InterCity-treinen van Irish Rail, en de Enterprise van Dublin naar Belfast (Verenigd Koninkrijk) | Irish Rail, National Transport Authority | niets |
| **Europa**: Nederland | NS Intercity, en de regionale treinen van Arriva (Arriva, RRReis, Blauwnet) en Keolis (Blauwnet, RRReis); de Sprinters van NS staan in Live Track Commuter Rail | NS, OVapi | een gratis sleutel |
| **Europa**: Noorwegen | de F-, RE-, RX- en R-lijnen van Vy (F1 ook naar Zweden), F5 en R50 van Go-Ahead Norge, F6, F7 en R60 tot R75 van SJ Nord | Entur | niets |
| **Europa**: Spanje | de AVE-, Avlo-, Alvia-, Avant-, Euromed-, Intercity-, MD- en Regional-treinen van Renfe, ook naar Frankrijk en Portugal; de regionale lijnen R11 tot R17 van Rodalies de Catalunya | Renfe | niets |
| **Europa**: Zweden | SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget, Värmlandstrafik, Tågab en Inlandsbanan, elk een eigen spoorweg; Öresundståg ook naar Denemarken | Trafikverket | een gratis sleutel |
| **Noord-Amerika**: Canada | VIA Rail, elke route | VIA Rail | niets |
| **Noord-Amerika**: Verenigde Staten | Amtrak, elke route, ook naar Canada | Amtraker | niets |
| **Noord-Amerika**: Verenigde Staten | Brightline (Florida) | Brightline | niets |

Staat het er niet bij? [Laat het ons weten](#help-het-groeien). Waar iemand
de gegevens openlijk publiceert, kijken we of we het kunnen toevoegen.

⚠ **Een trein is maar zo goed als de gegevens van zijn spoorweg.** Sommige
spoorwegen melden een trein om de paar seconden, sommige om de paar minuten,
sommige alleen als hij seinen passeert, en sommige publiceren helemaal geen
posities. De beperkingen van elke spoorweg staan onder
[Alles op de kaart, in detail](#alles-op-de-kaart-in-detail).

⚠ **Het is niet de officiële informatie van de spoorweg.** Kijk voordat je
reist in de eigen app of op de eigen website van de spoorweg.

---

## Onderdeel van Live Track: de andere modules

Live Track is een reeks Home Assistant-integraties, één per soort bewegend
ding, allemaal getekend op dezelfde kaart. Elke werkt op zichzelf; samen
vormen ze één live beeld. Ze delen de kaart en een Python-bibliotheek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
dus een extra module installeren voegt geen verzoeken toe aan een bron die een
andere al leest.

| Module | Wat het op de kaart zet | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | vliegtuigen boven je via ADS-B, met routes en typesymbolen | uitgebracht |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | schepen en boten via AIS, bij jou in de buurt of overal | uitgebracht |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | forensentreinen in Noord-Amerika, Europa en Australië | uitgebracht |
| **Live Track Intercity Rail** | intercity- en langeafstandstreinen in Noord-Amerika, Europa en Australië (deze module) | uitgebracht |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | vliegtuigen en schepen van immigratie- en federale ordediensten, uit openbare lijsten | uitgebracht |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | weer, stormen en natuurgevaren | uitgebracht |
| Live Track Stations | vertrekborden en "tijd om te gaan"-meldingen voor elk station | gepland |
| Live Track Satellites | satellieten die over je heen trekken | gepland |
| Live Track Freight Trains | goederen- en werktreinen waar spoorwegen ze publiceren | gepland |
| Live Track Transit | stadsbussen, trams, veerboten en metro | gepland |
| Live Track Intercity Buses | intercity- en streekbussen | gepland |
| Live Track Commuter Buses | forensenbussen | gepland |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | de gedeelde kaart waarop elke module tekent | uitgebracht, met elke module geïnstalleerd |

Alles is gratis en open source. Niets wordt achtergehouden voor sponsors.

---

## Voordat je begint

* **Home Assistant** 2026.11 of nieuwer.
* **De Marktplaats** (HACS) in je Home Assistant, om het op de makkelijke
  manier te installeren en bij te werken. Zonder kun je de bestanden met de
  hand kopiëren.
* **Internettoegang** voor Home Assistant: elke trein komt uit de eigen
  gepubliceerde gegevens van zijn spoorweg.
* Niets te betalen. 13 van de 33 spoorwegen hebben geen account nodig; de
  andere 20 hebben een eigen gratis sleutel nodig, en vier sleutels dekken ze
  allemaal ([hierboven](#aangezet-door-je-eigen-gratis-sleutel-of-account)).
* Home Assistant installeert de Python-pakketten die het nodig heeft
  (`saw-livetrack`, `gtfs-realtime-bindings` en `tzdata`) zelf, de eerste keer
  dat de integratie laadt.

---

## Installeren, stap voor stap

### Via de Marktplaats (aanbevolen)

1. Open in Home Assistant **Instellingen → Marktplaats** (HACS).
2. Zoek **Live Track Intercity Rail** en open het.
3. Kies **Download** (of **Installeren**).
4. **Herstart Home Assistant**: **Instellingen → Systeem → Reparaties** biedt
   de herstart aan, of gebruik **Instellingen → Systeem → Herstart**.

Vindt de zoekfunctie het niet, voeg het dan toe via de koppeling: kies **Via
koppeling toevoegen** (of het menu met de drie puntjes → **Aangepaste
repositories**), voer `StrausbergAutomationWorks/LiveTrackIntercityRail` in,
kies **Integratie** als om het type wordt gevraagd en ga daarna verder bij stap
3.

De Marktplaats biedt daarna elke nieuwe release aan als update.

### Met de hand

1. Download de broncode van de
   [nieuwste release](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/releases/latest).
2. Kopieer de map `custom_components/live_track_intercity_rail` daaruit naar
   de map `custom_components` van je Home Assistant-configuratiemap (maak
   `custom_components` aan als die er niet is).
3. Herstart Home Assistant.

Om met de hand bij te werken, vervang je de map door die van de nieuwe release
en herstart je.

---

## Instellen, stap voor stap

1. Open **Instellingen → Apparaten en diensten**.
2. Kies **Voeg integratie toe** (rechtsonder) en zoek naar **Live Track
   Intercity Rail**.
3. **Region** (regio): kies het land van de spoorweg. Alleen landen met
   minstens één spoorweg staan in de lijst. Kies **Verzend**.
4. **Railroad** (spoorweg): kies de spoorweg. Kies **Verzend**.
5. **API key** (API-sleutel): alleen voor NSW TrainLink, V/Line, de drie
   Nederlandse spoorwegen en de vijftien Zweedse spoorwegen. Plak je sleutel
   ([hoe je er een krijgt](#gratis-sleutels-die-meer-aanzetten-stap-voor-stap))
   en kies **Verzend**. De andere spoorwegen slaan deze stap over.

Dat is alles. De treinen verschijnen binnen een minuut of twee. Waar de lijnen
van een spoorweg uit zijn dienstregeling komen, gaan de treinen hun lijnen
volgen zodra de dienstregeling is gedownload, wat de eerste keer een paar
minuten kan duren. Om een andere spoorweg te volgen, voeg je de integratie
opnieuw toe. Dezelfde spoorweg twee keer wordt geweigerd.

### Wijzigen wat het toont: de opties

Open **Instellingen → Apparaten en diensten → Live Track Intercity Rail →
Configureer** (het tandwiel) bij de spoorweg die je wilt wijzigen. Er is één
optie:

| Optie | Wat het doet | Standaard |
|---|---|---|
| **Poll interval** (ophaalinterval) | hoe vaak de bron van de spoorweg wordt gelezen, 15 tot 600 seconden. Een korter interval dan de eigen verversing van de bron laat niets meer zien | per spoorweg: 15 seconden voor Renfe (Spain) en de drie Nederlandse spoorwegen; 60 seconden voor Brightline, NSW TrainLink, Irish Rail en SJ Nord; 30 seconden voor de andere |

---

## Gratis sleutels die meer aanzetten, stap voor stap

Twintig spoorwegen vragen elke gebruiker om een eigen sleutel, bij vier
aanbieders. Elk van deze sleutels is gratis, en iedereen die Live Track
Intercity Rail installeert, krijgt een eigen sleutel. Je plakt de sleutel als
de instellingsdialoog erom vraagt ([stap 5 hierboven](#instellen-stap-voor-stap)).
Alleen de sleutel wordt gevraagd: geen wachtwoord en geen geheim. De sleutel
wordt in Home Assistant bij de integratie bewaard, alleen naar zijn eigen
aanbieder gestuurd, en nooit in het logboek geschreven. Als de aanbieder hem
tien minuten lang weigert, vraagt Home Assistant je om een nieuwe.

### Transport for NSW (NSW TrainLink, New South Wales, Australië)

1. Open <https://opendata.transport.nsw.gov.au/>, kies **Register**, maak een
   account aan en log in.
2. Kies het pictogram van je gebruikersprofiel en dan **API Tokens**.
3. Typ een naam voor de sleutel en kies **CREATE API TOKEN**. Kopieer de
   sleutel meteen: de site toont hem maar één keer.
4. Plak hem in **API key** als je NSW TrainLink toevoegt. Plak alleen de
   sleutel: Live Track Intercity Rail zet het woord `apikey` er zelf voor.

### Transport Victoria (V/Line, Victoria, Australië)

1. Open <https://opendata.transport.vic.gov.au/>, kies **Login** en dan
   **Sign up**.
2. Voer je gegevens in en kies **Create Account**. Voer de code uit de e-mail
   in die je krijgt en kies **Confirm**.
3. Het portaal vraagt om een authenticator-app op je telefoon: scan er de
   QR-code mee, voer de code van de app in en kies **Confirm**. Log daarna in
   met je e-mailadres, je wachtwoord en de code van de app.
4. Kies **My Account** → **Profile** → **API tokens**. Je sleutel staat er
   al. Plak hem in **API key** als je V/Line toevoegt.

### NS (NS, Arriva en Keolis, Nederland)

1. Open <https://apiportal.ns.nl/>, kies **Inloggen** en dan **Externe
   bezoeker**.
2. Vul het formulier in en verstuur het. Een e-mail bevestigt de registratie.
   Het kan tot 5 minuten duren voordat de API's in het portaal verschijnen.
3. Open de pagina van de **Virtual Train API** (de treinposities van NS).
   Open onder **Related Products** het product, geef je abonnement een naam
   en kies **Subscribe**.
4. Als NS het abonnement heeft goedgekeurd, staat je sleutel op je
   profielpagina. Plak hem in **API key** als je NS, Arriva of Keolis
   toevoegt. Eén sleutel geldt voor alle drie.

### Trafikverket (de 15 Zweedse spoorwegen)

1. Open <https://data.trafikverket.se/oauth2/Account/register>.
2. Vul **Email**, **Displayname** (weergavenaam), **Password** (wachtwoord)
   en **Confirm password** in, vink **Accept license and Agreement** aan en
   kies **Register**.
3. Open <https://data.trafikverket.se/get-started> en kies **Create key**,
   onder **Create a key**. Log in met het account dat je hebt gemaakt en maak
   de sleutel aan.
4. Plak hem in **API key** als je een Zweedse spoorweg toevoegt. Eén sleutel
   geldt voor alle vijftien.

---

## De kaart op een dashboard zetten

De kaart is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
de kaart waarop elke Live Track-module tekent. **Hij wordt met Live Track
Intercity Rail geïnstalleerd**: niets te downloaden, niets te kopiëren, geen
bron toe te voegen.

1. Open een dashboard, kies het potlood (**Wijzig dashboard**) en dan **Voeg
   kaart toe**.
2. Scrol naar beneden en kies **Handmatig**.
3. Plak dit en kies **Bewaar**:

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

Andere Live Track-modules gaan op dezelfde manier in `entity_filter`: nog een
regel `- domain: geo_location` voor elke bron.

**Op de kaart:**

* Elke trein is een marker in de kleuren van zijn spoorweg, met zijn
  treinnummer of lijn als label. De treinen van Amtrak zijn sterren, die van
  VIA Rail dragen het esdoornblad, de InterCity-treinen van Irish Rail zijn
  klavertjes, en sommige treinen zijn afbeeldingen (elke spoorweg hieronder
  zegt welke).
* Bij de meeste spoorwegen wisselen de kleuren met de richting: de ene kant
  op bij het verlaten van de belangrijkste stad, de andere kant op
  ernaartoe.
* Een pijl toont de richting waarin de trein rijdt. Een stilstaande trein
  houdt zijn laatste richting. Afbeeldingen blijven rechtop en hebben geen
  pijl.
* **Wijs** een trein **aan** om zijn spoorweg, nummer, lijn en route te zien.
  **Klik** erop voor al zijn details, inclusief zijn volgende halte en zijn
  vertraging.

Als de bronnen van je dashboards in YAML worden ingesteld
(`lovelace: resource_mode: yaml`), kan er niets voor je worden geregistreerd:
een melding onder **Reparaties** geeft dan de precieze regels om aan
`configuration.yaml` toe te voegen. Ze zien er zo uit, met het eigen adres
van de integratie in plaats van de plaatshouders:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_intercity_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Elke Live Track-module heeft een kopie van de kaart en registreert die als
Home Assistant start. Samen houden ze precies één regel in **Instellingen →
Dashboards → Bronnen**: de nieuwste kaartversie die een van hen heeft, nooit
een oudere. Een kaart die je zelf via de Marktplaats hebt geïnstalleerd, wordt
met rust gelaten. Als je de laatste spoorweg van deze module verwijdert, gaat
de regel over naar een andere Live Track-module, of wordt hij verwijderd als
er geen meer is. Als de bestanden van de integratie worden verwijderd terwijl
haar spoorwegen nog zijn ingesteld, en er geen andere Live Track-module is
geïnstalleerd, verwijder dan zelf de regel in **Instellingen → Dashboards →
Bronnen**.

**Om de kaart in plaats daarvan met de hand te installeren**, volg je de
stappen in de [README van de kaart](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
Een regel die je zelf hebt gemaakt, voor een kopie onder `/local/` of op een
ander adres, wordt nooit gewijzigd of verwijderd. Zolang die de kaart laadt,
laat elke Live Track-module de kaart eraan over, ook als een module een nieuwere
release heeft, en niets in **Reparaties** meldt dat. Om terug te gaan naar de
kopie van de module, verwijder je je regel in **Instellingen → Dashboards →
Bronnen** en herstart je Home Assistant. Verwijder je het bestand van je kopie,
verwijder dan ook de regel: zolang een regel waarvan het bestand weg is blijft
staan, voegt de module geen eigen regel toe.

Elke andere kaart die `geo_location`-entiteiten toont, toont de treinen ook,
als gewone markers.

---

## Gebruiken in automatiseringen

Alles is een gewone Home Assistant-entiteit, dus de automatiseringseditor
werkt ermee, zonder code.

**Een melding op je telefoon als de gegevens van je spoorweg stoppen** (de
treinen verdwijnen dan van de kaart):

1. **Instellingen → Automatiseringen en scènes → Maak automatisering aan →
   Voeg automatisering toe**.
2. **Wanneer**: **Voeg trigger toe** → **Entiteit** → **Status gewijzigd**.
   Kies de entiteit **Trains in service** (treinen in dienst) van de
   spoorweg, en kies onder **Naar (optioneel)** **Niet beschikbaar**.
3. **Doe dan**: **Voeg actie toe**, zoek de meldingsactie van je telefoon (die
   draagt de naam van je telefoon) en voer een bericht in, bijvoorbeeld:

   ```text
   Geen intercitytreinen op de kaart: de gegevens van de spoorweg zijn gestopt
   ```

4. **Bewaar**.

**Andere ideeën:** een lamp die aangaat als een trein van Amtrak binnen 2 km
(1,2 mijl) van je huis in de Verenigde Staten is, via de afstand van de
markers; een telling op het dashboard van de treinen die VR in de loop van de
dag in Finland laat rijden; een bericht als de eerste trein van de dag van
Queensland Rail Travel vertrekt (Australië), via **Trains in service** dat
boven 0 stijgt.

---

## Alles op de kaart, in detail

### Treinen

Elke trein is één marker. Zijn status is zijn afstand tot je huis, in
kilometers. De marker verschijnt als de spoorweg de trein meldt, of als zijn
dienstregeling zegt dat hij rijdt, en wordt verwijderd als de trein uit de
gegevens van de spoorweg verdwijnt of zijn rit voorbij is.

* **Tussen twee meldingen** rijdt een trein langs zijn eigen lijn naar zijn
  volgende halte: met de snelheid die de spoorweg meldt, of, waar die er geen
  meldt, met de snelheid tussen zijn laatste twee meldingen. Hij rijdt nooit
  voorbij zijn volgende halte, en stopt met bewegen 30 minuten na de laatste
  melding. Een trein op een bekende lijn wordt op de lijn getekend; de eigen
  melding van de spoorweg wordt ernaast bewaard.
* **Als de gegevens van een spoorweg uitvallen**, blijven zijn treinen tot 10
  minuten lang rijden op hun laatste goede melding. Daarna zijn ze niet
  beschikbaar en verdwijnen ze van de kaart tot de gegevens terugkomen.
* **Te laat en zeer te laat**: waar de spoorweg zijn eigen regel voor een
  vertraagde trein publiceert, gebruikt de integratie die. Waar hij er geen
  publiceert, is een trein te laat naar de afstand die hij aflegt, met de
  drempels van Amtrak Status Maps (asm.transitdocs.com). Elke spoorweg
  hieronder zegt welke.

Op elke trein: `marker_label`, `train`, `line_name`, `observed_at` (wanneer
zijn melding klopte), `course_deg` (terwijl hij rijdt), `next_stop` en
`arrival_estimated_at` (waar bekend), `delay_min`, `late_threshold_min` en
`very_late_threshold_min`, `speed_kmh` (waar de spoorweg die meldt),
`attribution`, en, tussen twee meldingen, `previous_latitude`,
`previous_longitude`, `previous_observed_at` en `segment_duration_s`. Een
trein die langs zijn lijn wordt bewogen, draagt `position_source: estimated`,
met de melding van de spoorweg in `fix_latitude` en `fix_longitude`.

### Journey Beyond (Australië)

⚠ **Journey Beyond publiceert geen posities.** Elke trein wordt getekend uit
zijn gepubliceerde dienstregeling, overgenomen in een bestand dat met de
integratie wordt meegeleverd (vertrekken tot 29 december 2027), dus er wordt
niets gedownload. Elke trein wordt volgens zijn tijden op zijn lijn geplaatst,
als schatting gemarkeerd, zonder vertraging: een vertraagde of geannuleerde
trein wordt toch op tijd getekend. Elke dienst is zijn eigen afbeelding (de
kameel met ruiter, een vogel, een kangoeroe, een emoe), in zijn kleuren op de
heenweg en omgewisseld op de terugweg, zonder label: wijs hem aan om de trein
en zijn rit te zien.

### NSW TrainLink (New South Wales, Australië)

Uit de NSW TrainLink-feed van Transport for NSW, met je eigen sleutel, een
nieuwe positie ongeveer eens per minuut. Het label is het treinnummer. NSW-
oranje met een witte ring bij het verlaten van Sydney, omgewisseld ernaartoe.
De feed heeft geen snelheid, dus een trein rijdt langs zijn lijn met de
snelheid tussen zijn laatste twee posities. Te laat vanaf 11 minuten (NSW
TrainLink rekent een trein binnen 10 minuten als op tijd), zeer te laat vanaf
30.

### Queensland Rail Travel (Australië)

⚠ **Queensland Rail Travel publiceert geen posities.** Je Home Assistant leest
de tijden die de Service Updates-pagina van Queensland Rail Travel toont: de
lijst van de treinen van vandaag hoogstens elke 5 minuten, en de tijden van
elke trein hoogstens elke 5 minuten, van 30 minuten voor zijn vertrek tot 15
minuten na zijn aankomst. Elke trein wordt volgens die tijden op zijn lijn
geplaatst en als schatting gemarkeerd. Elke lijn is zijn eigen afbeelding, in
zijn kleuren bij het verlaten van Brisbane en omgewisseld ernaartoe, met het
treinnummer in een label ernaast. Te laat of zeer te laat wordt niet getoond.

### V/Line (Victoria, Australië)

Uit de V/Line-feed van Transport Victoria, met je eigen sleutel: de
langeafstandslijnen naar Albury, Ararat, Bairnsdale, Echuca, Maryborough,
Shepparton, Swan Hill en Warrnambool. Het label is het treinnummer. V/Line-
paars met een gele ring bij het verlaten van Melbourne, omgewisseld ernaartoe.
De feed heeft geen snelheid, dus een trein rijdt met de snelheid tussen zijn
laatste twee posities; na 10 minuten zonder nieuwe positie wordt hij naar zijn
volgende halte getimed. Te laat vanaf 11 minuten op de lange lijnen en 6 op de
korte (de eigen lijst van V/Line), zeer te laat vanaf 30.

### WA Trains (Western Australia, Australië)

⚠ **Er worden geen live posities gepubliceerd.** Elke trein wordt getekend
uit de dienstregeling van de Public Transport Authority of Western Australia:
langs zijn lijn geplaatst volgens zijn geplande tijden, als schatting
gemarkeerd, zonder vertraging. De dienstregeling wordt eens per dag
gecontroleerd. Het label is de eerste drie letters van de route: AUS
(Australind, paars), PRO (Prospector, oranje), MER (MerredinLink, groen) en
AVO (AvonLink, groen), in beide richtingen hetzelfde.

### VR (Finland)

Uit Digitraffic van Fintraffic, een nieuwe positie ongeveer elke 30 seconden.
Het label is het treintype en -nummer, zoals VR het schrijft (`IC 23`).
VR-groen met een donkere ring bij het verlaten van Helsinki, omgewisseld
ernaartoe. De gegevens hebben geen richting, dus de pijl volgt de lijn. Te
laat vanaf 6 minuten (VR rekent een trein als te laat als hij meer dan vijf
minuten vertraging heeft), zeer te laat vanaf 12.

* **De Kerstmanexpres**, van de eerste zondag van de advent tot 6 januari:
  een sneeuwpop op weg naar het noorden, een rendier op de terugweg, zonder
  nummer. Vanaf 12 minuten vertraging draait de figuur om de paar seconden om.
* **Het zomerhuisje**, van midzomeravond tot 31 juli: elke
  langeafstandstrein van VR wordt als een huisje getekend, met zijn nummer
  ernaast.

### Irish Rail (Ierland)

Uit de live dienst van Irish Rail en de dienstregeling van de National
Transport Authority. ⚠ Irish Rail meldt een trein alleen als hij
seinpunten passeert die een paar minuten uit elkaar liggen, dus elke trein
wordt getekend uit zijn dienstregeling en zijn laatste vertraging, langs zijn
route bewogen. Het label is het treinnummer zonder zijn letter (A700 toont
700). Een InterCity-trein is een groen klavertje met een oranje rand en
nummer bij het verlaten van Dublin, met omgewisselde kleuren ernaartoe. De
Enterprise is een zilveren schijf met een rode buitenring, een magenta band en
een magenta nummer; op weg naar Dublin is de schijf magenta. Te laat vanaf 10
minuten (de regel van de National Transport Authority), zeer te laat vanaf
20.

### NS, Arriva en Keolis (Nederland)

Uit de voertuiggegevens van NS, met je eigen sleutel, een nieuwe positie
ongeveer elke 10 seconden. Deze feed meldt de eigen snelheid en richting van
een trein, en beide worden doorgegeven. De volgende halte en de vertraging
komen uit de dienstregeling van OVapi; het spoor is de eigen kaart van NS van
zijn lijnen, eens per dag gedownload. Het label is het treinnummer. De treinen
van NS zijn geel met een NS-blauwe ring; de treinen van Arriva en Keolis
hebben voorlopig het eigen uiterlijk van de kaart. Te laat vanaf 3 minuten
(de eigen definitie van NS), zeer te laat vanaf 10.

### Vy, Go-Ahead Norge en SJ Nord (Noorwegen)

Uit Entur, elke spoorweg een eigen invoer. Het label is de lijncode (F4,
RE10, R50). De eigen kleur van de lijn met een witte ring bij het verlaten van
Oslo S (op een rit die Oslo S niet bereikt, de grootste eindstad), omgewisseld
ernaartoe. Entur publiceert geen snelheid en geen richting, dus een trein rijdt
met de snelheid tussen zijn laatste twee posities, en de pijl volgt zijn lijn.
In de lange tunnels van Oslo wordt een trein waarvan de posities stoppen langs
zijn lijn bewogen tot ze terugkomen. ⚠ **SJ Nord publiceert geen posities:**
elk van zijn treinen wordt volgens zijn verwachte tijden op zijn lijn
geplaatst. Te laat vanaf 4 minuten, en vanaf 6 op de F-lijnen en de lijnen naar
Göteborg (Zweden), de regel van Bane NOR en Vy; zeer te laat bij het dubbele.

### Renfe (Spain) en Renfe Regionals (Catalunya, Spanje)

**Renfe (Spain)** leest de langeafstandsfeed van Renfe, een nieuwe positie
ongeveer elke 15 seconden. Het label is het treinnummer; de dienst (AVE,
Avlo, Alvia enzovoort) staat in het aanwijsvak. AVE marineblauw, Avlo
turquoise, elke andere dienst Renfe-paars, elk gevuld bij het verlaten van
Madrid (op een rit die Madrid niet bereikt, de grootste eindstad) en
omgewisseld ernaartoe. Renfe publiceert geen routelijnen, dus de lijnen zijn
gebouwd uit OpenStreetMap en worden met de integratie meegeleverd. Renfe
publiceert geen regel voor een vertraagde trein, dus een trein is te laat naar
de lengte van zijn rit: vanaf 10 minuten tot 400 km (250 mijl), 15 tot 560 km
(350 mijl), 20 tot 725 km (450 mijl), 25 tot 885 km (550 mijl), 30 daarboven;
zeer te laat bij het dubbele.

**Renfe Regionals (Catalunya)** tekent de regionale lijnen R11 tot R17 van
Rodalies de Catalunya. Het label is het treinnummer, in de eigen kleur van de
lijn, gevuld bij het verlaten van Barcelona en omgewisseld ernaartoe. Buiten
Barcelona is een positie het laatste station dat een trein passeerde, dus de
trein wordt tussen stations getimed met de dienstregeling en zijn vertraging.
Te laat vanaf 10 minuten, zeer te laat vanaf 20, naar de lengte van de
langste lijn. Met beide spoorwegen van Renfe ingesteld wordt elke trein één
keer getekend.

### De Zweedse spoorwegen (Zweden)

Uit Trafikverket, met je eigen sleutel (één sleutel voor alle vijftien). Het
label is het treinnummer op het kaartje; het merk, het nummer en de
eindstations staan in het aanwijsvak. Elk merk heeft zijn eigen kleuren,
omgewisseld op weg naar Stockholm C (op een rit die Stockholm C niet bereikt,
de grootste eindstad). Trafikverket geeft een snelheid bij ongeveer de helft
van zijn posities; de andere treinen rijden met de snelheid tussen hun laatste
twee posities. Zweden publiceert geen routelijnen, dus de lijnen zijn gebouwd
uit OpenStreetMap en worden met de integratie meegeleverd. Te laat vanaf 6
minuten (Trafikverket rekent een trein als op tijd tot 5 minuten en 59
seconden), zeer te laat vanaf 12.

### VIA Rail (Canada)

Uit de eigen treinstatusgegevens van VIA Rail. Elke trein is een schijf met
het esdoornblad en een band in de kleur van zijn routegroep (Atlantic,
Western, Ontario en Quebec, Prince Rupert, Churchill, Sudbury naar White
River, Montréal scenic), met het treinnummer in een rechtopstaand label.
Oneven nummers hebben een gele schijf, even nummers een schijf in de kleur van
de band. Een trein zonder nieuwe positie rijdt naar zijn volgende halte om aan
te komen op de eigen schatting van VIA. VIA publiceert geen regel voor een
vertraagde trein, dus een trein is te laat vanaf 10 minuten op de corridor
Québec City naar Windsor en vanaf 60 elders (de waarden van Amtrak Status
Maps voor VIA), zeer te laat bij het dubbele.

### Amtrak (Verenigde Staten)

Amtrak publiceert geen open live gegevens. Amtraker geeft de eigen
treinvolging van Amtrak door, met een nieuwe positie elke 3 tot 5 minuten, en
de integratie beweegt elke trein langs zijn lijn met de snelheid die Amtrak
meldt. Elke trein is een ster met zijn nummer erdoor, in de kleuren van zijn
route (de Northeast-routes, Cascades, Pacific Surfliner, Acela en meer), anders
de vlagster. De Maple Leaf (New York naar Toronto) verandert langzaam tussen
de ster van Amtrak en het embleem van VIA. Een trein die bij de grens in
Lacolle, Rouses Point of Niagara Falls stilstaat, toont "Customs" in plaats
van zijn vertraging. Te laat vanaf 16 minuten (Amtrak rekent een trein binnen
15 minuten als op tijd), zeer te laat vanaf 30. Hetzelfde treinnummer kan op
twee of drie dagen tegelijk rijden, dus elke rit is zijn eigen marker.

### Brightline (Verenigde Staten)

Uit de eigen feed van Brightline, een nieuwe positie ongeveer elke 60
seconden. Het label is het ritnummer, in zwart met een witte rand, op een
schijf in de kleur van de bestemming van de trein, met een zwarte ring. Een
positie die ouder is dan 5 minuten wordt niet gebruikt. De feed heeft geen
snelheid, dus een trein rijdt met de snelheid tussen zijn laatste twee
posities. Brightline publiceert geen regel voor een vertraagde trein, dus een
trein is te laat vanaf 10 minuten, zeer te laat vanaf 20, naar de lengte van
zijn rit.

---

## Alle entiteiten die het aanmaakt

Per spoorweg:

| Entiteit | Wat het is |
|---|---|
| `sensor.<spoorweg>_trains_in_service` | **Trains in service** (treinen in dienst): hoeveel treinen de spoorweg nu op de kaart laat rijden. Voor Amtrak: `sensor.amtrak_trains_in_service` |
| `geo_location.<spoorweg>_train_…` | één per trein (`geo_location.amtrak_train_5_17`); hij komt en gaat met de trein. Elk draagt `source: live_track_intercity_rail`, en zijn status is zijn afstand tot je huis in kilometers |

De entiteit-ID van een marker komt van de spoorweg en de rit, nooit van zijn
label: `geo_location.amtrak_train_5_17` is trein 5 van Amtrak die op de 17e
van de maand vertrok, dus een trein houdt zijn hele rit dezelfde entiteit-ID,
en een andere rit met hetzelfde nummer krijgt een eigen. De marker wordt
verwijderd als de rit uit de gegevens van de spoorweg verdwijnt of eindigt. De
markers hebben geen unieke ID, net als geen enkele Live Track-kaartmarker,
dus je kunt ze in de interface niet hernoemen, verbergen of aan een ruimte
toewijzen. De sensor heeft een unieke ID en kun je hernoemen.

Attributen die bij elke ophaalbeurt veranderen, de posities en tijden van de
markers, worden in de geschiedenis van Home Assistant opgeslagen, zoals bij
elke entiteit. De sensor heeft geen attributen, dus hem bewaren kost weinig,
en hij is de registratie van hoeveel treinen er op een dag reden. Om de
markers buiten de geschiedenis te houden, zet je dit in `configuration.yaml`
en herstart je:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_train_*
```

Heeft je `configuration.yaml` al een `recorder:`-sectie, voeg dan alleen het
patroon `geo_location.*_train_*` toe, onder `exclude:` en `entity_globs:`. Het
patroon past alleen op de treinmarkers van deze module. Een kaart die is
ingesteld om de geschiedenis te tekenen, heeft dan geen spoor meer om te
tekenen.

---

## Wat het verstuurt en downloadt

**Over je locatie.** Niets. De positie van je huis wordt alleen binnen je
Home Assistant gebruikt, om de afstand van elke trein te geven. Je sleutel,
waar een spoorweg er een nodig heeft, wordt alleen naar de aanbieder van die
spoorweg gestuurd. Niets anders over jou wordt ergens heen gestuurd. Elke
dienst ziet je internetadres, zoals elke website.

**Hoeveel.** Elke live bron wordt bij elke ophaalbeurt gelezen, standaard met
het eigen interval van de spoorweg (**Poll interval**, 15 tot 600 seconden),
of minder vaak waar de tabel dat zegt. Waar meerdere Live Track-modules of
spoorwegen dezelfde bron lezen, leest één gedeelde client die één keer voor
allemaal. Gemeten op 19 november 2026, 02:44 tot 02:49 UTC:

| Spoorweg | Live gegevens, één keer lezen | Dienstregeling en lijnen |
|---|---|---|
| Journey Beyond (Australië) | geen: er wordt niets gedownload | geen: de dienstregeling en lijnen worden met de integratie meegeleverd |
| NSW TrainLink (Australië) | 124 KB uit twee feeds, hoogstens eens per 55 seconden | 40 MB, als gewijzigd, dagelijks gecontroleerd |
| Queensland Rail Travel (Australië) | de lijst, 5,5 KB, elke 5 minuten; de tijden van elke rijdende trein, 6 tot 8 KB, elke 5 minuten | geen: de lijnen worden met de integratie meegeleverd |
| V/Line (Australië) | 14 KB uit twee feeds | 58 MB (het deel van V/Line uit het bestand van 311 MB van Transport Victoria, apart gelezen), als gewijzigd, dagelijks gecontroleerd |
| WA Trains (Australië) | geen: er bestaat geen live feed | 28 MB, als gewijzigd, dagelijks gecontroleerd |
| VR (Finland) | 1,4 KB gecomprimeerd voor de posities; de treinen van de dag, de eerste keer 0,5 MB gecomprimeerd, daarna alleen de wijzigingen, eens per minuut | 3,1 MB, elke dag |
| Irish Rail (Ierland) | 0,2 KB, hoogstens eens per 55 seconden | 6,6 MB, als gewijzigd, dagelijks gecontroleerd; de stationslijst, 46 KB, eens per week |
| NS, Arriva, Keolis (Nederland) | 1,5 KB, hoogstens eens per 9 seconden; vertragingen van OVapi, 5,3 MB, elke 5 minuten en alleen als gewijzigd | de dienstregeling van OVapi, 267 MB, hoogstens eens per week en alleen als gewijzigd; de spoorkaart van NS, 1,3 MB, elke dag |
| Vy, Go-Ahead Norge, SJ Nord (Noorwegen) | Vy 510 KB uit twee feeds, Go-Ahead Norge 7 KB, SJ Nord 0,7 KB eens per minuut | Vy 67 MB, Go-Ahead Norge 20 MB, SJ Nord 26 MB, als gewijzigd, dagelijks gecontroleerd |
| Renfe (Spain) | 2,1 KB uit twee feeds | 0,7 MB, elke dag; de lijnen worden met de integratie meegeleverd |
| Renfe Regionals (Catalunya, Spanje) | 0,2 KB uit twee feeds die alle lokale netten van Renfe dragen | 16 MB, elke dag |
| De Zweedse spoorwegen (Zweden) | de eerste keer 474 KB, daarna 5 tot 9 KB aan wijzigingen | geen; de stationslijst, 0,15 MB, elke dag; de lijnen worden met de integratie meegeleverd |
| VIA Rail (Canada) | 353 KB, gecomprimeerd verstuurd als 33 KB | 1,0 MB, eens per week |
| Amtrak (Verenigde Staten) | 1,2 MB, gecomprimeerd verstuurd als 113 KB | 18,6 MB, eens per week |
| Brightline (Verenigde Staten) | 1,3 KB uit twee feeds | 29 KB, eens per week |

⚠ Toen dit werd gemeten, was het dag in Australië, avond in Noord-Amerika en
nacht in Europa. Een live feed is 's nachts het kleinst: overdag zijn de
Europese feeds groter dan de tabel laat zien.

**Na een fout.** De treinen blijven tot 10 minuten rijden op de laatste goede
gegevens; daarna worden ze als niet beschikbaar gemarkeerd tot de bron
antwoordt. Een dienstregeling die niet kan worden gedownload, wordt later
opnieuw geprobeerd, en de kopie die je hebt blijft in gebruik. Als een
aanbieder je sleutel tien minuten lang blijft weigeren, vraagt Home Assistant
om een nieuwe.

**Op schijf.** Dienstregelingen en routelijnen worden in de map `.storage`
van Home Assistant bewaard onder namen die beginnen met `saw_`, gedeeld met de
andere Live Track-modules die dezelfde spoorweg lezen. Als je Live Track
Intercity Rail verwijdert en geen andere Live Track-module ze gebruikt, kun je
ze met de hand verwijderen.

---

## Help het groeien

Live Track Intercity Rail groeit nog. We voegen spoorwegen en landen toe zodra
we ze vinden, en we willen weten wat je hierna zou willen.

### Iets voorstellen

Ontbreekt je land of je spoorweg? Klopt er iets niet, of is iets moeilijk te
begrijpen? Laat het ons weten op de manier die voor jou het makkelijkst is:

* [**Vul een kort formulier in**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=nl.yml)
  in het Nederlands. Je hebt een gratis GitHub-account nodig.
* **Stuur een e-mail** naar
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Geen account nodig.

Hoe dan ook, het helpt als je ons vertelt:

* wat je graag zou zien, en waar ter wereld;
* een link naar waar de gegevens worden gepubliceerd, als je die kent (een
  open-datapagina, een openbare feed, de website van een dienst): niet nodig,
  maar het helpt;
* de taal van je Home Assistant, als het probleem de formulering of een
  vertaling is.

Schrijf in het Engels of in je eigen taal, wat voor jou het makkelijkst is.

### Zelf iets toevoegen, met onze hulp

Wil je zelf iets toevoegen, dan helpen we je daarbij, van de eerste vraag tot
de afgeronde release. Je hoeft geen ontwikkelaar te zijn om te beginnen:

* **Een vertaling.** De teksten in de instellingsdialoog zijn een korte lijst
  zinnen in één tekstbestand. We laten je zien welk bestand en welke regels.
* **Een nieuwe spoorweg.** Vertel ons waar de gegevens worden gepubliceerd. We
  kunnen de code samen schrijven, of de jouwe nakijken.
* **Testen waar je woont.** Installeer het, bekijk jouw deel van de kaart, en
  vertel ons wat klopt en wat niet.
* **Een verbetering van deze README.** Als een stap niet overeenkwam met wat
  je zag, vertel ons wat je zag.

[**Vertel ons wat je in gedachten hebt**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=nl.yml)
of schrijf naar
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
en we antwoorden met de volgende stappen.

---

## Talen

Deze README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), **Nederlands**, [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md),
[Suomi](README.fi.md), [Svenska](README.sv.md),
[Norsk bokmål](README.nb.md), [Gaeilge](README.ga.md). Elke vertaalde README
is volledig. Geen enkele is nog door een moedertaalspreker gelezen. Is een van
deze talen de jouwe, laat ons dan weten of de README goed leest: zie
[Help het groeien](#help-het-groeien).

De instellingsdialoog en de opties zijn voorlopig alleen in het Engels, in welke
taal je Home Assistant ook staat. Spreek je een andere taal, dan kun je ze zelf
vertalen: het is een korte lijst zinnen in één bestand, en [we helpen je
daarbij](#zelf-iets-toevoegen-met-onze-hulp).

Een fout gevonden in een vertaling, of een andere taal nodig? Laat het ons
weten op <https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues>,
of [vertaal het met onze hulp](#zelf-iets-toevoegen-met-onze-hulp).

---

## Vermeldingen en licenties

Elke live bron wordt tijdens het draaien gelezen, door je Home Assistant;
niets uit een live feed staat in deze repository. Elke trein vermeldt zijn
bron in zijn attribuut `attribution`. De voorwaarden van elke bron binden jou,
als degene die de gegevens ontvangt.

* **Amtraker** (amtraker.com), dat de treinvolging van Amtrak doorgeeft
  (Verenigde Staten): gegevens onder de
  [Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/),
  naamsvermelding verplicht. De eigen dienstregeling van **Amtrak** voor de
  routelijnen.
* **Brightline** (Verenigde Staten): zijn GTFS- en GTFS-Realtime-feeds;
  Brightline publiceert geen voorwaarden.
* **VIA Rail** (Canada): zijn treinstatusgegevens, waarvoor VIA geen
  voorwaarden publiceert; zijn dienstregeling onder de Open Government Licence
  - Canada 2.0 ([developer resources](https://www.viarail.ca/en/developer-resources)).
* **Fintraffic / digitraffic.fi** (Finland): gegevens onder CC BY 4.0.
* **Transport for NSW** (Australië): gegevens onder CC BY 4.0
  ([datalicentie](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australië): gegevens onder CC BY 4.0
  ([open data](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Queensland Rail Travel** (Australië): de tijden die zijn Service
  Updates-pagina toont, gelezen door je Home Assistant; zie de
  [copyrightpagina van Queensland Rail](https://www.queenslandrailtravel.com.au/copyright).
  Niets van Queensland Rail Travel wordt met de integratie meegeleverd.
* **Journey Beyond** (Australië): zijn gepubliceerde dienstregelingen,
  overgenomen in `data/journey_beyond_timetable.json`; Journey Beyond
  publiceert er geen voorwaarden voor.
* **Public Transport Authority of Western Australia**: dienstregelingsgegevens
  gratis beschikbaar via www.transperth.wa.gov.au
  ([spatial data access](https://www.transperth.wa.gov.au/About/Spatial-Data-Access);
  niet CC BY).
* **Renfe** (Spanje): gegevens onder CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)).
* **Entur** (Noorwegen): bevat gegevens onder de Noorse licentie voor open
  overheidsgegevens ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)),
  verspreid door Entur.
* **Trafikverket** (Zweden): gegevens onder [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Ierland): live gegevens; Irish Rail publiceert geen
  voorwaarden. Dienstregeling van de
  [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Ierland), CC BY 4.0, geleverd zoals ze is.
* **NS** (Nederland): voertuiggegevens en spoorkaart, met je eigen sleutel,
  onder de voorwaarden van het [NS API-portaal](https://apiportal.ns.nl/).
  Dienstregeling en vertragingen van [OVapi](https://gtfs.ovapi.nl/), CC0.
* **Bestanden meegeleverd in `data/`**: routelijnen voor Journey Beyond,
  Queensland Rail Travel, Renfe (Spain) en Zweden, gebouwd uit
  [OpenStreetMap](https://www.openstreetmap.org/copyright), © OpenStreetMap-
  bijdragers, onder de
  [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/);
  de gemeenten van de eindstations van de ritten van Renfe (OpenStreetMap,
  ODbL 1.0) en hun inwonertallen (Wikidata-eigenschap P1082, CC0, anders
  OpenStreetMap); inwonertallen van Zweedse eindsteden van Statistics Sweden
  (SCB) en Trafikverket, beide CC0 1.0; inwonertallen van Noorse eindsteden
  van Statistics Norway, tabel 04859, CC BY 4.0.
* **De kaart** is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, een kopie van [ha-map-card](https://github.com/nathan-gs/ha-map-card)
  door nathan-gs, MIT, meegeleverd in `frontend/`. De kaarttegels en hun
  vermeldingen staan in zijn README.

Geen van deze organisaties heeft deze integratie gemaakt of goedgekeurd.

**Code**: MIT, in [LICENSE](LICENSE). De bestanden in `data/` houden de
licenties van hun bronnen, hierboven genoemd.

**Voor ontwikkelaars:** elke spoorweg is één module in
`custom_components/live_track_intercity_rail/operators/`, die een
bronadapter in `sources/` leest; de meegeleverde routelijnen worden opnieuw
gebouwd met de scripts in `tools/` (`journey_beyond.py`, `qrt_lines.py`,
`renfe_spain_lines.py`, `sweden_lines.py`). De tests draaien met
`python -m unittest discover -s tests`.

---

## Trefwoorden

Home Assistant treinen · Home Assistant trein volgen · live treinkaart ·
intercity · langeafstandstreinen · treinen live · GTFS-Realtime · Amtrak ·
Amtraker · Brightline · VIA Rail · trains en temps réel · VR · kaukojunat ·
NSW TrainLink · XPT · V/Line · The Ghan · Indian Pacific · Spirit of
Queensland · Transwa · Renfe · AVE · Avlo · Alvia · Rodalies · trenes en
tiempo real · Vy · SJ Nord · tog i sanntid · SJ · Snälltåget · Öresundståg ·
tåg i realtid · Irish Rail · Enterprise · traenacha beo · NS Intercity ·
Arriva · Keolis · Zugverkehr · treni in tempo reale · togtrafik · 火车实时地图 ·
geo_location · kaart · Lovelace · HACS · Marktplaats · Live Track · LiveTrack ·
StrausbergAutomationWorks

---

**Erkenning.** StrausbergAutomationWorks erkent de inheemse volken van alle
landen en wateren op deze kaart, overal ter wereld, en betuigt zijn respect aan
hun Elders, van vroeger en nu.
