# Live Track Intercity Rail

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · **Suomi** · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · [Gaeilge](README.ga.md) · [Kaikki kielet](#kielet)

**Kaukojunat Home Assistantiin, yhdelle kartalle.** Live Track Intercity Rail
tuo Home Assistantin kartalle jokaisen junan niiltä kauko- ja pikajunien
rautateiltä, jotka valitset: missä juna on, sen numeron, onko se myöhässä
rautatien oman säännön mukaan, ja sen seuraavan pysähdyksen. Jokainen rautatie
lisätään erikseen, sen omista julkaistuista tiedoista.

> **Live Track Intercity Rail on yksi Live Trackin moduuli.** Live Track on
> joukko Home Assistant -integraatioita, jotka piirtävät kaiken liikkuvan ja
> sään, jonka läpi se liikkuu, yhdelle yhteiselle kartalle: lentokoneet,
> laivat, junat ja sää. Asenna se yksinään tai muiden moduulien rinnalle
> ([luettelo alempana](#osa-live-trackia-muut-moduulit)).

> **Kasvaa, ja ideat ovat tervetulleita.** Live Track Intercity Rail kattaa
> tänään 33 rautatietä 9 maassa 3 maanosassa, ja lisäämme rautateitä ja maita.
> Puuttuuko omasi? [Ehdota sitä](#auta-sitä-kasvamaan) tai lisää se itse:
> autamme sinua.

**Tila: 0.1.0, ensimmäinen julkaisu.** Lisätään Markkinapaikkaan linkillä
([alempana](#asenna-se-vaihe-vaiheelta)); se ei ole vielä Markkinapaikan
luettelossa.

StrausbergAutomationWorksin alkuperäistä työtä. Ei sidoksissa seuraaviin eikä
niiden hyväksymä: Amtrak, Amtraker, Brightline, VIA Rail, Fintraffic, VR,
Transport for NSW, NSW TrainLink, Transport Victoria, V/Line, Queensland Rail,
Journey Beyond, Länsi-Australian julkisen liikenteen viranomainen (Public
Transport Authority of Western Australia), Transwa, Renfe, Rodalies de
Catalunya, Entur, Vy, Go-Ahead Norge, SJ Nord, Trafikverket, SJ, VR
Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen,
Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget,
Värmlandstrafik, Tågab, Inlandsbanan, Irish Rail, Irlannin liikenneviranomainen
(National Transport Authority), NS, Arriva, Keolis, OVapi tai mikään muu
rautatie.

---

## Sisällys

1. [Kaikki mitä se tekee](#kaikki-mitä-se-tekee)
2. [Missä se toimii](#missä-se-toimii)
3. [Osa Live Trackia: muut moduulit](#osa-live-trackia-muut-moduulit)
4. [Ennen kuin aloitat](#ennen-kuin-aloitat)
5. [Asenna se, vaihe vaiheelta](#asenna-se-vaihe-vaiheelta)
6. [Ota se käyttöön, vaihe vaiheelta](#ota-se-käyttöön-vaihe-vaiheelta)
7. [Ilmaiset avaimet, jotka tuovat lisää, vaihe vaiheelta](#ilmaiset-avaimet-jotka-tuovat-lisää-vaihe-vaiheelta)
8. [Lisää kartta kojelaudalle](#lisää-kartta-kojelaudalle)
9. [Käytä sitä automaatioissa](#käytä-sitä-automaatioissa)
10. [Kaikki kartalla, tarkemmin](#kaikki-kartalla-tarkemmin)
11. [Kaikki sen luomat entiteetit](#kaikki-sen-luomat-entiteetit)
12. [Mitä se lähettää ja lataa](#mitä-se-lähettää-ja-lataa)
13. [Auta sitä kasvamaan](#auta-sitä-kasvamaan)
14. [Kielet](#kielet)
15. [Tekijät ja lisenssit](#tekijät-ja-lisenssit)
16. [Hakusanat](#hakusanat)

---

## Kaikki mitä se tekee

### Kartalla, ilman asetuksia

Lisäät **rautatien**: valitset maan ja sitten yhden sen kaukoliikenteen
rautateistä. Kaikki alla oleva näkyy sitten sen rautatien osalta. Lisää
integraatio uudelleen jokaista muuta haluamaasi rautatietä varten.

| Mitä | Missä | Mistä |
|---|---|---|
| **Liikenteessä olevat junat**: yksi merkki junaa kohden, nimettynä junan numerolla tai linjalla, rautatien omissa väreissä, käännettynä kulkusuuntaan | jokainen rautatie | kunkin rautatien omat julkaistut tiedot |
| **Myöhästyminen**: juna näkyy myöhässä tai paljon myöhässä rautatien oman säännön mukaan; jos rautatie ei julkaise sääntöä, sen mukaan, kuinka pitkän matkan juna kulkee | jokainen rautatie, joka ilmoittaa myöhästymiset | kunkin rautatien oma syöte |
| **Seuraava pysähdys ja sen aika**: asema, jolla juna pysähtyy seuraavaksi, ja milloin sen odotetaan olevan siellä | jokainen rautatie, jonka syöte tai aikataulu kertoo sen | kunkin rautatien oma syöte ja aikataulu |
| **Junat seuraavat raiteita**: kahden ilmoituksen välillä juna liikkuu omaa linjaansa pitkin viimeisellä nopeudellaan, ei suoraan poikki | jokainen rautatie, jonka linja tunnetaan | kunkin rautatien aikataulu tai integraation mukana toimitetut linjat |
| **Junat aikataulusta**: jos rautatie ei julkaise sijainteja, jokainen juna sijoitetaan linjalleen aikojensa mukaan ja merkitään arvioksi | Journey Beyond, Queensland Rail Travel ja WA Trains (Australia), SJ Nord (Norja); Irish Rail viimeisimmällä myöhästymisellään | kunkin rautatien aikataulu tai ajat |
| **Kuvat joillekin junille**: Joulupukin pikajuna ja kesämökki (Suomi), Journey Beyondin junien eläimet, oma kuva jokaiselle Queensland Rail Travelin linjalle | Suomi, Australia | piirretty tätä integraatiota varten |
| **Pysähtynyt rajalle**: Yhdysvaltain ja Kanadan rajanylityspaikalla seisova juna näyttää myöhästymisen sijaan "Customs" (tulli) | Amtrakin junat Kanadaan ja Kanadasta | Amtrakin sijainnit |
| **Yksi lukumäärä rautatietä kohden**: liikenteessä olevat junat | jokainen rautatie | samat tiedot |

### Oma ilmainen avain tai tili tuo lisää

| Ilmainen avain tai tili | Mitä se lisää |
|---|---|
| **Transport for NSW Open Data** -avain | NSW TrainLinkin aluejunat (Uusi Etelä-Wales, Australia) |
| **Transport Victoria Open Data** -avain | V/Linen kaukojunat (Victoria, Australia) |
| **NS API portal** -avain | NS Intercity sekä Arrivan ja Keoliksen aluejunat (Alankomaat); yksi avain kaikille kolmelle |
| **Trafikverket**-avain | 15 ruotsalaista rautatietä; yksi avain kaikille viidelletoista |

Kunkin saaminen vie muutaman minuutin: [vaihe vaiheelta alempana](#ilmaiset-avaimet-jotka-tuovat-lisää-vaihe-vaiheelta).
Muut 13 rautatietä eivät tarvitse avainta.

---

## Missä se toimii

| Alue | Mitä saat | Mistä | Tarvitsee |
|---|---|---|---|
| **Australia**: koko maa | Journey Beyond: The Ghan, The Ghan Expedition, Indian Pacific, Great Southern, The Overland, vain aikataulusta ([miksi](#journey-beyond-australia)) | Journey Beyond | ei mitään |
| **Australia**: Uusi Etelä-Wales | NSW TrainLinkin aluejunat (XPT ja Xplorer), myös Queenslandiin, Victoriaan ja Australian pääkaupunkiterritorioon | Transport for NSW | ilmainen avain |
| **Australia**: Queensland | Queensland Rail Travel: Spirit of Queensland, Spirit of the Outback, Tilt Train, Westlander, Inlander, Kuranda Scenic Railway, Gulflander, julkaistuista ajoistaan ([miksi](#queensland-rail-travel-australia)) | Queensland Rail Travel | ei mitään |
| **Australia**: Victoria | V/Linen kaukojunat (sen lähiliikenteen linjat ovat Live Track Commuter Railissa), myös Uuteen Etelä-Walesiin | Transport Victoria | ilmainen avain |
| **Australia**: Länsi-Australia | WA Trains: Australind, Prospector, MerredinLink ja AvonLink, vain aikataulusta ([miksi](#wa-trains-länsi-australia-australia)) | Länsi-Australian julkisen liikenteen viranomainen | ei mitään |
| **Eurooppa**: Suomi | VR:n kaukojunat | Fintraffic Digitraffic | ei mitään |
| **Eurooppa**: Irlanti | Irish Railin InterCity-junat ja Enterprise Dublinista Belfastiin (Yhdistynyt kuningaskunta) | Irish Rail, National Transport Authority | ei mitään |
| **Eurooppa**: Alankomaat | NS Intercity sekä Arrivan (Arriva, RRReis, Blauwnet) ja Keoliksen (Blauwnet, RRReis) aluejunat; NS:n Sprinterit ovat Live Track Commuter Railissa | NS, OVapi | ilmainen avain |
| **Eurooppa**: Norja | Vyn F-, RE-, RX- ja R-linjat (F1 myös Ruotsiin), Go-Ahead Norgen F5 ja R50, SJ Nordin F6, F7 ja R60–R75 | Entur | ei mitään |
| **Eurooppa**: Espanja | Renfen AVE-, Avlo-, Alvia-, Avant-, Euromed-, Intercity-, MD- ja Regional-junat, myös Ranskaan ja Portugaliin; Rodalies de Catalunyan aluelinjat R11–R17 | Renfe | ei mitään |
| **Eurooppa**: Ruotsi | SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget, Värmlandstrafik, Tågab ja Inlandsbanan, kukin oma rautatiensä; Öresundståg myös Tanskaan | Trafikverket | ilmainen avain |
| **Pohjois-Amerikka**: Kanada | VIA Rail, jokainen reitti | VIA Rail | ei mitään |
| **Pohjois-Amerikka**: Yhdysvallat | Amtrak, jokainen reitti, myös Kanadaan | Amtraker | ei mitään |
| **Pohjois-Amerikka**: Yhdysvallat | Brightline (Florida) | Brightline | ei mitään |

Eikö omasi ole luettelossa? [Kerro meille](#auta-sitä-kasvamaan). Jos joku
julkaisee tiedot avoimesti, katsomme sen lisäämistä.

⚠ **Juna on vain niin hyvä kuin rautatien tiedot.** Jotkin rautatiet ilmoittavat
junan muutaman sekunnin välein, jotkin muutaman minuutin välein, jotkin vain
sen ohittaessa opastimia, ja jotkin eivät julkaise sijainteja lainkaan. Kunkin
rautatien rajoitukset ovat kohdassa
[Kaikki kartalla, tarkemmin](#kaikki-kartalla-tarkemmin).

⚠ **Tämä ei ole rautatien virallista tietoa.** Tarkista ennen matkaa rautatien
oma sovellus tai verkkosivusto.

---

## Osa Live Trackia: muut moduulit

Live Track on joukko Home Assistant -integraatioita, yksi kutakin liikkuvaa
asiaa kohden, ja kaikki piirretään samalle karttakortille. Jokainen toimii
yksinään; yhdessä ne muodostavat yhden elävän kuvan. Niillä on yhteinen
karttakortti ja Python-kirjasto
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
joten uuden moduulin asentaminen ei lisää pyyntöjä lähteeseen, jota toinen jo
lukee.

| Moduuli | Mitä se tuo kartalle | Tila |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | lentokoneet yläpuolellasi ADS-B:n kautta, reiteillä ja tyyppikuvakkeilla | julkaistu |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | laivat ja veneet AIS:n kautta, lähelläsi tai missä tahansa | julkaistu |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | lähijunat Pohjois-Amerikassa, Euroopassa ja Australiassa | julkaistu |
| **Live Track Intercity Rail** | kaukojunat Pohjois-Amerikassa, Euroopassa ja Australiassa (tämä moduuli) | julkaistu |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | maahanmuutto- ja liittovaltion lainvalvontaviranomaisten lentokoneet ja alukset julkisista luetteloista | julkaistu |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | sää, myrskyt ja luonnonvaarat | julkaistu |
| Live Track Stations | lähtötaulut ja "nyt on lähdettävä" -ilmoitukset jokaiselle asemalle | suunnitteilla |
| Live Track Satellites | yläpuolelta kulkevat satelliitit | suunnitteilla |
| Live Track Freight Trains | tavara- ja työjunat siellä, missä rautatiet julkaisevat ne | suunnitteilla |
| Live Track Transit | kaupunkibussit, raitiovaunut, lautat ja metro | suunnitteilla |
| Live Track Intercity Buses | pika- ja aluebussit | suunnitteilla |
| Live Track Commuter Buses | työmatkabussit | suunnitteilla |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | yhteinen karttakortti, jolle jokainen moduuli piirtää | julkaistu, asennetaan jokaisen moduulin mukana |

Kaikki on ilmaista ja avointa lähdekoodia. Mitään ei pidätetä tukijoille.

---

## Ennen kuin aloitat

* **Home Assistant** 2026.11 tai uudempi.
* **Markkinapaikka** (HACS) Home Assistantissasi, jotta asennus ja päivitys
  käyvät helposti. Ilman sitä voit kopioida tiedostot käsin.
* **Internetyhteys** Home Assistantille: jokainen juna tulee rautatiensä omista
  julkaistuista tiedoista.
* **Valinnainen: auto-entities** Markkinapaikasta merkkien tuomiseksi
  kartalle (katso [Lisää kartta kojelaudalle](#lisää-kartta-kojelaudalle)).
* Ei mitään maksettavaa. 13 rautatietä 33:sta ei tarvitse tiliä; muut 20
  tarvitsevat oman ilmaisen avaimen, ja neljä avainta kattaa ne kaikki
  ([yllä](#oma-ilmainen-avain-tai-tili-tuo-lisää)).
* Home Assistant asentaa tarvitsemansa Python-paketit (`saw-livetrack`,
  `gtfs-realtime-bindings` ja `tzdata`) itse, kun integraatio latautuu
  ensimmäisen kerran.

---

## Asenna se, vaihe vaiheelta

### Markkinapaikasta (suositus)

Live Track Intercity Rail ei ole vielä Markkinapaikan luettelossa. Lisää se
sen linkillä:

1. Avaa Home Assistantissa **Asetukset → Markkinapaikka** (HACS).
2. Valitse **Lisää linkistä** (tai kolmen pisteen valikko → **Mukautetut
   tietovarastot**).
3. Kirjoita `StrausbergAutomationWorks/LiveTrackIntercityRail`. Jos tyyppiä
   kysytään, valitse **Integraatio**.
4. Etsi luettelosta **Live Track Intercity Rail** ja valitse **Lataa** tai
   **Asenna**.
5. **Käynnistä Home Assistant uudelleen**: **Asetukset → Järjestelmä →
   Korjaukset** tarjoaa uudelleenkäynnistystä, tai käytä **Asetukset →
   Järjestelmä → Käynnistä uudelleen**.

Markkinapaikka tarjoaa sen jälkeen jokaisen uuden julkaisun päivityksenä.

### Käsin

1. Lataa [uusimman julkaisun](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/releases/latest)
   lähdekoodi.
2. Kopioi sen kansio `custom_components/live_track_intercity_rail` Home
   Assistantin asetuskansion kansioon `custom_components` (luo
   `custom_components`, jos sitä ei ole).
3. Käynnistä Home Assistant uudelleen.

Päivittääksesi käsin korvaa kansio uuden julkaisun kansiolla ja käynnistä
uudelleen.

---

## Ota se käyttöön, vaihe vaiheelta

1. Avaa **Asetukset → Laitteet & palvelut**.
2. Valitse **Lisää integraatio** (oikealla alhaalla) ja hae **Live Track
   Intercity Rail**.
3. **Region** (alue): valitse rautatien maa. Vain maat, joissa on vähintään
   yksi rautatie, näkyvät. Valitse **Lähetä**.
4. **Railroad** (rautatie): valitse rautatie. Valitse **Lähetä**.
5. **API key** (API-avain): vain NSW TrainLinkille, V/Linelle, kolmelle
   hollantilaiselle rautatielle ja viidelletoista ruotsalaiselle rautatielle.
   Liitä avaimesi ([näin saat sen](#ilmaiset-avaimet-jotka-tuovat-lisää-vaihe-vaiheelta))
   ja valitse **Lähetä**. Muut rautatiet ohittavat tämän vaiheen.

Siinä kaikki. Junat ilmestyvät minuutin tai parin kuluessa. Jos rautatien
linjat tulevat sen aikataulusta, junat alkavat seurata linjojaan, kun
aikataulu on ladattu, mikä voi ensimmäisellä kerralla viedä muutaman
minuutin. Seurataksesi toista rautatietä lisää integraatio uudelleen. Samaa
rautatietä ei voi lisätä kahdesti.

### Muuta sitä, mitä se näyttää: asetukset

Avaa **Asetukset → Laitteet & palvelut → Live Track Intercity Rail →
Määrittele** (hammasratas) sen rautatien kohdalla, jota haluat muuttaa.
Asetuksia on yksi:

| Asetus | Mitä se tekee | Oletus |
|---|---|---|
| **Poll interval** (kyselyväli) | kuinka usein rautatien lähde luetaan, 15–600 sekuntia. Lähteen omaa päivitysväliä lyhyempi väli ei näytä mitään lisää | rautatiekohtainen: 15 sekuntia Renfe (Spain) -rautatielle ja kolmelle hollantilaiselle rautatielle; 60 sekuntia Brightlinelle, NSW TrainLinkille, Irish Railille ja SJ Nordille; 30 sekuntia muille |

---

## Ilmaiset avaimet, jotka tuovat lisää, vaihe vaiheelta

Kaksikymmentä rautatietä pyytää jokaiselta käyttäjältä oman avaimen neljältä
palveluntarjoajalta. Jokainen näistä avaimista on ilmainen, ja jokainen Live
Track Intercity Railin asentaja hankkii omansa. Liität avaimen, kun
asetusvalintaikkuna pyytää sitä ([vaihe 5 yllä](#ota-se-käyttöön-vaihe-vaiheelta)).
Vain avainta kysytään: ei salasanaa eikä salaisuutta. Avain tallennetaan
Home Assistantiin integraation mukana, lähetetään vain sen omalle
palveluntarjoajalle, eikä sitä koskaan kirjoiteta lokiin. Jos palveluntarjoaja
hylkää sen kymmenen minuutin ajan, Home Assistant pyytää sinulta uutta.

### Transport for NSW (NSW TrainLink, Uusi Etelä-Wales, Australia)

1. Avaa <https://opendata.transport.nsw.gov.au/>, valitse **Register**, luo
   tili ja kirjaudu sisään.
2. Valitse käyttäjäprofiilisi kuvake ja sitten **API Tokens**.
3. Kirjoita avaimelle nimi ja valitse **CREATE API TOKEN**. Kopioi avain heti:
   sivusto näyttää sen vain kerran.
4. Liitä se kenttään **API key**, kun lisäät NSW TrainLinkin. Liitä pelkkä
   avain: Live Track Intercity Rail lisää sanan `apikey` itse.

### Transport Victoria (V/Line, Victoria, Australia)

1. Avaa <https://opendata.transport.vic.gov.au/>, valitse **Login** ja sitten
   **Sign up**.
2. Anna tietosi ja valitse **Create Account**. Kirjoita saamasi sähköpostin
   koodi ja valitse **Confirm**.
3. Portaali pyytää puhelimeesi todennussovellusta: skannaa QR-koodi sillä,
   kirjoita sovelluksen koodi ja valitse **Confirm**. Kirjaudu sitten sisään
   sähköpostiosoitteellasi, salasanallasi ja sovelluksen koodilla.
4. Valitse **My Account** → **Profile** → **API tokens**. Avaimesi on jo
   siellä. Liitä se kenttään **API key**, kun lisäät V/Linen.

### NS (NS, Arriva ja Keolis, Alankomaat)

1. Avaa <https://apiportal.ns.nl/>, valitse **Inloggen** (kirjaudu sisään) ja
   sitten **Externe bezoeker** (ulkopuolinen vierailija).
2. Täytä lomake ja lähetä se. Sähköposti vahvistaa rekisteröinnin.
   Rajapintojen ilmestyminen portaaliin voi kestää enintään 5 minuuttia.
3. Avaa **Virtual Train API** -sivu (NS:n junien sijainnit). Avaa kohdasta
   **Related Products** sen tuote, anna tilauksellesi nimi ja valitse
   **Subscribe**.
4. Kun NS on hyväksynyt tilauksen, avaimesi on profiilisivullasi. Liitä se
   kenttään **API key**, kun lisäät NS:n, Arrivan tai Keoliksen. Yksi avain
   kelpaa kaikille kolmelle.

### Trafikverket (15 ruotsalaista rautatietä)

1. Avaa <https://data.trafikverket.se/oauth2/Account/register>.
2. Täytä **Email**, **Displayname**, **Password** ja **Confirm password**,
   rastita **Accept license and Agreement** ja valitse **Register**.
3. Avaa <https://data.trafikverket.se/get-started> ja valitse kohdan
   **Create a key** alta **Create key**. Kirjaudu sisään luomallasi tilillä ja
   luo avain.
4. Liitä se kenttään **API key**, kun lisäät ruotsalaisen rautatien. Yksi
   avain kelpaa kaikille viidelletoista.

---

## Lisää kartta kojelaudalle

Kartta on [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
kortti, jolle jokainen Live Track -moduuli piirtää. **Se asennetaan Live Track
Intercity Railin mukana**: ei mitään ladattavaa, ei mitään kopioitavaa, ei
resurssia lisättävänä.

1. Avaa kojelauta, valitse kynä (**Muokkaa käyttöliittymää**) ja sitten
   **Lisää kortti**.
2. Vieritä alas ja valitse **Manuaalinen**.
3. Liitä tämä ja valitse **Tallenna**:

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

Tämä tapa tarvitsee Markkinapaikasta
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities)-kortin.
Jos muita Live Track -moduuleja on asennettu, lisää yksi
`- domain: geo_location` -suodatin lisää kutakin niiden lähdettä kohden
(`live_track_commuter_rail`, `live_track_aircraft` ja niin edelleen).

**Ilman auto-entities-korttia:** LiveTrackMapCard voi valita itse, mitä se
näyttää, `entity_filter`-asetuksella. Liitä tämä sen sijaan; muuta ei tarvitse
asentaa:

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

Muut Live Track -moduulit lisätään `entity_filter`-asetukseen samalla tavalla:
yksi `- domain: geo_location` -sääntö lisää kutakin lähdettä kohden.

**Kartalla:**

* Jokainen juna on merkki rautatiensä väreissä, nimettynä junan numerolla tai
  linjalla. Amtrakin junat ovat tähtiä, VIA Railin junissa on vaahteranlehti,
  Irish Railin InterCity-junat ovat apilanlehtiä, ja jotkin junat ovat kuvia
  (kukin rautatie alla kertoo, mitkä).
* Useimmilla rautateillä värit vaihtuvat suunnan mukaan: yhdet päätaajamasta
  lähdettäessä, toiset sinne mentäessä.
* Nuoli näyttää junan kulkusuunnan. Paikallaan seisova juna säilyttää
  viimeisen suuntansa. Kuvat pysyvät pystyssä, eikä niissä ole nuolta.
* **Osoita** junaa nähdäksesi sen rautatien, numeron, linjan ja sen, missä se
  kulkee. **Napsauta** sitä nähdäksesi kaikki sen tiedot, myös seuraavan
  pysähdyksen ja myöhästymisen.

Jos kojelautojesi resurssit on määritelty YAMLissa
(`lovelace: resource_mode: yaml`), mitään ei voida rekisteröidä puolestasi:
**Korjaukset**-ilmoitus antaa silloin tarkat rivit, jotka lisätään tiedostoon
`configuration.yaml`. Ne näyttävät tältä, paikkamerkkien tilalla integraation
oma osoite:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_intercity_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Jokainen Live Track -moduuli sisältää kopion kortista ja rekisteröi sen, kun
Home Assistant käynnistyy. Yhdessä ne pitävät kohdassa **Asetukset →
Kojelaudat → Resurssit** täsmälleen yhden rivin: uusimman korttiversion, joka
millään niistä on, ei koskaan vanhempaa. Kortti, jonka asensit itse
Markkinapaikasta, jätetään rauhaan. Kun poistat tämän moduulin viimeisen
rautatien, rivi siirtyy toiselle Live Track -moduulille, tai se poistetaan,
jos muita ei ole. Jos integraation tiedostot poistetaan, kun sen rautatiet
ovat yhä käytössä, eikä muuta Live Track -moduulia ole asennettu, poista rivi
itse kohdassa **Asetukset → Kojelaudat → Resurssit**.

**Asentaaksesi kortin sen sijaan käsin** noudata
[kortin README-tiedoston](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track)
ohjeita. Itse tekemäsi rivi kopiolle kansiossa `/local/` ohjataan tämän
moduulin kopioon vain, jos tämän moduulin kopio on uudempi julkaisu.

Mikä tahansa muu karttakortti, joka näyttää `geo_location`-entiteettejä,
näyttää myös junat tavallisina merkkeinä.

---

## Käytä sitä automaatioissa

Kaikki on tavallisia Home Assistant -entiteettejä, joten automaatioeditori
toimii niiden kanssa ilman koodia.

**Ilmoitus puhelimeen, kun rautatiesi tiedot lakkaavat tulemasta** (junat
poistuvat silloin kartalta):

1. **Asetukset → Automaatiot & tilanteet → Lisää automaatio → Luo uusi
   automaatio**.
2. **Kun**: **Laukaisuehto** → **Entiteetti** → **Tila muuttui**. Valitse
   rautatien **Trains in service** (liikenteessä olevat junat) -entiteetti, ja
   valitse kohdassa **Kohdetila (valinnainen)** **Ei saatavissa**.
3. **Tee sitten**: **Lisää toiminto**, hae puhelimesi ilmoitustoiminto (siinä
   on puhelimesi nimi) ja kirjoita viesti, esimerkiksi:

   ```text
   Kartalla ei ole kaukojunia: rautatien tiedot ovat lakanneet tulemasta
   ```

4. **Tallenna**.

**Muita ideoita:** valo, joka syttyy, kun Amtrakin juna on 2 km:n (1,2 mailin)
päässä kodistasi Yhdysvalloissa, merkkien etäisyyden perusteella; kojelaudan
lukema VR:n Suomessa päivän mittaan ajamista junista; viesti, kun Queensland
Rail Travelin päivän ensimmäinen juna lähtee (Australia), kun **Trains in
service** nousee yli 0:n.

---

## Kaikki kartalla, tarkemmin

### Junat

Jokainen juna on yksi merkki. Sen tila on sen etäisyys kodistasi
kilometreinä. Merkki ilmestyy, kun rautatie ilmoittaa junan tai kun sen
aikataulu sanoo sen olevan liikenteessä, ja se poistetaan, kun juna poistuu
rautatien tiedoista tai sen vuoro päättyy.

* **Kahden ilmoituksen välillä** juna liikkuu omaa linjaansa pitkin kohti
  seuraavaa pysähdystään: rautatien ilmoittamalla nopeudella, tai jos
  rautatie ei ilmoita nopeutta, kahden viimeisen ilmoituksen välisellä
  nopeudella. Se ei koskaan ohita seuraavaa pysähdystään, ja se lakkaa
  liikkumasta 30 minuuttia viimeisen ilmoituksen jälkeen. Tunnetulla linjalla
  oleva juna piirretään linjalle; rautatien oma ilmoitus säilytetään sen
  rinnalla.
* **Jos rautatien tiedot katkeavat**, sen junat liikkuvat viimeisen hyvän
  ilmoituksen varassa enintään 10 minuuttia. Sen jälkeen ne ovat ei
  saatavissa ja poistuvat kartalta, kunnes tiedot palaavat.
* **Myöhässä ja paljon myöhässä**: jos rautatie julkaisee oman sääntönsä
  myöhässä olevalle junalle, integraatio käyttää sitä. Jos se ei julkaise
  sääntöä, juna on myöhässä sen mukaan, kuinka pitkän matkan se kulkee,
  Amtrak Status Mapsin (asm.transitdocs.com) raja-arvoilla. Kukin rautatie
  alla kertoo, kumpi.

Jokaisessa junassa: `marker_label`, `train`, `line_name`, `observed_at`
(milloin sen ilmoitus piti paikkansa), `course_deg` (sen liikkuessa),
`next_stop` ja `arrival_estimated_at` (jos tiedossa), `delay_min`,
`late_threshold_min` ja `very_late_threshold_min`, `speed_kmh` (jos rautatie
ilmoittaa sen), `attribution` sekä kahden ilmoituksen välillä
`previous_latitude`, `previous_longitude`, `previous_observed_at` ja
`segment_duration_s`. Linjaansa pitkin siirretyllä junalla on
`position_source: estimated`, ja rautatien ilmoitus on kentissä
`fix_latitude` ja `fix_longitude`.

### Journey Beyond (Australia)

⚠ **Journey Beyond ei julkaise sijainteja.** Jokainen juna piirretään sen
julkaistusta aikataulusta, joka on kirjoitettu integraation mukana
toimitettavaan tiedostoon (lähdöt 29. joulukuuta 2027 asti), joten mitään ei
ladata. Jokainen juna sijoitetaan linjalleen aikojensa mukaan, merkitään
arvioksi, eikä sillä ole myöhästymistä: myöhässä oleva tai peruttu juna
piirretään silti aikataulussa. Jokainen palvelu on oma kuvansa (kameli ja
ratsastaja, lintu, kenguru, emu), menosuunnassa omissa väreissään ja
paluusuunnassa värit vaihdettuina, ilman nimeä: osoita sitä nähdäksesi junan
ja sen vuoron.

### NSW TrainLink (Uusi Etelä-Wales, Australia)

Transport for NSW:n NSW TrainLink -syötteestä omalla avaimellasi, uusi
sijainti noin kerran minuutissa. Nimenä on junan numero. NSW:n oranssi
valkoisella renkaalla Sydneystä lähdettäessä, värit vaihdettuina sinne
mentäessä. Syötteessä ei ole nopeutta, joten juna liikkuu linjaansa pitkin
kahden viimeisen sijaintinsa välisellä nopeudella. Myöhässä 11 minuutista
alkaen (NSW TrainLink pitää junaa ajallaan 10 minuutin sisällä), paljon
myöhässä 30 minuutista.

### Queensland Rail Travel (Australia)

⚠ **Queensland Rail Travel ei julkaise sijainteja.** Home Assistantisi lukee
ajat, jotka Queensland Rail Travelin Service Updates -sivu näyttää: päivän
junien luettelon enintään 5 minuutin välein ja kunkin junan ajat enintään 5
minuutin välein 30 minuuttia ennen sen lähtöä 15 minuuttiin sen saapumisen
jälkeen. Jokainen juna sijoitetaan linjalleen näiden aikojen mukaan ja
merkitään arvioksi. Jokainen linja on oma kuvansa, omissa väreissään
Brisbanesta lähdettäessä ja värit vaihdettuina sinne mentäessä, junan numero
lapussa vieressä. Myöhässä tai paljon myöhässä ei näytetä.

### V/Line (Victoria, Australia)

Transport Victorian V/Line-syötteestä omalla avaimellasi: kaukolinjat
Alburyyn, Araratiin, Bairnsdaleen, Echucaan, Maryboroughiin, Sheppartoniin,
Swan Hilliin ja Warrnamboolin. Nimenä on junan numero. V/Linen violetti
keltaisella renkaalla Melbournesta lähdettäessä, värit vaihdettuina sinne
mentäessä. Syötteessä ei ole nopeutta, joten juna liikkuu kahden viimeisen
sijaintinsa välisellä nopeudella; kun uutta sijaintia ei ole tullut 10
minuuttiin, se ajoitetaan seuraavalle pysähdykselleen. Myöhässä 11 minuutista
alkaen pitkillä linjoilla ja 6 minuutista lyhyillä (V/Linen oma luettelo),
paljon myöhässä 30 minuutista.

### WA Trains (Länsi-Australia, Australia)

⚠ **Reaaliaikaisia sijainteja ei julkaista.** Jokainen juna piirretään
Länsi-Australian julkisen liikenteen viranomaisen aikataulusta: sijoitetaan
linjalleen aikataulun aikojen mukaan, merkitään arvioksi, ilman
myöhästymistä. Aikataulu tarkistetaan kerran päivässä. Nimenä on reitin kolme
ensimmäistä kirjainta: AUS (Australind, violetti), PRO (Prospector,
oranssi), MER (MerredinLink, vihreä) ja AVO (AvonLink, vihreä), samat
kumpaankin suuntaan.

### VR (Suomi)

Fintrafficin Digitrafficista, uusi sijainti noin 30 sekunnin välein. Nimenä
on junatyyppi ja numero niin kuin VR ne kirjoittaa (`IC 23`). VR:n vihreä
tummalla renkaalla Helsingistä lähdettäessä, värit vaihdettuina sinne
mentäessä. Tiedoissa ei ole suuntaa, joten nuoli seuraa linjaa. Myöhässä 6
minuutista alkaen (VR pitää junaa myöhässä, kun se on yli viisi minuuttia
myöhässä), paljon myöhässä 12 minuutista.

* **Joulupukin pikajuna** ensimmäisestä adventtisunnuntaista 6. tammikuuta
  asti: lumiukko pohjoiseen mentäessä, poro takaisin tultaessa, ilman
  numeroa. 12 minuutin myöhästymisestä alkaen hahmo kääntyy ympäri muutaman
  sekunnin välein.
* **Kesämökki** juhannusaatosta 31. heinäkuuta asti: jokainen VR:n kaukojuna
  piirretään mökkinä, numero vieressä.

### Irish Rail (Irlanti)

Irish Railin reaaliaikaisesta palvelusta ja Irlannin liikenneviranomaisen
(National Transport Authority) aikataulusta. ⚠ Irish Rail ilmoittaa junan vain
sen ohittaessa muutaman minuutin päässä toisistaan olevia
turvalaitekohtia, joten jokainen juna piirretään aikataulustaan ja
viimeisimmästä myöhästymisestään, siirrettynä reittiään pitkin. Nimenä on
junan numero ilman kirjainta (A700 näkyy 700). InterCity-juna on vihreä
apilanlehti oranssilla ääriviivalla ja numerolla Dublinista lähdettäessä,
värit vaihdettuina sinne mentäessä. Enterprise on hopeinen kiekko punaisella
ulkorenkaalla, magentalla nauhalla ja magentalla numerolla; Dubliniin
mentäessä kiekko on magenta. Myöhässä 10 minuutista alkaen (National
Transport Authorityn sääntö), paljon myöhässä 20 minuutista.

### NS, Arriva ja Keolis (Alankomaat)

NS:n kalustotiedoista omalla avaimellasi, uusi sijainti noin 10 sekunnin
välein. Tämä syöte ilmoittaa junan oman nopeuden ja suunnan, ja molemmat
välitetään eteenpäin. Seuraava pysähdys ja myöhästyminen tulevat OVapin
aikataulusta; raide on NS:n oma kartta linjoistaan, ladattuna kerran
päivässä. Nimenä on junan numero. NS:n junat ovat keltaisia NS:n sinisellä
renkaalla; Arrivan ja Keoliksen junilla on toistaiseksi karttakortin oma
ulkoasu. Myöhässä 3 minuutista alkaen (NS:n oma määritelmä), paljon myöhässä
10 minuutista.

### Vy, Go-Ahead Norge ja SJ Nord (Norja)

Enturista, kukin rautatie omana kohtanaan. Nimenä on linjatunnus (F4, RE10,
R50). Linjan oma väri valkoisella renkaalla Oslo S:ltä lähdettäessä (vuorolla,
joka ei kulje Oslo S:lle, sen suuremmalta pääteasemakaupungilta), värit
vaihdettuina sinne mentäessä. Entur ei julkaise nopeutta eikä suuntaa, joten
juna liikkuu kahden viimeisen sijaintinsa välisellä nopeudella ja nuoli
seuraa sen linjaa. Oslon pitkissä tunneleissa juna, jonka sijainnit
katkeavat, siirretään linjaansa pitkin, kunnes ne palaavat. ⚠ **SJ Nord ei
julkaise sijainteja:** jokainen sen juna sijoitetaan linjalleen odotettujen
aikojensa mukaan. Myöhässä 4 minuutista alkaen, F-linjoilla ja Göteborgin
(Ruotsi) linjoilla 6 minuutista, Bane NORin ja Vyn sääntö; paljon myöhässä
kaksinkertaisesta.

### Renfe (Spain) ja Renfe Regionals (Catalunya), Espanja

**Renfe (Spain)** lukee Renfen kaukoliikenteen syötettä, uusi sijainti noin
15 sekunnin välein. Nimenä on junan numero; palvelu (AVE, Avlo, Alvia ja niin
edelleen) on osoitinruudussa. AVE tummansininen, Avlo turkoosi, jokainen muu
palvelu Renfen violetti, kukin täytettynä Madridista lähdettäessä (vuorolla,
joka ei kulje Madridiin, sen suuremmasta pääteasemakaupungista) ja värit
vaihdettuina sinne mentäessä. Renfe ei julkaise reittiviivoja, joten linjat
on rakennettu OpenStreetMapista ja toimitetaan integraation mukana. Renfe ei
julkaise sääntöä myöhässä olevalle junalle, joten juna on myöhässä matkansa
pituuden mukaan: 10 minuutista alkaen 400 km:iin (250 mailiin) asti, 15
minuutista 560 km:iin (350 mailiin) asti, 20 minuutista 725 km:iin (450
mailiin) asti, 25 minuutista 885 km:iin (550 mailiin) asti, 30 minuutista
sitä pidemmillä; paljon myöhässä kaksinkertaisesta.

**Renfe Regionals (Catalunya)** piirtää Rodalies de Catalunyan aluelinjat
R11–R17. Nimenä on junan numero linjan omassa värissä, täytettynä
Barcelonasta lähdettäessä ja värit vaihdettuina sinne mentäessä. Barcelonan
ulkopuolella sijainti on viimeinen asema, jonka juna ohitti, joten juna
ajoitetaan asemien välillä aikataulun ja myöhästymisensä mukaan. Myöhässä 10
minuutista alkaen, paljon myöhässä 20 minuutista, pisimmän linjan pituuden
mukaan. Kun molemmat Renfen rautatiet ovat käytössä, jokainen juna
piirretään kerran.

### Ruotsin rautatiet (Ruotsi)

Trafikverketiltä omalla avaimellasi (yksi avain kaikille viidelletoista).
Nimenä on lipussa oleva junan numero; tuotemerkki, numero ja pääteasemat ovat
osoitinruudussa. Jokaisella tuotemerkillä on omat värinsä, vaihdettuina
Stockholm C:hen mentäessä (vuorolla, joka ei kulje Stockholm C:hen, sen
suurempaan pääteasemakaupunkiin). Trafikverket antaa nopeuden noin puoleen
sijainneistaan; muut junat liikkuvat kahden viimeisen sijaintinsa välisellä
nopeudella. Ruotsi ei julkaise reittiviivoja, joten linjat on rakennettu
OpenStreetMapista ja toimitetaan integraation mukana. Myöhässä 6 minuutista
alkaen (Trafikverket pitää junaa ajallaan 5 minuuttiin 59 sekuntiin asti),
paljon myöhässä 12 minuutista.

### VIA Rail (Kanada)

VIA Railin omista junan tilatiedoista. Jokainen juna on kiekko, jossa on
vaahteranlehti ja nauha reittiryhmänsä värissä (Atlantic, Western, Ontario ja
Quebec, Prince Rupert, Churchill, Sudbury–White River, Montréalin
maisemareitit), junan numero pystyssä olevassa lapussa. Parittomilla
numeroilla kiekko on keltainen, parillisilla nauhan värinen. Juna, jolla ei
ole uutta sijaintia, liikkuu kohti seuraavaa pysähdystään saapuakseen VIA:n
oman arvion mukaan. VIA ei julkaise sääntöä myöhässä olevalle junalle, joten
juna on myöhässä 10 minuutista alkaen Québec Cityn ja Windsorin välisellä
käytävällä ja 60 minuutista muualla (Amtrak Status Mapsin arvot VIA:lle),
paljon myöhässä kaksinkertaisesta.

### Amtrak (Yhdysvallat)

Amtrak ei julkaise avointa reaaliaikaista dataa. Amtraker välittää Amtrakin
oman junaseurannan, uusi sijainti 3–5 minuutin välein, ja integraatio
liikuttaa jokaista junaa linjaansa pitkin Amtrakin ilmoittamalla nopeudella.
Jokainen juna on tähti, jonka poikki on sen numero, reittinsä väreissä
(Northeastin reitit, Cascades, Pacific Surfliner, Acela ja muut), muuten
lipputähti. Maple Leaf (New Yorkista Torontoon) vaihtuu hitaasti Amtrakin
tähdestä VIA:n merkkiin. Rajalla Lacollessa, Rouses Pointissa tai Niagara
Fallsissa seisova juna näyttää myöhästymisen sijaan "Customs" (tulli).
Myöhässä 16 minuutista alkaen (Amtrak pitää junaa ajallaan 15 minuutin
sisällä), paljon myöhässä 30 minuutista. Sama junanumero voi kulkea kahtena
tai kolmena päivänä yhtä aikaa, joten jokainen vuoro on oma merkkinsä.

### Brightline (Yhdysvallat)

Brightlinen omasta syötteestä, uusi sijainti noin 60 sekunnin välein. Nimenä
on vuoron numero, mustana valkoisella ääriviivalla, kiekossa junan määränpään
värissä, mustalla renkaalla. Yli 5 minuuttia vanhaa sijaintia ei käytetä.
Syötteessä ei ole nopeutta, joten juna liikkuu kahden viimeisen sijaintinsa
välisellä nopeudella. Brightline ei julkaise sääntöä myöhässä olevalle
junalle, joten juna on myöhässä 10 minuutista alkaen, paljon myöhässä 20
minuutista, matkansa pituuden mukaan.

---

## Kaikki sen luomat entiteetit

Jokaiselle rautatielle:

| Entiteetti | Mikä se on |
|---|---|
| `sensor.<railroad>_trains_in_service` | **Trains in service** (liikenteessä olevat junat): kuinka monta junaa rautatie ajaa kartalla juuri nyt. Amtrakille: `sensor.amtrak_trains_in_service` |
| `geo_location.<railroad>_train_…` | yksi junaa kohden (`geo_location.amtrak_train_5_17`); se tulee ja menee junan mukana. Jokaisella on `source: live_track_intercity_rail`, ja sen tila on sen etäisyys kodistasi kilometreinä |

Merkin entiteettitunnus tulee rautatiestä ja vuorosta, ei koskaan sen
nimestä: `geo_location.amtrak_train_5_17` on Amtrakin juna 5, joka lähti
kuukauden 17. päivänä, joten juna säilyttää saman entiteettitunnuksen koko
vuoronsa ajan, ja saman numeron toinen vuoro saa omansa. Merkki poistetaan,
kun vuoro poistuu rautatien tiedoista tai päättyy. Merkeillä ei ole
yksilöllistä tunnusta (unique ID), kuten ei millään Live Trackin
karttamerkillä, joten niitä ei voi nimetä uudelleen, piilottaa tai liittää
alueeseen käyttöliittymässä. Anturilla on yksilöllinen tunnus, ja sen voi
nimetä uudelleen.

Jokaisella kyselyllä muuttuvat attribuutit, merkkien sijainnit ja ajat,
tallentuvat Home Assistantin historiaan, kuten minkä tahansa entiteetin.
Anturilla ei ole attribuutteja, joten sen säilyttäminen maksaa vähän, ja se on
tallenne siitä, kuinka monta junaa päivänä kulki. Pitääksesi merkit poissa
historiasta lisää tämä tiedostoon `configuration.yaml` ja käynnistä
uudelleen:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_train_*
```

Jos tiedostossasi `configuration.yaml` on jo `recorder:`-osio, lisää siihen
vain kuvio `geo_location.*_train_*`, kohtien `exclude:` ja `entity_globs:`
alle. Kuvio osuu vain tämän moduulin junamerkkeihin. Historiaa piirtämään
asetetulla karttakortilla ei silloin ole jälkeä piirrettävänä.

---

## Mitä se lähettää ja lataa

**Sijainnistasi.** Ei mitään. Kotisi sijaintia käytetään vain Home
Assistantisi sisällä, jokaisen junan etäisyyden laskemiseen. Avaimesi, jos
rautatie sellaisen tarvitsee, lähetetään vain sen rautatien
palveluntarjoajalle. Mitään muuta sinusta ei lähetetä mihinkään. Jokainen
palvelu näkee internetosoitteesi, kuten mikä tahansa verkkosivusto.

**Kuinka paljon.** Jokainen reaaliaikainen lähde luetaan jokaisella
kyselyllä, oletuksena rautatien omalla välillä (**Poll interval**, 15–600
sekuntia), tai harvemmin, jos taulukko niin kertoo. Jos useampi Live Track
-moduuli tai rautatie lukee samaa lähdettä, yksi yhteinen asiakas lukee sen
kerran kaikille. Mitattu 19. marraskuuta 2026 klo 02.44–02.49 UTC:

| Rautatie | Reaaliaikainen data, yksi luku | Aikataulu ja linjat |
|---|---|---|
| Journey Beyond (Australia) | ei mitään: mitään ei ladata | ei mitään: sen aikataulu ja linjat toimitetaan integraation mukana |
| NSW TrainLink (Australia) | 124 kt kahdesta syötteestä, enintään kerran 55 sekunnissa | 40 Mt, kun muuttunut, tarkistetaan päivittäin |
| Queensland Rail Travel (Australia) | luettelo, 5,5 kt, 5 minuutin välein; kunkin liikenteessä olevan junan ajat, 6–8 kt, 5 minuutin välein | ei mitään: sen linjat toimitetaan integraation mukana |
| V/Line (Australia) | 14 kt kahdesta syötteestä | 58 Mt (V/Linen osa Transport Victorian 311 Mt:n tiedostosta, luettuna erikseen), kun muuttunut, tarkistetaan päivittäin |
| WA Trains (Australia) | ei mitään: reaaliaikaista syötettä ei ole | 28 Mt, kun muuttunut, tarkistetaan päivittäin |
| VR (Suomi) | 1,4 kt pakattuna sijainneista; päivän junat, 0,5 Mt pakattuna ensimmäisellä kerralla, sitten vain muutokset, kerran minuutissa | 3,1 Mt, joka päivä |
| Irish Rail (Irlanti) | 0,2 kt, enintään kerran 55 sekunnissa | 6,6 Mt, kun muuttunut, tarkistetaan päivittäin; asemaluettelo, 46 kt, kerran viikossa |
| NS, Arriva, Keolis (Alankomaat) | 1,5 kt, enintään kerran 9 sekunnissa; myöhästymiset OVapilta, 5,3 Mt, 5 minuutin välein ja vain muuttuneina | OVapin aikataulu, 267 Mt, enintään kerran viikossa ja vain muuttuneena; NS:n raidekartta, 1,3 Mt, joka päivä |
| Vy, Go-Ahead Norge, SJ Nord (Norja) | Vy 510 kt kahdesta syötteestä, Go-Ahead Norge 7 kt, SJ Nord 0,7 kt kerran minuutissa | Vy 67 Mt, Go-Ahead Norge 20 Mt, SJ Nord 26 Mt, kun muuttunut, tarkistetaan päivittäin |
| Renfe (Spain) | 2,1 kt kahdesta syötteestä | 0,7 Mt, joka päivä; sen linjat toimitetaan integraation mukana |
| Renfe Regionals (Catalunya) | 0,2 kt kahdesta syötteestä, joissa ovat kaikki Renfen paikallisverkot | 16 Mt, joka päivä |
| Ruotsin rautatiet (Ruotsi) | 474 kt ensimmäisellä kerralla, sitten 5–9 kt muutoksia | ei mitään; asemaluettelo, 0,15 Mt, joka päivä; linjat toimitetaan integraation mukana |
| VIA Rail (Kanada) | 353 kt, lähetetään pakattuna 33 kt:na | 1,0 Mt, kerran viikossa |
| Amtrak (Yhdysvallat) | 1,2 Mt, lähetetään pakattuna 113 kt:na | 18,6 Mt, kerran viikossa |
| Brightline (Yhdysvallat) | 1,3 kt kahdesta syötteestä | 29 kt, kerran viikossa |

⚠ Mittaushetkellä Australiassa oli päivä, Pohjois-Amerikassa ilta ja
Euroopassa yö. Reaaliaikainen syöte on pienimmillään yöllä: päivällä
Euroopan syötteet ovat taulukkoa suurempia.

**Virheen jälkeen.** Junat liikkuvat viimeisten hyvien tietojen varassa
enintään 10 minuuttia; sitten ne merkitään ei saatavissa oleviksi, kunnes
lähde vastaa. Aikataulun epäonnistunutta latausta yritetään myöhemmin
uudelleen, ja hallussasi oleva kopio pysyy käytössä. Jos palveluntarjoaja
hylkää avaimesi kymmenen minuutin ajan, Home Assistant pyytää uutta.

**Levyllä.** Aikataulut ja reittiviivat säilytetään Home Assistantin
`.storage`-kansiossa nimillä, jotka alkavat `saw_`, yhteisinä muiden samaa
rautatietä lukevien Live Track -moduulien kanssa. Jos poistat Live Track
Intercity Railin eikä mikään muu Live Track -moduuli käytä niitä, voit
poistaa ne käsin.

---

## Auta sitä kasvamaan

Live Track Intercity Rail kasvaa yhä. Lisäämme rautateitä ja maita sitä mukaa
kuin löydämme niitä, ja haluamme tietää, mitä toivoisit seuraavaksi.

### Ehdota jotain

Puuttuuko maasi tai rautatiesi? Onko jokin väärin tai vaikea ymmärtää? Kerro
meille tavalla, joka on sinulle helpoin:

* [**Täytä lyhyt lomake**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=fi.yml)
  suomeksi. Tarvitset ilmaisen GitHub-tilin.
* **Lähetä sähköpostia** osoitteeseen
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Tiliä ei tarvita.

Kummin tahansa, auttaa, jos kerrot meille:

* mitä haluaisit nähdä, ja missä päin maailmaa;
* linkin paikkaan, jossa tiedot julkaistaan, jos tiedät sellaisen (avoimen
  datan sivu, julkinen syöte, palvelun verkkosivu): ei pakollista, mutta
  auttaa;
* Home Assistantisi kielen, jos ongelma koskee sanamuotoa tai käännöstä.

Kirjoita englanniksi tai omalla kielelläsi, kumpi on sinulle helpompaa.

### Lisää se itse, meidän avullamme

Jos haluat lisätä jotain itse, autamme sinua ensimmäisestä kysymyksestä
valmiiseen julkaisuun asti. Sinun ei tarvitse olla kehittäjä aloittaaksesi:

* **Käännös.** Asetusvalintaikkunan sanat ovat lyhyt lista lauseita yhdessä
  tekstitiedostossa. Näytämme, mikä tiedosto ja mitkä rivit.
* **Uusi rautatie.** Kerro meille, missä tiedot julkaistaan. Voimme kirjoittaa
  koodin yhdessä tai käydä omasi läpi.
* **Testaaminen siellä, missä asut.** Asenna se, katso omaa osaasi kartasta
  ja kerro, mikä on oikein ja mikä ei.
* **Korjaus tähän README-tiedostoon.** Jos jokin vaihe ei vastannut sitä,
  mitä näit, kerro meille, mitä näit.

[**Kerro meille, mitä sinulla on mielessä**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=fi.yml)
tai kirjoita osoitteeseen
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
niin vastaamme seuraavilla vaiheilla.

---

## Kielet

Tämä README: [English](README.md), [Deutsch](README.de.md), [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md), [Español](README.es.md),
[Italiano](README.it.md), [Dansk](README.da.md), **Suomi**, [Svenska](README.sv.md),
[Norsk bokmål](README.nb.md), [Gaeilge](README.ga.md). Jokainen käännetty README on täydellinen. Yksikään ei
ole vielä ollut äidinkielisen lukijan tarkistettavana. Jos suomi on
äidinkielesi, kerro meille, luetaanko tämä README sujuvasti: katso
[Auta sitä kasvamaan](#auta-sitä-kasvamaan).

Asetusvalintaikkuna ja asetukset ovat toistaiseksi vain englanniksi, oli Home
Assistantisi kieli mikä tahansa. Jos puhut jotain muuta kieltä, voit kääntää ne
itse: ne ovat lyhyt lista lauseita yhdessä tiedostossa, ja [autamme sinua
siinä](#lisää-se-itse-meidän-avullamme).

Löysitkö virheen käännöksestä, tai tarvitsetko toisen kielen? Kerro meille
osoitteessa <https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues>,
tai [käännä se meidän avullamme](#lisää-se-itse-meidän-avullamme).

---

## Tekijät ja lisenssit

Home Assistantisi lukee jokaisen reaaliaikaisen lähteen käytön aikana; mitään
reaaliaikaisesta syötteestä ei ole tässä tietovarastossa. Jokainen juna
mainitsee lähteensä `attribution`-attribuutissaan. Kunkin lähteen ehdot
sitovat sinua sen tietojen vastaanottajana.

* **Amtraker** (amtraker.com), joka välittää Amtrakin junaseurantaa
  (Yhdysvallat): data lisenssillä
  [Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/),
  lähdemaininta vaaditaan. **Amtrakin** oma aikataulu reittiviivoja varten.
* **Brightline** (Yhdysvallat): sen GTFS- ja GTFS-Realtime-syötteet;
  Brightline ei julkaise ehtoja.
* **VIA Rail** (Kanada): sen junan tilatiedot, joille VIA ei julkaise ehtoja;
  sen aikataulu lisenssillä Open Government Licence - Canada 2.0
  ([developer resources](https://www.viarail.ca/en/developer-resources)).
* **Fintraffic / digitraffic.fi** (Suomi): data lisenssillä CC BY 4.0.
* **Transport for NSW** (Australia): data lisenssillä CC BY 4.0
  ([datalisenssi](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australia): data lisenssillä CC BY 4.0
  ([avoin data](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Queensland Rail Travel** (Australia): ajat, jotka sen Service Updates
  -sivu näyttää, Home Assistantisi lukemina; katso
  [Queensland Railin tekijänoikeussivu](https://www.queenslandrailtravel.com.au/copyright).
  Mitään Queensland Rail Travelin omaa ei toimiteta integraation mukana.
* **Journey Beyond** (Australia): sen julkaistut aikataulut, kirjoitettuina
  tiedostoon `data/journey_beyond_timetable.json`; Journey Beyond ei julkaise
  niille ehtoja.
* **Länsi-Australian julkisen liikenteen viranomainen** (Public Transport
  Authority of Western Australia): aikataulutiedot saatavilla maksutta
  osoitteesta www.transperth.wa.gov.au
  ([spatial data access](https://www.transperth.wa.gov.au/About/Spatial-Data-Access);
  ei CC BY).
* **Renfe** (Espanja): data lisenssillä CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)).
* **Entur** (Norja): sisältää Norjan avoimen julkisen datan lisenssillä
  ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)) olevaa dataa, jota Entur
  jakelee.
* **Trafikverket** (Ruotsi): data lisenssillä [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Irlanti): reaaliaikainen data; Irish Rail ei julkaise ehtoja.
  Aikataulu [National Transport Authoritylta](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Irlanti), CC BY 4.0, sellaisenaan.
* **NS** (Alankomaat): kalustotiedot ja raidekartta omalla avaimellasi,
  [NS API portalin](https://apiportal.ns.nl/) ehdoin. Aikataulu ja
  myöhästymiset [OVapilta](https://gtfs.ovapi.nl/), CC0.
* **Kansiossa `data/` toimitettavat tiedostot**: Journey Beyondin,
  Queensland Rail Travelin, Renfe (Spain) -rautatien ja Ruotsin reittiviivat,
  rakennettu [OpenStreetMapista](https://www.openstreetmap.org/copyright),
  © OpenStreetMapin tekijät, lisenssillä
  [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/);
  Renfen vuorojen pääteasemakunnat (OpenStreetMap, ODbL 1.0) ja niiden
  väkiluvut (Wikidatan ominaisuus P1082, CC0, muuten OpenStreetMap);
  Ruotsin pääteasemakaupunkien väkiluvut Ruotsin tilastokeskukselta (SCB) ja
  Trafikverketiltä, molemmat CC0 1.0; Norjan pääteasemakaupunkien väkiluvut
  Norjan tilastokeskukselta (Statistics Norway), taulukko 04859, CC BY 4.0.
* **Karttakortti** on [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, kopio nathan-gsin [ha-map-cardista](https://github.com/nathan-gs/ha-map-card),
  MIT, toimitettuna kansiossa `frontend/`. Sen karttatiilet ja niiden
  lähdemaininnat ovat sen README-tiedostossa.

Mikään näistä organisaatioista ei tehnyt tai hyväksynyt tätä integraatiota.

**Koodi**: MIT, tiedostossa [LICENSE](LICENSE). Kansion `data/` tiedostot
säilyttävät lähteidensä lisenssit, jotka on lueteltu yllä.

**Kehittäjille:** jokainen rautatie on yksi moduuli kansiossa
`custom_components/live_track_intercity_rail/operators/`, ja se lukee
lähdesovitinta kansiossa `sources/`; toimitetut reittiviivat rakennetaan
uudelleen kansion `tools/` skripteillä (`journey_beyond.py`, `qrt_lines.py`,
`renfe_spain_lines.py`, `sweden_lines.py`). Testit ajetaan komennolla
`python -m unittest discover -s tests`.

---

## Hakusanat

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

**Kunnioitus.** StrausbergAutomationWorks tunnustaa kaikkien tämän kartan
kattamien maiden ja vesien alkuperäiskansat kaikkialla maailmassa ja osoittaa
kunnioitusta niiden vanhimmille, menneille ja nykyisille.
