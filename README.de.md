# Live Track Intercity Rail

[English](README.md) · **Deutsch** · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · [Gaeilge](README.ga.md) · [Alle Sprachen](#sprachen)

**Fernzüge für Home Assistant, auf einer Karte.** Live Track Intercity Rail
zeigt jeden Zug der Fern- und Intercity-Bahnen, die Sie wählen, auf Ihrer
Home-Assistant-Karte: wo er ist, seine Nummer, ob er nach der eigenen Regel
der Bahn verspätet ist, und seinen nächsten Halt. Jede Bahn wird einzeln
hinzugefügt, aus ihren eigenen veröffentlichten Daten.

> **Live Track Intercity Rail ist ein Modul von Live Track**, einer Familie von
> Home-Assistant-Integrationen, die alles, was sich bewegt, und das Wetter,
> durch das es sich bewegt, auf einer gemeinsamen Karte zeichnen: Flugzeuge,
> Schiffe, Züge und Wetter. Installieren Sie es allein oder neben den anderen
> Modulen ([Liste unten](#teil-von-live-track-die-anderen-module)).

> **Es wächst und ist offen für Ideen.** Live Track Intercity Rail deckt heute
> 33 Bahnen in 9 Ländern auf 3 Kontinenten ab, und wir fügen weitere Bahnen
> und Länder hinzu. Fehlt Ihre? [Schlagen Sie sie vor](#helfen-sie-mit-es-zu-erweitern),
> oder fügen Sie sie selbst hinzu: Wir helfen Ihnen dabei.

**Status: 0.1.3, veröffentlicht.** Im Katalog des Marketplace ([Installation
unten](#installation-schritt-für-schritt)).

Eigene Arbeit von StrausbergAutomationWorks. Nicht verbunden mit und nicht
unterstützt von Amtrak, Amtraker, Brightline, VIA Rail, Fintraffic, VR,
Transport for NSW, NSW TrainLink, Transport Victoria, V/Line, Queensland
Rail, Journey Beyond, der Public Transport Authority of Western Australia,
Transwa, Renfe, Rodalies de Catalunya, Entur, Vy, Go-Ahead Norge, SJ Nord,
Trafikverket, SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg,
Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget,
Värmlandstrafik, Tågab, Inlandsbanan, Irish Rail, der National Transport
Authority (Irland), NS, Arriva, Keolis, OVapi oder einer anderen Bahn.

---

## Inhalt

1. [Alles, was es kann](#alles-was-es-kann)
2. [Wo es funktioniert](#wo-es-funktioniert)
3. [Teil von Live Track: die anderen Module](#teil-von-live-track-die-anderen-module)
4. [Bevor Sie beginnen](#bevor-sie-beginnen)
5. [Installation, Schritt für Schritt](#installation-schritt-für-schritt)
6. [Einrichtung, Schritt für Schritt](#einrichtung-schritt-für-schritt)
7. [Kostenlose Schlüssel, die mehr freischalten, Schritt für Schritt](#kostenlose-schlüssel-die-mehr-freischalten-schritt-für-schritt)
8. [Die Karte auf ein Dashboard bringen](#die-karte-auf-ein-dashboard-bringen)
9. [In Automationen verwenden](#in-automationen-verwenden)
10. [Alles auf der Karte im Detail](#alles-auf-der-karte-im-detail)
11. [Alle Entitäten, die es anlegt](#alle-entitäten-die-es-anlegt)
12. [Was es sendet und herunterlädt](#was-es-sendet-und-herunterlädt)
13. [Helfen Sie mit, es zu erweitern](#helfen-sie-mit-es-zu-erweitern)
14. [Sprachen](#sprachen)
15. [Danksagungen und Lizenzen](#danksagungen-und-lizenzen)
16. [Stichwörter](#stichwörter)

---

## Alles, was es kann

### Auf der Karte, ohne etwas einzurichten

Sie fügen eine **Bahn** hinzu: Sie wählen ein Land, dann eine seiner
Fernbahnen. Alles unten erscheint dann für diese Bahn. Fügen Sie die
Integration für jede weitere Bahn, die Sie möchten, erneut hinzu.

| Was | Wo | Woher |
|---|---|---|
| **Züge im Einsatz**: eine Markierung je Zug, beschriftet mit seiner Zugnummer oder seiner Linie, in den Farben der Bahn, in seine Fahrtrichtung gedreht | jede Bahn | die eigenen veröffentlichten Daten jeder Bahn |
| **Verspätung**: ein Zug erscheint verspätet oder stark verspätet nach der eigenen Regel der Bahn; wo eine Bahn keine Regel veröffentlicht, nach der Länge seiner Fahrt | jede Bahn, die Verspätungen meldet | der eigene Feed jeder Bahn |
| **Nächster Halt und seine Zeit**: der Bahnhof, an dem ein Zug als Nächstes hält, und wann er dort erwartet wird | jede Bahn, deren Feed oder Fahrplan das angibt | Feed und Fahrplan jeder Bahn |
| **Züge, die den Gleisen folgen**: zwischen zwei Meldungen fährt ein Zug auf seiner eigenen Strecke mit seiner letzten Geschwindigkeit weiter, nicht quer über die Karte | jede Bahn, deren Strecke bekannt ist | der Fahrplan jeder Bahn, oder mit der Integration ausgelieferte Strecken |
| **Züge nach Fahrplan**: wo eine Bahn keine Positionen veröffentlicht, wird jeder Zug nach seinen Zeiten auf seine Strecke gesetzt und als Schätzung gekennzeichnet | Journey Beyond, Queensland Rail Travel und WA Trains (Australien), SJ Nord (Norwegen); Irish Rail mit seiner letzten Verspätung | Fahrplan oder Zeiten jeder Bahn |
| **Bilder für manche Züge**: der Santa Claus Express und ein Sommerhaus (Finnland), die Tiere der Züge von Journey Beyond, ein Bild für jede Linie von Queensland Rail Travel | Finnland, Australien | für diese Integration gezeichnet |
| **Halt an der Grenze**: ein Zug, der an einem Grenzübergang zwischen den Vereinigten Staaten und Kanada steht, zeigt „Customs" statt seiner Verspätung | Amtrak-Züge von und nach Kanada | die Positionen von Amtrak |
| **Ein Zähler je Bahn**: Züge im Einsatz | jede Bahn | dieselben Daten |

### Mit Ihrem eigenen kostenlosen Schlüssel oder Konto eingeschaltet

| Kostenloser Schlüssel oder Konto | Was es hinzufügt |
|---|---|
| Schlüssel von **Transport for NSW Open Data** | die Regionalzüge von NSW TrainLink (New South Wales, Australien) |
| Schlüssel von **Transport Victoria Open Data** | die Fernzüge von V/Line (Victoria, Australien) |
| Schlüssel des **NS API portal** | NS Intercity, die Regionalzüge von Arriva und Keolis (Niederlande); ein Schlüssel für alle drei |
| Schlüssel von **Trafikverket** | die 15 schwedischen Bahnen; ein Schlüssel für alle fünfzehn |

Jeder ist in wenigen Minuten zu bekommen: [Schritt für Schritt unten](#kostenlose-schlüssel-die-mehr-freischalten-schritt-für-schritt).
Die anderen 13 Bahnen brauchen keinen Schlüssel.

---

## Wo es funktioniert

| Region | Was Sie bekommen | Woher | Benötigt |
|---|---|---|---|
| **Australien**: im ganzen Land | Journey Beyond: The Ghan, The Ghan Expedition, Indian Pacific, Great Southern, The Overland, nur nach Fahrplan ([warum](#journey-beyond-australien)) | Journey Beyond | nichts |
| **Australien**: New South Wales | die Regionalzüge von NSW TrainLink (XPT und Xplorer), auch nach Queensland, Victoria und ins Australian Capital Territory | Transport for NSW | einen kostenlosen Schlüssel |
| **Australien**: Queensland | Queensland Rail Travel: Spirit of Queensland, Spirit of the Outback, Tilt Train, Westlander, Inlander, Kuranda Scenic Railway, Gulflander, nach ihren veröffentlichten Zeiten ([warum](#queensland-rail-travel-australien)) | Queensland Rail Travel | nichts |
| **Australien**: Victoria | die Fernzüge von V/Line (seine Pendlerlinien sind in Live Track Commuter Rail), auch nach New South Wales | Transport Victoria | einen kostenlosen Schlüssel |
| **Australien**: Western Australia | WA Trains: der Australind, der Prospector, der MerredinLink und der AvonLink, nur nach Fahrplan ([warum](#wa-trains-western-australia-australien)) | Public Transport Authority of Western Australia | nichts |
| **Europa**: Finnland | die Fernzüge von VR | Fintraffic Digitraffic | nichts |
| **Europa**: Irland | die InterCity-Züge von Irish Rail und der Enterprise von Dublin nach Belfast (Vereinigtes Königreich) | Irish Rail, National Transport Authority | nichts |
| **Europa**: Niederlande | NS Intercity und die Regionalzüge von Arriva (Arriva, RRReis, Blauwnet) und Keolis (Blauwnet, RRReis); die Sprinter von NS sind in Live Track Commuter Rail | NS, OVapi | einen kostenlosen Schlüssel |
| **Europa**: Norwegen | die Linien F, RE, RX und R von Vy (F1 auch nach Schweden), F5 und R50 von Go-Ahead Norge, F6, F7 und R60 bis R75 von SJ Nord | Entur | nichts |
| **Europa**: Spanien | die Züge AVE, Avlo, Alvia, Avant, Euromed, Intercity, MD und Regional von Renfe, auch nach Frankreich und Portugal; die Regionallinien R11 bis R17 von Rodalies de Catalunya | Renfe | nichts |
| **Europa**: Schweden | SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget, Värmlandstrafik, Tågab und Inlandsbanan, jede als eigene Bahn; Öresundståg auch nach Dänemark | Trafikverket | einen kostenlosen Schlüssel |
| **Nordamerika**: Kanada | VIA Rail, jede Strecke | VIA Rail | nichts |
| **Nordamerika**: Vereinigte Staaten | Amtrak, jede Strecke, auch nach Kanada | Amtraker | nichts |
| **Nordamerika**: Vereinigte Staaten | Brightline (Florida) | Brightline | nichts |

Nicht auf der Liste? [Sagen Sie es uns](#helfen-sie-mit-es-zu-erweitern). Wo
jemand die Daten offen veröffentlicht, sehen wir uns an, sie hinzuzufügen.

⚠ **Ein Zug ist nur so gut wie die Daten seiner Bahn.** Manche Bahnen melden
einen Zug alle paar Sekunden, manche alle paar Minuten, manche nur, wenn er
Signale passiert, und manche veröffentlichen gar keine Positionen. Die
Grenzen jeder Bahn stehen unter
[Alles auf der Karte im Detail](#alles-auf-der-karte-im-detail).

⚠ **Es sind nicht die amtlichen Angaben der Bahn.** Prüfen Sie vor der Reise
die eigene App oder Website der Bahn.

---

## Teil von Live Track: die anderen Module

Live Track ist eine Reihe von Home-Assistant-Integrationen, eine für jede Art
von beweglichem Ding, alle auf derselben Kartenkarte gezeichnet. Jede
funktioniert allein; zusammen ergeben sie ein lebendiges Bild. Sie teilen sich
die Kartenkarte und eine Python-Bibliothek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
sodass eine weitere installierte Integration keine zusätzlichen Anfragen an
eine Quelle stellt, die eine andere bereits liest.

| Modul | Was es auf die Karte bringt | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | Flugzeuge über Ihnen per ADS-B, mit Routen und Typsymbolen | veröffentlicht |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | Schiffe und Boote per AIS, in Ihrer Nähe oder irgendwo | veröffentlicht |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | Nahverkehrszüge in Nordamerika, Europa und Australien | veröffentlicht |
| **Live Track Intercity Rail** | Intercity- und Fernzüge in Nordamerika, Europa und Australien (dieses Modul) | veröffentlicht |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | Flugzeuge und Schiffe der Einwanderungs- und Bundespolizeibehörden, aus öffentlichen Listen | veröffentlicht |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | Wetter, Stürme und Naturgefahren | veröffentlicht |
| [Live Track Internet](https://github.com/StrausbergAutomationWorks/LiveTrackInternet) | Internetausfälle, Seekabel und Landverbindungen | veröffentlicht |
| Live Track Stations | Abfahrtstafeln und „Zeit zu gehen“-Hinweise für jeden Bahnhof | geplant |
| Live Track Satellites | Satelliten, die über Sie hinwegziehen | geplant |
| Live Track Freight Trains | Güter- und Arbeitszüge, wo Bahnen sie veröffentlichen | geplant |
| Live Track Transit | Stadtbusse, Straßenbahnen, Fähren und U-Bahnen | geplant |
| Live Track Intercity Buses | Fernbusse und Regionalbusse | geplant |
| Live Track Commuter Buses | Pendlerbusse | geplant |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | die gemeinsame Kartenkarte, auf der jedes Modul zeichnet | veröffentlicht, mit jedem Modul installiert |

Alles ist kostenlos und quelloffen. Nichts wird für Sponsoren zurückgehalten.

---

## Bevor Sie beginnen

* **Home Assistant** 2026.11 oder neuer.
* **Der Marketplace** (HACS) in Ihrem Home Assistant, um es auf dem einfachen
  Weg zu installieren und zu aktualisieren. Ohne ihn können Sie die Dateien
  von Hand kopieren.
* **Internetzugang** für Home Assistant: Jeder Zug kommt aus den eigenen
  veröffentlichten Daten seiner Bahn.
* Nichts zu bezahlen. 13 der 33 Bahnen brauchen kein Konto; die anderen 20
  brauchen einen eigenen kostenlosen Schlüssel, und vier Schlüssel decken sie
  alle ab ([oben](#mit-ihrem-eigenen-kostenlosen-schlüssel-oder-konto-eingeschaltet)).
* Home Assistant installiert die Python-Pakete, die es braucht
  (`saw-livetrack`, `gtfs-realtime-bindings` und `tzdata`), selbst, wenn die
  Integration zum ersten Mal lädt.

---

## Installation, Schritt für Schritt

### Über den Marketplace (empfohlen)

1. Öffnen Sie in Home Assistant **Einstellungen → Marketplace** (HACS).
2. Suchen Sie nach **Live Track Intercity Rail** und öffnen Sie es.
3. Wählen Sie **Herunterladen** (oder **Installieren**).
4. **Starten Sie Home Assistant neu**: **Einstellungen → System → Reparaturen**
   bietet den Neustart an, oder nutzen Sie **Einstellungen → System → Neu
   starten**.

Findet die Suche es nicht, fügen Sie es per Link hinzu: wählen Sie **Über Link
hinzufügen** (oder das Dreipunktmenü → **Benutzerdefinierte Repositorys**),
geben Sie `StrausbergAutomationWorks/LiveTrackIntercityRail` ein, wählen Sie
**Integration**, wenn nach dem Typ gefragt wird, und fahren Sie dann mit Schritt
3 fort.

Der Marketplace bietet dann jede neue Veröffentlichung als Aktualisierung an.

### Von Hand

1. Laden Sie den Quellcode der
   [neuesten Veröffentlichung](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/releases/latest)
   herunter.
2. Kopieren Sie dessen Ordner `custom_components/live_track_intercity_rail` in
   den Ordner `custom_components` Ihres Home-Assistant-Konfigurationsordners
   (legen Sie `custom_components` an, falls es ihn nicht gibt).
3. Starten Sie Home Assistant neu.

Zum Aktualisieren von Hand ersetzen Sie den Ordner durch den der neuen
Veröffentlichung und starten neu.

---

## Einrichtung, Schritt für Schritt

1. Öffnen Sie **Einstellungen → Geräte & Dienste**.
2. Wählen Sie **Integration hinzufügen** (unten rechts) und suchen Sie nach
   **Live Track Intercity Rail**.
3. **Region**: Wählen Sie das Land der Bahn. Nur Länder mit mindestens einer
   Bahn werden aufgeführt. Wählen Sie **OK**.
4. **Railroad** (die Bahn): Wählen Sie die Bahn. Wählen Sie **OK**.
5. **API key** (der Schlüssel): nur für NSW TrainLink, V/Line, die drei
   niederländischen Bahnen und die fünfzehn schwedischen Bahnen. Fügen Sie
   Ihren Schlüssel ein
   ([wie Sie einen bekommen](#kostenlose-schlüssel-die-mehr-freischalten-schritt-für-schritt))
   und wählen Sie **OK**. Die anderen Bahnen überspringen diesen Schritt.

Das ist alles. Die Züge erscheinen innerhalb von ein oder zwei Minuten. Wo die
Strecken einer Bahn aus ihrem Fahrplan kommen, folgen die Züge ihren Strecken,
sobald der Fahrplan heruntergeladen ist, was beim ersten Mal einige Minuten
dauern kann. Um eine weitere Bahn zu beobachten, fügen Sie die Integration
erneut hinzu. Dieselbe Bahn zweimal wird abgelehnt.

### Was es zeigt ändern: die Optionen

Öffnen Sie **Einstellungen → Geräte & Dienste → Live Track Intercity Rail →
Konfigurieren** (das Zahnrad) bei der Bahn, die Sie ändern möchten. Es gibt
eine Option:

| Option | Was sie bewirkt | Standard |
|---|---|---|
| **Poll interval** (Abfrageintervall) | wie oft die Quelle der Bahn gelesen wird, 15 bis 600 Sekunden. Ein kürzeres Intervall als die eigene Aktualisierung der Quelle zeigt nichts mehr | je nach Bahn: 15 Sekunden für Renfe (Spain) und die drei niederländischen Bahnen; 60 Sekunden für Brightline, NSW TrainLink, Irish Rail und SJ Nord; 30 Sekunden für die anderen |

---

## Kostenlose Schlüssel, die mehr freischalten, Schritt für Schritt

Zwanzig Bahnen bitten jeden Nutzer um einen eigenen Schlüssel, von vier
Anbietern. Jeder dieser Schlüssel ist kostenlos, und jede Person, die Live
Track Intercity Rail installiert, bekommt ihren eigenen. Sie fügen den
Schlüssel ein, wenn der Einrichtungsdialog danach fragt
([Schritt 5 oben](#einrichtung-schritt-für-schritt)). Nur der Schlüssel wird
erfragt: kein Passwort und kein Geheimnis. Der Schlüssel wird in Home
Assistant bei der Integration gespeichert, nur an seinen eigenen Anbieter
gesendet und nie ins Protokoll geschrieben. Lehnt der Anbieter ihn zehn
Minuten lang ab, bittet Home Assistant Sie um einen neuen.

### Transport for NSW (NSW TrainLink, New South Wales, Australien)

1. Öffnen Sie <https://opendata.transport.nsw.gov.au/>, wählen Sie
   **Register**, legen Sie ein Konto an und melden Sie sich an.
2. Wählen Sie Ihr Profilsymbol, dann **API Tokens**.
3. Geben Sie einen Namen für den Schlüssel ein und wählen Sie **CREATE API
   TOKEN**. Kopieren Sie den Schlüssel sofort: Die Website zeigt ihn nur
   einmal.
4. Fügen Sie ihn unter **API key** ein, wenn Sie NSW TrainLink hinzufügen.
   Fügen Sie nur den Schlüssel ein: Live Track Intercity Rail setzt das Wort
   `apikey` selbst davor.

### Transport Victoria (V/Line, Victoria, Australien)

1. Öffnen Sie <https://opendata.transport.vic.gov.au/>, wählen Sie **Login**,
   dann **Sign up**.
2. Geben Sie Ihre Angaben ein und wählen Sie **Create Account**. Geben Sie den
   Code aus der E-Mail ein, die Sie erhalten, und wählen Sie **Confirm**.
3. Das Portal verlangt eine Authenticator-App auf Ihrem Telefon: Scannen Sie
   den QR-Code damit, geben Sie den Code der App ein und wählen Sie
   **Confirm**. Melden Sie sich dann mit Ihrer E-Mail, Ihrem Passwort und dem
   Code der App an.
4. Wählen Sie **My Account** → **Profile** → **API tokens**. Ihr Schlüssel ist
   schon da. Fügen Sie ihn unter **API key** ein, wenn Sie V/Line hinzufügen.

### NS (NS, Arriva und Keolis, Niederlande)

1. Öffnen Sie <https://apiportal.ns.nl/>, wählen Sie **Inloggen** (Anmelden),
   dann **Externe bezoeker** (externer Besucher).
2. Füllen Sie das Formular aus und senden Sie es ab. Eine E-Mail bestätigt die
   Registrierung. Es kann bis zu 5 Minuten dauern, bis die APIs im Portal
   erscheinen.
3. Öffnen Sie die Seite der **Virtual Train API** (die Zugpositionen von NS).
   Öffnen Sie unter **Related Products** ihr Produkt, geben Sie Ihrem
   Abonnement einen Namen und wählen Sie **Subscribe**.
4. Wenn NS das Abonnement genehmigt hat, steht Ihr Schlüssel auf Ihrer
   Profilseite. Fügen Sie ihn unter **API key** ein, wenn Sie NS, Arriva oder
   Keolis hinzufügen. Ein Schlüssel gilt für alle drei.

### Trafikverket (die 15 schwedischen Bahnen)

1. Öffnen Sie <https://data.trafikverket.se/oauth2/Account/register>.
2. Füllen Sie **Email**, **Displayname**, **Password** und **Confirm password**
   aus, setzen Sie das Häkchen bei **Accept license and Agreement** und wählen
   Sie **Register**.
3. Öffnen Sie <https://data.trafikverket.se/get-started> und wählen Sie
   **Create key** unter **Create a key**. Melden Sie sich mit dem Konto an, das
   Sie angelegt haben, und erstellen Sie den Schlüssel.
4. Fügen Sie ihn unter **API key** ein, wenn Sie eine schwedische Bahn
   hinzufügen. Ein Schlüssel gilt für alle fünfzehn.

---

## Die Karte auf ein Dashboard bringen

Die Karte ist [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
die Karte, auf der jedes Live-Track-Modul zeichnet. **Sie wird mit Live Track
Intercity Rail installiert**: nichts herunterzuladen, nichts zu kopieren,
keine Ressource hinzuzufügen.

1. Öffnen Sie ein Dashboard, wählen Sie den Stift (**Dashboard bearbeiten**),
   dann **Karte hinzufügen**.
2. Scrollen Sie ganz nach unten und wählen Sie **Manuell**.
3. Fügen Sie dies ein und wählen Sie **Speichern**:

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

Andere Live-Track-Module kommen genauso in `entity_filter`: eine weitere Regel
`- domain: geo_location` für jede Quelle.

**Auf der Karte:**

* Jeder Zug ist eine Markierung in den Farben seiner Bahn, beschriftet mit
  seiner Zugnummer oder Linie. Die Züge von Amtrak sind Sterne, die von VIA
  Rail tragen das Ahornblatt, die InterCity-Züge von Irish Rail sind
  Kleeblätter, und manche Züge sind Bilder (jede Bahn unten sagt, welche).
* Bei den meisten Bahnen tauschen die Farben mit der Richtung: eine Art, wenn
  der Zug die Hauptstadt verlässt, die andere, wenn er auf sie zufährt.
* Ein Pfeil zeigt die Fahrtrichtung. Ein stehender Zug behält seine letzte
  Richtung. Bilder bleiben aufrecht und haben keinen Pfeil.
* **Zeigen** Sie auf einen Zug, um seine Bahn, Nummer, Linie und Strecke zu
  sehen. **Klicken** Sie darauf für alle Details, auch seinen nächsten Halt
  und seine Verspätung.

Sind die Ressourcen Ihrer Dashboards in YAML festgelegt
(`lovelace: resource_mode: yaml`), kann nichts für Sie registriert werden:
Ein Eintrag unter **Reparaturen** nennt dann die genauen Zeilen für
`configuration.yaml`. Sie sehen so aus, mit der eigenen Adresse der
Integration an Stelle der Platzhalter:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_intercity_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Jedes Live-Track-Modul trägt eine Kopie der Karte und registriert sie, wenn
Home Assistant startet. Zusammen halten sie genau eine Zeile unter
**Einstellungen → Dashboards → Ressourcen**: die neueste Kartenversion, die
eines von ihnen trägt, nie eine ältere. Eine Karte, die Sie selbst über den
Marketplace installiert haben, bleibt unberührt. Entfernen Sie die letzte
Bahn dieses Moduls, geht die Zeile an ein anderes Live-Track-Modul über, oder
sie wird entfernt, wenn keines übrig ist. Werden die Dateien der Integration
entfernt, während ihre Bahnen noch eingerichtet sind, und ist kein anderes
Live-Track-Modul installiert, entfernen Sie die Zeile selbst unter
**Einstellungen → Dashboards → Ressourcen**.

**Um die Karte stattdessen von Hand zu installieren**, folgen Sie den
Schritten in der [README der Karte](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
Eine Zeile, die Sie selbst für eine Kopie unter `/local/` oder unter einer
anderen Adresse angelegt haben, wird nie geändert oder entfernt. Solange sie die
Karte lädt, überlässt jedes Live-Track-Modul ihr die Karte, auch wenn ein Modul
eine neuere Veröffentlichung mitbringt, und nichts unter **Reparaturen** weist
darauf hin. Um zur Kopie des Moduls zurückzukehren, entfernen Sie Ihre Zeile
unter **Einstellungen → Dashboards → Ressourcen** und starten Home Assistant
neu. Wenn Sie die Datei Ihrer Kopie löschen, entfernen Sie auch ihre Zeile:
Solange eine Zeile stehen bleibt, deren Datei fehlt, legt das Modul keine eigene
Zeile an.

Jede andere Kartenkarte, die `geo_location`-Entitäten zeigt, zeigt die Züge
auch, als einfache Markierungen.

---

## In Automationen verwenden

Alles ist eine gewöhnliche Home-Assistant-Entität, daher funktioniert der
Automationseditor damit, ohne Code.

**Eine Benachrichtigung aufs Telefon, wenn die Daten Ihrer Bahn ausbleiben**
(die Züge verlassen dann die Karte):

1. **Einstellungen → Automationen & Szenen → Automation erstellen → Neue
   Automation erstellen**.
2. **Sobald**: **Auslöser hinzufügen** → **Entität** → **Zustand geändert**.
   Wählen Sie die Entität **Trains in service** der Bahn, und unter **Zu
   (optional)** wählen Sie **Nicht verfügbar**.
3. **Dann**: **Aktion hinzufügen**, suchen Sie die Benachrichtigungsaktion
   Ihres Telefons (sie trägt den Namen Ihres Telefons) und geben Sie eine
   Nachricht ein, zum Beispiel:

   ```text
   Keine Fernzüge auf der Karte: die Daten der Bahn sind ausgeblieben
   ```

4. **Speichern**.

**Weitere Ideen:** ein Licht, das angeht, wenn ein Amtrak-Zug weniger als
2 km (1,2 Meilen) von Ihrem Zuhause in den Vereinigten Staaten entfernt ist,
aus der Entfernung der Markierungen; eine Dashboard-Anzeige der Züge, die VR
in Finnland über den Tag fährt; eine Nachricht, wenn der erste Zug des Tages
von Queensland Rail Travel abfährt (Australien), aus **Trains in service**,
das über 0 steigt.

---

## Alles auf der Karte im Detail

### Züge

Jeder Zug ist eine Markierung. Ihr Zustand ist ihre Entfernung von Ihrem
Zuhause, in Kilometern. Die Markierung erscheint, wenn die Bahn den Zug meldet
oder wenn ihr Fahrplan sagt, dass er fährt, und wird entfernt, wenn der Zug
die Daten der Bahn verlässt oder seine Fahrt zu Ende ist.

* **Zwischen zwei Meldungen** fährt ein Zug auf seiner eigenen Strecke zu
  seinem nächsten Halt: mit der Geschwindigkeit, die die Bahn meldet, oder,
  wo sie keine meldet, mit der Geschwindigkeit zwischen seinen letzten zwei
  Meldungen. Er fährt nie über seinen nächsten Halt hinaus und hält 30 Minuten
  nach der letzten Meldung an. Ein Zug auf einer bekannten Strecke wird auf
  der Strecke gezeichnet; die eigene Meldung der Bahn wird daneben behalten.
* **Fallen die Daten einer Bahn aus**, fahren ihre Züge bis zu 10 Minuten auf
  der letzten guten Meldung weiter. Danach sind sie nicht verfügbar und
  verlassen die Karte, bis die Daten zurück sind.
* **Verspätet und stark verspätet**: Wo die Bahn ihre eigene Regel für einen
  verspäteten Zug veröffentlicht, verwendet die Integration sie. Wo sie keine
  veröffentlicht, ist ein Zug nach der Länge seiner Fahrt verspätet, mit den
  Schwellen von Amtrak Status Maps (asm.transitdocs.com). Jede Bahn unten
  sagt, welche Regel gilt.

An jedem Zug: `marker_label`, `train`, `line_name`, `observed_at` (wann seine
Meldung zutraf), `course_deg` (während er fährt), `next_stop` und
`arrival_estimated_at` (wo bekannt), `delay_min`, `late_threshold_min` und
`very_late_threshold_min`, `speed_kmh` (wo die Bahn sie meldet),
`attribution`, und zwischen zwei Meldungen `previous_latitude`,
`previous_longitude`, `previous_observed_at` und `segment_duration_s`. Ein
auf seiner Strecke bewegter Zug trägt `position_source: estimated`, mit der
Meldung der Bahn in `fix_latitude` und `fix_longitude`.

### Journey Beyond (Australien)

⚠ **Journey Beyond veröffentlicht keine Positionen.** Jeder Zug wird aus
seinem veröffentlichten Fahrplan gezeichnet, übertragen in eine Datei, die mit
der Integration ausgeliefert wird (Abfahrten bis 29. Dezember 2027), daher
wird nichts heruntergeladen. Jeder Zug wird nach seinen Zeiten auf seine
Strecke gesetzt, als Schätzung gekennzeichnet, ohne Verspätung: Ein
verspäteter oder ausgefallener Zug wird trotzdem pünktlich gezeichnet. Jeder
Zug ist sein eigenes Bild (Kamel und Reiter, ein Vogel, ein Känguru, ein Emu),
in seinen Farben auf der Hinfahrt und vertauscht auf der Rückfahrt, ohne
Beschriftung: Zeigen Sie darauf, um den Zug und seine Fahrt zu sehen.

### NSW TrainLink (New South Wales, Australien)

Aus dem NSW-TrainLink-Feed von Transport for NSW, mit Ihrem eigenen Schlüssel,
eine neue Position etwa einmal in der Minute. Die Beschriftung ist die
Zugnummer. NSW-Orange mit weißem Ring beim Verlassen von Sydney, vertauscht
auf dem Weg dorthin. Der Feed hat keine Geschwindigkeit, daher fährt ein Zug
mit der Geschwindigkeit zwischen seinen letzten zwei Positionen auf seiner
Strecke weiter. Verspätet ab 11 Minuten (NSW TrainLink zählt einen Zug
innerhalb von 10 Minuten als pünktlich), stark verspätet ab 30.

### Queensland Rail Travel (Australien)

⚠ **Queensland Rail Travel veröffentlicht keine Positionen.** Ihr Home
Assistant liest die Zeiten, die die Seite „Service Updates" von Queensland
Rail Travel zeigt: die Liste der heutigen Züge höchstens alle 5 Minuten, und
die Zeiten jedes Zugs höchstens alle 5 Minuten, von 30 Minuten vor seiner
Abfahrt bis 15 Minuten nach seiner Ankunft. Jeder Zug wird nach diesen Zeiten
auf seine Strecke gesetzt und als Schätzung gekennzeichnet. Jede Linie ist ihr
eigenes Bild, in ihren Farben beim Verlassen von Brisbane und vertauscht auf
dem Weg dorthin, mit der Zugnummer in einem Schild daneben. Verspätet oder
stark verspätet wird nicht angezeigt.

### V/Line (Victoria, Australien)

Aus dem V/Line-Feed von Transport Victoria, mit Ihrem eigenen Schlüssel: die
Fernlinien nach Albury, Ararat, Bairnsdale, Echuca, Maryborough, Shepparton,
Swan Hill und Warrnambool. Die Beschriftung ist die Zugnummer. V/Line-Lila mit
gelbem Ring beim Verlassen von Melbourne, vertauscht auf dem Weg dorthin. Der
Feed hat keine Geschwindigkeit, daher fährt ein Zug mit der Geschwindigkeit
zwischen seinen letzten zwei Positionen; nach 10 Minuten ohne neue Position
wird er nach der Zeit zu seinem nächsten Halt bewegt. Verspätet ab 11 Minuten
auf den langen Linien und ab 6 auf den kurzen (die eigene Liste von V/Line),
stark verspätet ab 30.

### WA Trains (Western Australia, Australien)

⚠ **Es werden keine Live-Positionen veröffentlicht.** Jeder Zug wird aus dem
Fahrplan der Public Transport Authority of Western Australia gezeichnet: nach
seinen planmäßigen Zeiten auf seine Strecke gesetzt, als Schätzung
gekennzeichnet, ohne Verspätung. Der Fahrplan wird einmal am Tag geprüft. Die
Beschriftung sind die ersten drei Buchstaben der Linie: AUS (Australind,
lila), PRO (Prospector, orange), MER (MerredinLink, grün) und AVO (AvonLink,
grün), in beiden Richtungen gleich.

### VR (Finnland)

Aus Digitraffic von Fintraffic, eine neue Position etwa alle 30 Sekunden. Die
Beschriftung ist Zugart und Nummer, wie VR sie schreibt (`IC 23`). VR-Grün mit
dunklem Ring beim Verlassen von Helsinki, vertauscht auf dem Weg dorthin. Die
Daten haben keine Richtung, daher folgt der Pfeil der Strecke. Verspätet ab
6 Minuten (VR zählt einen Zug als verspätet, wenn er mehr als fünf Minuten zu
spät ist), stark verspätet ab 12.

* **Der Santa Claus Express**, vom ersten Adventssonntag bis zum 6. Januar:
  ein Schneemann auf der Fahrt nach Norden, ein Rentier auf der Rückfahrt,
  ohne Nummer. Ab 12 Minuten Verspätung dreht sich die Figur alle paar
  Sekunden um.
* **Das Sommerhaus**, von Mittsommerabend bis 31. Juli: Jeder Fernzug von VR
  wird als Sommerhaus gezeichnet, mit seiner Nummer daneben.

### Irish Rail (Irland)

Aus dem Live-Dienst von Irish Rail und dem Fahrplan der National Transport
Authority. ⚠ Irish Rail meldet einen Zug nur, wenn er Signalpunkte passiert,
die einige Minuten auseinanderliegen, daher wird jeder Zug aus seinem
Fahrplan und seiner letzten Verspätung gezeichnet, auf seiner Strecke bewegt.
Die Beschriftung ist die Zugnummer ohne ihren Buchstaben (A700 zeigt 700). Ein
InterCity-Zug ist ein grünes Kleeblatt mit orangefarbenem Rand und orange
Nummer beim Verlassen von Dublin, die Farben vertauscht auf dem Weg dorthin.
Der Enterprise ist eine silberne Scheibe mit rotem Außenring, einem
magentafarbenen Band und magentafarbener Nummer; auf dem Weg nach Dublin ist
die Scheibe magenta. Verspätet ab 10 Minuten (die Regel der National
Transport Authority), stark verspätet ab 20.

### NS, Arriva und Keolis (Niederlande)

Aus den Fahrzeugdaten von NS, mit Ihrem eigenen Schlüssel, eine neue Position
etwa alle 10 Sekunden. Dieser Feed meldet die eigene Geschwindigkeit und
Richtung eines Zugs, und beide werden weitergegeben. Nächster Halt und
Verspätung kommen aus dem Fahrplan von OVapi; die Gleise sind die eigene
Streckenkarte von NS, einmal am Tag heruntergeladen. Die Beschriftung ist die
Zugnummer. Die Züge von NS sind gelb mit einem NS-blauen Ring; die Züge von
Arriva und Keolis haben vorerst das eigene Aussehen der Kartenkarte.
Verspätet ab 3 Minuten (die eigene Definition von NS), stark verspätet ab 10.

### Vy, Go-Ahead Norge und SJ Nord (Norwegen)

Aus Entur, jede Bahn mit ihrem eigenen Eintrag. Die Beschriftung ist der
Linienname (F4, RE10, R50). Die eigene Farbe der Linie mit weißem Ring beim
Verlassen von Oslo S (bei einer Fahrt, die Oslo S nicht erreicht, ihrer
größeren Endstadt), vertauscht auf dem Weg dorthin. Entur veröffentlicht
weder Geschwindigkeit noch Richtung, daher fährt ein Zug mit der
Geschwindigkeit zwischen seinen letzten zwei Positionen, und der Pfeil folgt
seiner Strecke. In den langen Tunneln von Oslo wird ein Zug, dessen
Positionen ausbleiben, auf seiner Strecke bewegt, bis sie zurückkommen.
⚠ **SJ Nord veröffentlicht keine Positionen:** Jeder seiner Züge wird nach
seinen erwarteten Zeiten auf seine Strecke gesetzt. Verspätet ab 4 Minuten,
und ab 6 auf den F-Linien und den Linien nach Göteborg (Schweden), die Regel
von Bane NOR und Vy; stark verspätet beim Doppelten.

### Renfe (Spain) und Renfe Regionals (Katalonien, Spanien)

**Renfe (Spain)** liest den Fernverkehrs-Feed von Renfe, eine neue Position
etwa alle 15 Sekunden. Die Beschriftung ist die Zugnummer; die Zuggattung
(AVE, Avlo, Alvia und so weiter) steht im Hinweisfeld. AVE marineblau, Avlo
türkis, jede andere Gattung Renfe-Lila, jeweils gefüllt beim Verlassen von
Madrid (bei einer Fahrt, die Madrid nicht erreicht, ihrer größeren Endstadt)
und vertauscht auf dem Weg dorthin. Renfe veröffentlicht keine
Streckenverläufe, daher werden die Strecken aus OpenStreetMap gebaut und mit
der Integration ausgeliefert. Renfe veröffentlicht keine Regel für einen
verspäteten Zug, daher ist ein Zug nach der Länge seiner Fahrt verspätet: ab
10 Minuten bis 400 km (250 Meilen), 15 bis 560 km (350 Meilen), 20 bis
725 km (450 Meilen), 25 bis 885 km (550 Meilen), 30 darüber; stark verspätet
beim Doppelten.

**Renfe Regionals (Catalunya)** zeichnet die Regionallinien R11 bis R17 von
Rodalies de Catalunya. Die Beschriftung ist die Zugnummer, in der eigenen
Farbe der Linie, gefüllt beim Verlassen von Barcelona und vertauscht auf dem
Weg dorthin. Außerhalb von Barcelona ist eine Position der letzte Bahnhof,
den ein Zug passiert hat, daher wird der Zug zwischen den Bahnhöfen nach
Fahrplan und Verspätung bewegt. Verspätet ab 10 Minuten, stark verspätet ab
20, nach der Länge der längsten Linie. Sind beide Renfe-Bahnen eingerichtet,
wird jeder Zug einmal gezeichnet.

### Die schwedischen Bahnen (Schweden)

Aus Trafikverket, mit Ihrem eigenen Schlüssel (ein Schlüssel für alle
fünfzehn). Die Beschriftung ist die Zugnummer auf der Fahrkarte; Marke,
Nummer und Endbahnhöfe stehen im Hinweisfeld. Jede Marke hat ihre eigenen
Farben, vertauscht auf dem Weg nach Stockholm C (bei einer Fahrt, die
Stockholm C nicht erreicht, ihrer größeren Endstadt). Trafikverket gibt bei
etwa der Hälfte seiner Positionen eine Geschwindigkeit an; die anderen Züge
fahren mit der Geschwindigkeit zwischen ihren letzten zwei Positionen.
Schweden veröffentlicht keine Streckenverläufe, daher werden die Strecken aus
OpenStreetMap gebaut und mit der Integration ausgeliefert. Verspätet ab
6 Minuten (Trafikverket zählt einen Zug bis 5 Minuten 59 Sekunden als
pünktlich), stark verspätet ab 12.

### VIA Rail (Kanada)

Aus den eigenen Zugstatusdaten von VIA Rail. Jeder Zug ist eine Scheibe mit
dem Ahornblatt und einem Band in der Farbe seiner Streckengruppe (Atlantic,
Western, Ontario und Quebec, Prince Rupert, Churchill, Sudbury nach White
River, Montréal scenic), mit der Zugnummer in einem aufrechten Schild.
Ungerade Nummern haben eine gelbe Scheibe, gerade eine Scheibe in der Farbe
des Bands. Ein Zug ohne neue Position fährt auf seinen nächsten Halt zu, um
zur eigenen Schätzung von VIA anzukommen. VIA veröffentlicht keine Regel für
einen verspäteten Zug, daher ist ein Zug ab 10 Minuten auf dem Korridor
Québec City nach Windsor verspätet und ab 60 anderswo (die Werte von Amtrak
Status Maps für VIA), stark verspätet beim Doppelten.

### Amtrak (Vereinigte Staaten)

Amtrak veröffentlicht keine offenen Live-Daten. Amtraker gibt die eigene
Zugverfolgung von Amtrak weiter, mit einer neuen Position alle 3 bis
5 Minuten, und die Integration bewegt jeden Zug mit der von Amtrak gemeldeten
Geschwindigkeit auf seiner Strecke. Jeder Zug ist ein Stern mit seiner Nummer
darauf, in den Farben seiner Strecke (die Strecken im Nordosten, Cascades,
Pacific Surfliner, Acela und weitere), sonst der Flaggenstern. Der Maple Leaf
(New York nach Toronto) wechselt langsam zwischen dem Stern von Amtrak und dem
Abzeichen von VIA. Ein Zug, der an der Grenze in Lacolle, Rouses Point oder
Niagara Falls steht, zeigt „Customs" statt seiner Verspätung. Verspätet ab
16 Minuten (Amtrak zählt einen Zug innerhalb von 15 Minuten als pünktlich),
stark verspätet ab 30. Dieselbe Zugnummer kann an zwei oder drei Tagen
zugleich fahren, daher ist jede Fahrt eine eigene Markierung.

### Brightline (Vereinigte Staaten)

Aus dem eigenen Feed von Brightline, eine neue Position etwa alle
60 Sekunden. Die Beschriftung ist die Fahrtnummer, schwarz mit weißem Rand,
auf einer Scheibe in der Farbe des Ziels des Zugs, mit einem schwarzen Ring.
Eine Position, die älter als 5 Minuten ist, wird nicht verwendet. Der Feed hat
keine Geschwindigkeit, daher fährt ein Zug mit der Geschwindigkeit zwischen
seinen letzten zwei Positionen. Brightline veröffentlicht keine Regel für
einen verspäteten Zug, daher ist ein Zug ab 10 Minuten verspätet, stark
verspätet ab 20, nach der Länge seiner Fahrt.

---

## Alle Entitäten, die es anlegt

Für jede Bahn:

| Entität | Was sie ist |
|---|---|
| `sensor.<railroad>_trains_in_service` | **Trains in service** (Züge im Einsatz): wie viele Züge die Bahn jetzt auf der Karte fährt. Für Amtrak: `sensor.amtrak_trains_in_service` |
| `geo_location.<railroad>_train_…` | eine je Zug (`geo_location.amtrak_train_5_17`); sie kommt und geht mit dem Zug. Jede trägt `source: live_track_intercity_rail`, und ihr Zustand ist ihre Entfernung von Ihrem Zuhause in Kilometern |

Die Entitäts-ID einer Markierung kommt aus der Bahn und der Fahrt, nie aus
ihrer Beschriftung: `geo_location.amtrak_train_5_17` ist der Amtrak-Zug 5, der
am 17. des Monats losfuhr. So behält ein Zug dieselbe Entitäts-ID für seine
ganze Fahrt, und eine andere Fahrt derselben Nummer bekommt ihre eigene. Die
Markierung wird entfernt, wenn die Fahrt die Daten der Bahn verlässt oder
endet. Die Markierungen haben keine eindeutige ID, wie keine Markierung einer
Live-Track-Karte, daher können sie in der Oberfläche nicht umbenannt,
ausgeblendet oder einem Bereich zugewiesen werden. Der Sensor hat eine
eindeutige ID und kann umbenannt werden.

Attribute, die sich bei jeder Abfrage ändern, die Positionen und Zeiten der
Markierungen, werden im Verlauf von Home Assistant gespeichert, wie bei jeder
Entität. Der Sensor hat keine Attribute, kostet daher wenig, und er ist die
Aufzeichnung, wie viele Züge an einem Tag fuhren. Um die Markierungen aus dem
Verlauf herauszuhalten, fügen Sie dies in `configuration.yaml` ein und
starten Sie dann neu:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_train_*
```

Hat Ihre `configuration.yaml` schon einen Abschnitt `recorder:`, fügen Sie nur
das Muster `geo_location.*_train_*` hinzu, unter `exclude:` und
`entity_globs:`. Das Muster trifft nur die Zugmarkierungen dieses Moduls. Eine
Kartenkarte, die einen Verlauf zeichnen soll, hat dann keine Spur zu zeichnen.

---

## Was es sendet und herunterlädt

**Über Ihren Standort.** Nichts. Die Position Ihres Zuhauses wird nur in Ihrem
Home Assistant verwendet, um die Entfernung jedes Zugs anzugeben. Ihr
Schlüssel, wo eine Bahn einen braucht, wird nur an den Anbieter dieser Bahn
gesendet. Sonst wird nichts über Sie irgendwohin gesendet. Jeder Dienst sieht
Ihre Internetadresse, wie jede Website.

**Wie viel.** Jede Live-Quelle wird bei jeder Abfrage gelesen, standardmäßig
im eigenen Intervall der Bahn (**Poll interval**, 15 bis 600 Sekunden), oder
seltener, wo die Tabelle es sagt. Wo mehrere Live-Track-Module oder Bahnen
dieselbe Quelle lesen, liest ein gemeinsamer Client sie einmal für alle.
Gemessen am 19. November 2026, 02:44 bis 02:49 UTC:

| Bahn | Live-Daten, ein Abruf | Fahrplan und Strecken |
|---|---|---|
| Journey Beyond (Australien) | keine: nichts wird heruntergeladen | keine: Fahrplan und Strecken werden mit der Integration ausgeliefert |
| NSW TrainLink (Australien) | 124 KB aus zwei Feeds, höchstens einmal alle 55 Sekunden | 40 MB, wenn geändert, täglich geprüft |
| Queensland Rail Travel (Australien) | die Liste, 5,5 KB, alle 5 Minuten; die Zeiten jedes fahrenden Zugs, 6 bis 8 KB, alle 5 Minuten | keine: die Strecken werden mit der Integration ausgeliefert |
| V/Line (Australien) | 14 KB aus zwei Feeds | 58 MB (der V/Line-Teil der 311-MB-Datei von Transport Victoria, allein gelesen), wenn geändert, täglich geprüft |
| WA Trains (Australien) | keine: es gibt keinen Live-Feed | 28 MB, wenn geändert, täglich geprüft |
| VR (Finnland) | 1,4 KB komprimiert für die Positionen; die Züge des Tages, beim ersten Mal 0,5 MB komprimiert, danach nur die Änderungen, einmal in der Minute | 3,1 MB, jeden Tag |
| Irish Rail (Irland) | 0,2 KB, höchstens einmal alle 55 Sekunden | 6,6 MB, wenn geändert, täglich geprüft; die Bahnhofsliste, 46 KB, einmal in der Woche |
| NS, Arriva, Keolis (Niederlande) | 1,5 KB, höchstens einmal alle 9 Sekunden; Verspätungen von OVapi, 5,3 MB, alle 5 Minuten und nur wenn geändert | der Fahrplan von OVapi, 267 MB, höchstens einmal in der Woche und nur wenn geändert; die Streckenkarte von NS, 1,3 MB, jeden Tag |
| Vy, Go-Ahead Norge, SJ Nord (Norwegen) | Vy 510 KB aus zwei Feeds, Go-Ahead Norge 7 KB, SJ Nord 0,7 KB einmal in der Minute | Vy 67 MB, Go-Ahead Norge 20 MB, SJ Nord 26 MB, wenn geändert, täglich geprüft |
| Renfe (Spain) (Spanien) | 2,1 KB aus zwei Feeds | 0,7 MB, jeden Tag; die Strecken werden mit der Integration ausgeliefert |
| Renfe Regionals (Katalonien, Spanien) | 0,2 KB aus zwei Feeds, die alle Nahverkehrsnetze von Renfe tragen | 16 MB, jeden Tag |
| Die schwedischen Bahnen (Schweden) | 474 KB beim ersten Mal, danach 5 bis 9 KB an Änderungen | keine; die Bahnhofsliste, 0,15 MB, jeden Tag; die Strecken werden mit der Integration ausgeliefert |
| VIA Rail (Kanada) | 353 KB, komprimiert als 33 KB gesendet | 1,0 MB, einmal in der Woche |
| Amtrak (Vereinigte Staaten) | 1,2 MB, komprimiert als 113 KB gesendet | 18,6 MB, einmal in der Woche |
| Brightline (Vereinigte Staaten) | 1,3 KB aus zwei Feeds | 29 KB, einmal in der Woche |

⚠ Bei der Messung war in Australien Tag, in Nordamerika Abend und in Europa
Nacht. Ein Live-Feed ist nachts am kleinsten: Tagsüber sind die europäischen
Feeds größer, als die Tabelle zeigt.

**Nach einem Fehler.** Die Züge fahren bis zu 10 Minuten auf den letzten guten
Daten weiter; dann werden sie als nicht verfügbar markiert, bis die Quelle
antwortet. Ein Fahrplan, dessen Download scheitert, wird später erneut
versucht, und Ihre vorhandene Kopie bleibt in Gebrauch. Lehnt ein Anbieter
Ihren Schlüssel zehn Minuten lang ab, bittet Home Assistant Sie um einen
neuen.

**Auf der Festplatte.** Fahrpläne und Strecken werden im Ordner `.storage` von
Home Assistant unter Namen gespeichert, die mit `saw_` beginnen, gemeinsam mit
den anderen Live-Track-Modulen, die dieselbe Bahn lesen. Wenn Sie Live Track
Intercity Rail entfernen und kein anderes Live-Track-Modul sie nutzt, können
Sie sie von Hand löschen.

---

## Helfen Sie mit, es zu erweitern

Live Track Intercity Rail wächst noch. Wir fügen Bahnen und Länder hinzu,
sobald wir sie finden, und wir möchten wissen, was Sie sich als Nächstes
wünschen.

### Etwas vorschlagen

Fehlt Ihr Land oder Ihre Bahn? Ist etwas falsch oder schwer zu verstehen?
Sagen Sie es uns auf dem Weg, der für Sie einfacher ist:

* [**Füllen Sie ein kurzes Formular aus**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=de.yml)
  auf Deutsch. Sie brauchen ein kostenloses GitHub-Konto.
* **Schreiben Sie eine E-Mail** an
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Kein Konto nötig.

In beiden Fällen hilft es, wenn Sie uns sagen:

* was Sie gern sehen würden, und wo auf der Welt;
* einen Link, wo die Daten veröffentlicht werden, falls Sie einen kennen (eine
  Open-Data-Seite, ein öffentlicher Feed, die Website eines Dienstes): nicht
  nötig, aber hilfreich;
* die Sprache Ihres Home Assistant, wenn es um die Formulierung oder eine
  Übersetzung geht.

Schreiben Sie auf Englisch oder in Ihrer eigenen Sprache, was für Sie
einfacher ist.

### Selbst etwas hinzufügen, mit unserer Hilfe

Wenn Sie selbst etwas hinzufügen möchten, helfen wir Ihnen dabei, von der
ersten Frage bis zur fertigen Veröffentlichung. Sie müssen kein Entwickler
sein, um anzufangen:

* **Eine Übersetzung.** Die Texte im Einrichtungsdialog sind eine kurze Liste
  von Sätzen in einer Textdatei. Wir zeigen Ihnen, welche Datei und welche
  Zeilen.
* **Eine neue Bahn.** Sagen Sie uns, wo die Daten veröffentlicht werden. Wir
  können den Code gemeinsam schreiben oder Ihren durchsehen.
* **Testen, wo Sie wohnen.** Installieren Sie es, sehen Sie sich Ihren Teil
  der Karte an, und sagen Sie uns, was stimmt und was nicht.
* **Eine Korrektur dieser README.** Wenn ein Schritt nicht zu dem passte, was
  Sie gesehen haben, sagen Sie uns, was Sie gesehen haben.

[**Sagen Sie uns, was Sie vorhaben**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=de.yml)
oder schreiben Sie an
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
und wir antworten mit den nächsten Schritten.

---

## Sprachen

Diese README: [English](README.md), **Deutsch**, [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md),
[Suomi](README.fi.md), [Svenska](README.sv.md),
[Norsk bokmål](README.nb.md), [Gaeilge](README.ga.md). Jede übersetzte README
ist vollständig. Keine wurde bisher von einem Muttersprachler gelesen. Wenn
eine dieser Sprachen Ihre ist, sagen Sie uns bitte, ob sich ihre README gut
liest: siehe [Helfen Sie mit, es zu erweitern](#helfen-sie-mit-es-zu-erweitern).

Der Einrichtungsdialog und die Optionen sind vorerst nur auf Englisch, gleich
welche Sprache Ihr Home Assistant hat. Wenn Sie eine andere Sprache sprechen,
können Sie sie selbst übersetzen: Es ist eine kurze Liste von Sätzen in einer
Datei, und [wir helfen Ihnen dabei](#selbst-etwas-hinzufügen-mit-unserer-hilfe).

Einen Fehler in einer Übersetzung gefunden, oder eine andere Sprache nötig?
Sagen Sie es uns unter
<https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues>, oder
[übersetzen Sie mit unserer Hilfe](#selbst-etwas-hinzufügen-mit-unserer-hilfe).

---

## Danksagungen und Lizenzen

Jede Live-Quelle wird zur Laufzeit von Ihrem Home Assistant gelesen; nichts
aus einem Live-Feed liegt in diesem Repository. Jeder Zug nennt seine Quelle
in seinem Attribut `attribution`. Die Bedingungen jeder Quelle binden Sie, als
die Person, die ihre Daten empfängt.

* **Amtraker** (amtraker.com), der die Zugverfolgung von Amtrak weitergibt
  (Vereinigte Staaten): Daten unter der
  [Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/),
  Namensnennung erforderlich. Der eigene Fahrplan von **Amtrak** für die
  Strecken.
* **Brightline** (Vereinigte Staaten): seine Feeds GTFS und GTFS-Realtime;
  Brightline veröffentlicht keine Bedingungen.
* **VIA Rail** (Kanada): seine Zugstatusdaten, für die VIA keine Bedingungen
  veröffentlicht; sein Fahrplan unter der Open Government Licence - Canada 2.0
  ([developer resources](https://www.viarail.ca/en/developer-resources)).
* **Fintraffic / digitraffic.fi** (Finnland): Daten unter CC BY 4.0.
* **Transport for NSW** (Australien): Daten unter CC BY 4.0
  ([Datenlizenz](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australien): Daten unter CC BY 4.0
  ([Open Data](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Queensland Rail Travel** (Australien): die Zeiten, die seine Seite
  „Service Updates" zeigt, von Ihrem Home Assistant gelesen; siehe
  [die Urheberrechtsseite von Queensland Rail](https://www.queenslandrailtravel.com.au/copyright).
  Nichts von Queensland Rail Travel wird mit der Integration ausgeliefert.
* **Journey Beyond** (Australien): seine veröffentlichten Fahrpläne,
  übertragen in `data/journey_beyond_timetable.json`; Journey Beyond
  veröffentlicht keine Bedingungen dafür.
* **Public Transport Authority of Western Australia**: timetable data
  available free of charge from www.transperth.wa.gov.au
  ([spatial data access](https://www.transperth.wa.gov.au/About/Spatial-Data-Access);
  nicht CC BY).
* **Renfe** (Spanien): Daten unter CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)).
* **Entur** (Norwegen): contains data under the Norwegian licence for Open
  Government data ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)) distributed
  by Entur.
* **Trafikverket** (Schweden): Daten unter [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Irland): Live-Daten; Irish Rail veröffentlicht keine
  Bedingungen. Fahrplan der
  [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Irland), CC BY 4.0, ohne Gewähr bereitgestellt.
* **NS** (Niederlande): Fahrzeugdaten und Streckenkarte, mit Ihrem eigenen
  Schlüssel, unter den Bedingungen des [NS API portal](https://apiportal.ns.nl/).
  Fahrplan und Verspätungen von [OVapi](https://gtfs.ovapi.nl/), CC0.
* **In `data/` ausgelieferte Dateien**: die Strecken für Journey Beyond,
  Queensland Rail Travel, Renfe (Spain) und Schweden, aus
  [OpenStreetMap](https://www.openstreetmap.org/copyright) gebaut,
  © OpenStreetMap-Mitwirkende, unter der
  [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/);
  die Gemeinden der Endbahnhöfe der Renfe-Fahrten (OpenStreetMap, ODbL 1.0)
  und ihre Einwohnerzahlen (Wikidata-Eigenschaft P1082, CC0, sonst
  OpenStreetMap); die Einwohnerzahlen schwedischer Endstädte von Statistics
  Sweden (SCB) und Trafikverket, beide CC0 1.0; die Einwohnerzahlen
  norwegischer Endstädte von Statistics Norway, Tabelle 04859, CC BY 4.0.
* **Die Kartenkarte** ist [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, eine Kopie von [ha-map-card](https://github.com/nathan-gs/ha-map-card)
  von nathan-gs, MIT, ausgeliefert in `frontend/`. Ihre Kartenkacheln und deren
  Nachweise stehen in ihrer README.

Keine dieser Organisationen hat diese Integration erstellt oder unterstützt.

**Code**: MIT, in [LICENSE](LICENSE). Die Dateien in `data/` behalten die
Lizenzen ihrer Quellen, oben aufgeführt.

**Für Entwickler:** Jede Bahn ist ein Modul in
`custom_components/live_track_intercity_rail/operators/`, das einen
Quelladapter in `sources/` liest; die ausgelieferten Strecken werden mit den
Skripten in `tools/` neu gebaut (`journey_beyond.py`, `qrt_lines.py`,
`renfe_spain_lines.py`, `sweden_lines.py`). Die Tests laufen mit
`python -m unittest discover -s tests`.

---

## Stichwörter

Home Assistant Züge · Home Assistant Zugverfolgung · Live-Zugkarte ·
Fernverkehr · Fernzüge · Zugverkehr · GTFS-Realtime · Amtrak · Amtraker ·
Brightline · VIA Rail · trains en temps réel · VR · kaukojunat · NSW
TrainLink · XPT · V/Line · The Ghan · Indian Pacific · Spirit of Queensland ·
Transwa · Renfe · AVE · Avlo · Alvia · Rodalies · trenes en tiempo real · Vy ·
SJ Nord · tog i sanntid · SJ · Snälltåget · Öresundståg · tåg i realtid ·
Irish Rail · Enterprise · traenacha beo · NS Intercity · Arriva · treinen live ·
treni in tempo reale · togtrafik · 火车实时地图 · geo_location · Kartenkarte ·
Lovelace · HACS · Marketplace · Live Track · LiveTrack ·
StrausbergAutomationWorks

---

**Würdigung.** StrausbergAutomationWorks würdigt die indigenen Völker aller
Länder und Gewässer auf dieser Karte, überall auf der Welt, und erweist ihren
Ältesten, in Vergangenheit und Gegenwart, seinen Respekt.
