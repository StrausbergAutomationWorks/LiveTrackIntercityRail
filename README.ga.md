# Live Track Intercity Rail

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · **Gaeilge** · [Gach teanga](#teangacha)

**Traenacha idirchathrach do Home Assistant, ar aon léarscáil amháin.** Cuireann
Live Track Intercity Rail gach traein de na hiarnróid idirchathrach agus
fadachair a roghnaíonn tú ar do léarscáil Home Assistant: cá bhfuil sí, a
huimhir, an bhfuil sí déanach de réir riail an iarnróid féin, agus an chéad
stad eile atá aici. Cuirtear gach iarnród leis ar leith, óna shonraí
foilsithe féin.

> **Modúl amháin de Live Track is ea Live Track Intercity Rail**, teaghlach de
> chomhtháthuithe Home Assistant a tharraingíonn gach rud a ghluaiseann, agus
> an aimsir trína ngluaiseann sé, ar aon léarscáil chomhroinnte amháin:
> aerárthaí, longa, traenacha agus aimsir. Suiteáil é leis féin, nó in
> éineacht leis na modúil eile ([liosta thíos](#cuid-de-live-track-na-modúil-eile)).

> **Ag fás, agus oscailte do smaointe.** Clúdaíonn Live Track Intercity Rail
> 33 iarnród i 9 dtír ar 3 mhór-roinn inniu, agus táimid ag cur tuilleadh
> iarnród agus tíortha leis. An bhfuil d'iarnród féin in easnamh?
> [Mol é](#cuidigh-leis-fás), nó cuir leis tú féin é: cuideoimid leat.

**Stádas: 0.1.4, eisithe.** I gcatalóg an Mhargaidh ([suiteáil thíos
é](#suiteáil-é-céim-ar-chéim)).

Saothar bunaidh le StrausbergAutomationWorks. Níl baint aige le, ná formhuiniú
ó, Amtrak, Amtraker, Brightline, VIA Rail, Fintraffic, VR, Transport for NSW,
NSW TrainLink, Transport Victoria, V/Line, Queensland Rail, Journey Beyond,
údarás iompair phoiblí Iarthar na hAstráile (Public Transport Authority of
Western Australia), Transwa, Renfe, Rodalies de Catalunya, Entur, Vy,
Go-Ahead Norge, SJ Nord, Trafikverket, SJ, VR Snabbtåg, Snälltåget,
Öresundståg, Pågatågen, Mälartåg, Västtågen, Krösatågen, Östgötapendeln,
Norrtåg, Tåg i Bergslagen, X-Tåget, Värmlandstrafik, Tågab, Inlandsbanan,
Irish Rail (Iarnród Éireann), an tÚdarás Náisiúnta Iompair (National
Transport Authority, Éire), NS, Arriva, Keolis, OVapi, ná aon iarnród eile.

---

## Clár ábhair

1. [Gach rud a dhéanann sé](#gach-rud-a-dhéanann-sé)
2. [Cá n-oibríonn sé](#cá-n-oibríonn-sé)
3. [Cuid de Live Track: na modúil eile](#cuid-de-live-track-na-modúil-eile)
4. [Sula dtosaíonn tú](#sula-dtosaíonn-tú)
5. [Suiteáil é, céim ar chéim](#suiteáil-é-céim-ar-chéim)
6. [Socraigh é, céim ar chéim](#socraigh-é-céim-ar-chéim)
7. [Eochracha saor in aisce a chuireann tuilleadh ar siúl, céim ar chéim](#eochracha-saor-in-aisce-a-chuireann-tuilleadh-ar-siúl-céim-ar-chéim)
8. [Cuir an léarscáil ar phainéal](#cuir-an-léarscáil-ar-phainéal)
9. [Úsáid é in uathoibrithe](#úsáid-é-in-uathoibrithe)
10. [Gach rud ar an léarscáil, go mion](#gach-rud-ar-an-léarscáil-go-mion)
11. [Na haonáin go léir a chruthaíonn sé](#na-haonáin-go-léir-a-chruthaíonn-sé)
12. [Cad a sheolann sé agus a íoslódálann sé](#cad-a-sheolann-sé-agus-a-íoslódálann-sé)
13. [Cuidigh leis fás](#cuidigh-leis-fás)
14. [Teangacha](#teangacha)
15. [Creidiúintí agus ceadúnais](#creidiúintí-agus-ceadúnais)
16. [Eochairfhocail](#eochairfhocail)

---

## Gach rud a dhéanann sé

### Ar an léarscáil, gan aon rud le socrú

Cuireann tú **iarnród** leis: roghnaíonn tú tír, ansin ceann dá hiarnróid
idirchathrach. Feictear gach rud thíos ansin don iarnród sin. Cuir an
comhtháthú leis arís do gach iarnród eile atá uait.

| Cad é | Cá háit | Ó |
|---|---|---|
| **Traenacha i seirbhís**: marcóir amháin in aghaidh na traenach, lipéadaithe lena huimhir nó lena líne, i ndathanna an iarnróid féin, casta i dtreo a taistil | gach iarnród | sonraí foilsithe gach iarnróid féin |
| **Déanacht**: taispeántar traein mar dhéanach nó an-déanach de réir riail an iarnróid féin; nuair nach bhfoilsíonn iarnród aon riail, de réir chomh fada is a thaistealaíonn an traein | gach iarnród a thuairiscíonn moill | fotha gach iarnróid féin |
| **An chéad stad eile agus a am**: an stáisiún ag a stadfaidh an traein ina dhiaidh seo, agus cathain a bhfuiltear ag súil léi ann | gach iarnród a luann a fhotha nó a amchlár é | fotha agus amchlár gach iarnróid féin |
| **Traenacha a leanann na ráillí**: idir dhá thuairisc, gluaiseann traein feadh a líne féin ag a luas deireanach, ní díreach trasna | gach iarnród a bhfuil a líne ar eolas | amchlár gach iarnróid, nó línte a sheoltar leis an gcomhtháthú |
| **Traenacha ón amchlár**: nuair nach bhfoilsíonn iarnród aon suíomh, cuirtear gach traein ar a líne de réir a hamanna, agus marcáiltear í mar mheastachán | Journey Beyond, Queensland Rail Travel agus WA Trains (An Astráil), SJ Nord (An Iorua); Irish Rail lena moill is déanaí | amchlár nó amanna gach iarnróid |
| **Pictiúir do roinnt traenacha**: Traein Dhaidí na Nollag agus teachín samhraidh (An Fhionlainn), ainmhithe thraenacha Journey Beyond, pictiúr do gach líne de chuid Queensland Rail Travel | An Fhionlainn, An Astráil | tarraingthe don chomhtháthú seo |
| **Stoptha ag an teorainn**: taispeánann traein atá ina seasamh ag pointe trasnaithe teorann idir Stáit Aontaithe Mheiriceá agus Ceanada "Customs" (custaim) in áit a moille | traenacha Amtrak go Ceanada agus as | suíomhanna Amtrak |
| **Líon amháin in aghaidh an iarnróid**: traenacha i seirbhís | gach iarnród | na sonraí céanna |

### Le heochair nó cuntas saor in aisce de do chuid féin

| Eochair nó cuntas saor in aisce | Cad a chuireann sé leis |
|---|---|
| Eochair **Transport for NSW Open Data** | traenacha réigiúnacha NSW TrainLink (New South Wales, An Astráil) |
| Eochair **Transport Victoria Open Data** | traenacha fadachair V/Line (Victoria, An Astráil) |
| Eochair **NS API portal** | NS Intercity, agus traenacha réigiúnacha Arriva agus Keolis (An Ísiltír); freastalaíonn eochair amháin ar an triúr |
| Eochair **Trafikverket** | na 15 iarnród Sualannacha; freastalaíonn eochair amháin ar an gcúig cinn déag |

Tógann gach ceann acu cúpla nóiméad le fáil: [céim ar chéim thíos](#eochracha-saor-in-aisce-a-chuireann-tuilleadh-ar-siúl-céim-ar-chéim).
Ní theastaíonn eochair ó na 13 iarnród eile.

---

## Cá n-oibríonn sé

| Réigiún | Cad a fhaigheann tú | Ó | Teastaíonn |
|---|---|---|---|
| **An Astráil**: ar fud na tíre | Journey Beyond: The Ghan, The Ghan Expedition, Indian Pacific, Great Southern, The Overland, ón amchlár amháin ([cén fáth](#journey-beyond-an-astráil)) | Journey Beyond | faic |
| **An Astráil**: New South Wales | traenacha réigiúnacha NSW TrainLink (XPT agus Xplorer), isteach i Queensland, i Victoria agus i gCríoch Phríomhchathair na hAstráile freisin | Transport for NSW | eochair saor in aisce |
| **An Astráil**: Queensland | Queensland Rail Travel: Spirit of Queensland, Spirit of the Outback, Tilt Train, Westlander, Inlander, Kuranda Scenic Railway, Gulflander, óna n-amanna foilsithe ([cén fáth](#queensland-rail-travel-an-astráil)) | Queensland Rail Travel | faic |
| **An Astráil**: Victoria | traenacha fadachair V/Line (tá a línte comaitéara in Live Track Commuter Rail), isteach i New South Wales freisin | Transport Victoria | eochair saor in aisce |
| **An Astráil**: Iarthar na hAstráile | WA Trains: an Australind, an Prospector, an MerredinLink agus an AvonLink, ón amchlár amháin ([cén fáth](#wa-trains-iarthar-na-hastráile-an-astráil)) | údarás iompair phoiblí Iarthar na hAstráile | faic |
| **An Eoraip**: An Fhionlainn | traenacha fadachair VR | Fintraffic Digitraffic | faic |
| **An Eoraip**: Éire | traenacha InterCity Irish Rail (Iarnród Éireann), agus an Enterprise ó Bhaile Átha Cliath go Béal Feirste (An Ríocht Aontaithe) | Irish Rail, an tÚdarás Náisiúnta Iompair | faic |
| **An Eoraip**: An Ísiltír | NS Intercity, agus traenacha réigiúnacha Arriva (Arriva, RRReis, Blauwnet) agus Keolis (Blauwnet, RRReis); tá Sprinters NS in Live Track Commuter Rail | NS, OVapi | eochair saor in aisce |
| **An Eoraip**: An Iorua | línte F, RE, RX agus R Vy (F1 isteach sa tSualainn freisin), F5 agus R50 Go-Ahead Norge, F6, F7 agus R60 go R75 SJ Nord | Entur | faic |
| **An Eoraip**: An Spáinn | traenacha AVE, Avlo, Alvia, Avant, Euromed, Intercity, MD agus Regional Renfe, isteach san Fhrainc agus sa Phortaingéil freisin; línte réigiúnacha R11 go R17 Rodalies de Catalunya | Renfe | faic |
| **An Eoraip**: An tSualainn | SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget, Värmlandstrafik, Tågab agus Inlandsbanan, iarnród an ceann; Öresundståg isteach sa Danmhairg freisin | Trafikverket | eochair saor in aisce |
| **Meiriceá Thuaidh**: Ceanada | VIA Rail, gach bealach | VIA Rail | faic |
| **Meiriceá Thuaidh**: Stáit Aontaithe Mheiriceá | Amtrak, gach bealach, isteach i gCeanada freisin | Amtraker | faic |
| **Meiriceá Thuaidh**: Stáit Aontaithe Mheiriceá | Brightline (Florida) | Brightline | faic |

Níl sé ar an liosta? [Inis dúinn](#cuidigh-leis-fás). Nuair a fhoilsíonn
duine éigin na sonraí go hoscailte, féachfaimid ar é a chur leis.

⚠ **Níl traein níos fearr ná sonraí a hiarnróid.** Tuairiscíonn roinnt
iarnród traein gach cúpla soicind, roinnt gach cúpla nóiméad, roinnt nuair a
théann sí thar chomharthaí amháin, agus ní fhoilsíonn roinnt suíomhanna ar
chor ar bith. Tá teorainneacha gach iarnróid faoi
[Gach rud ar an léarscáil, go mion](#gach-rud-ar-an-léarscáil-go-mion).

⚠ **Ní hé seo eolas oifigiúil an iarnróid.** Sula dtaistealaíonn tú, seiceáil
aip nó suíomh gréasáin an iarnróid féin.

---

## Cuid de Live Track: na modúil eile

Is sraith de chomhtháthuithe Home Assistant é Live Track, ceann amháin do gach
cineál ruda a ghluaiseann, iad ar fad tarraingthe ar an gcárta léarscáile
céanna. Oibríonn gach ceann leis féin; le chéile déanann siad pictiúr beo
amháin. Roinneann siad an cárta léarscáile agus leabharlann Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
mar sin ní chuireann modúl eile a shuiteáil iarratais le foinse atá á léamh ag
modúl eile cheana.

| Modúl | Cad a chuireann sé ar an léarscáil | Stádas |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aerárthaí os do chionn ó ADS-B, le bealaí agus deilbhíní de réir cineáil | eisithe |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | longa agus báid ó AIS, in aice leat nó áit ar bith | eisithe |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | traenacha comaitéara i Meiriceá Thuaidh, san Eoraip agus san Astráil | eisithe |
| **Live Track Intercity Rail** | traenacha idirchathrach agus fadachair i Meiriceá Thuaidh, san Eoraip agus san Astráil (an modúl seo) | eisithe |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | aerárthaí agus soithí inimirce agus forfheidhmithe dlí cónaidhme, ó liostaí poiblí | eisithe |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | aimsir, stoirmeacha agus guaiseacha nádúrtha | eisithe |
| [Live Track Internet](https://github.com/StrausbergAutomationWorks/LiveTrackInternet) | cliseadh idirlín, cáblaí fomhuirí agus naisc talún | eisithe |
| Live Track Stations | cláir imeachta agus foláirimh "am imeacht" do gach stáisiún | beartaithe |
| Live Track Satellites | satailítí ag dul thar bráid os do chionn | beartaithe |
| Live Track Freight Trains | traenacha lastais agus oibre nuair a fhoilsíonn iarnróid iad | beartaithe |
| Live Track Transit | busanna cathrach, tramanna, báid farantóireachta agus meitreo | beartaithe |
| Live Track Intercity Buses | cóistí idirchathrach agus réigiúnacha | beartaithe |
| Live Track Commuter Buses | busanna comaitéara | beartaithe |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | an cárta léarscáile comhroinnte a dtarraingíonn gach modúl air | eisithe, suiteáilte le gach modúl |

Tá gach rud saor in aisce agus foinse oscailte. Ní choinnítear aon rud siar do
lucht urraíochta.

---

## Sula dtosaíonn tú

* **Home Assistant** 2026.11 nó níos déanaí.
* **An Margadh** (HACS) i do Home Assistant, chun é a shuiteáil agus a
  nuashonrú ar an mbealach éasca. Gan é, is féidir leat na comhaid a chóipeáil
  de láimh.
* **Rochtain ar an idirlíon** do Home Assistant: tagann gach traein ó shonraí
  foilsithe a hiarnróid féin.
* Faic le híoc. Ní theastaíonn cuntas ó 13 de na 33 iarnród; teastaíonn
  eochair saor in aisce de do chuid féin ón 20 eile, agus clúdaíonn ceithre
  eochair iad go léir
  ([thuas](#le-heochair-nó-cuntas-saor-in-aisce-de-do-chuid-féin)).
* Suiteálann Home Assistant na pacáistí Python a theastaíonn uaidh
  (`saw-livetrack`, `gtfs-realtime-bindings` agus `tzdata`) leis féin an chéad
  uair a lódáiltear an comhtháthú.

---

## Suiteáil é, céim ar chéim

### Ón Margadh (molta)

1. In Home Assistant, oscail **Socruithe → Margadh** (HACS).
2. Cuardaigh **Live Track Intercity Rail** agus oscail é.
3. Roghnaigh **Download** (nó **Suiteáil**).
4. **Atosaigh Home Assistant**: tairgeann **Socruithe → Córas →
   Deisiúcháin** an t-atosú, nó úsáid **Socruithe → Córas → Atosaigh**.

Mura n-aimsíonn an cuardach é, cuir leis é trína nasc: roghnaigh **Cuir leis ón
nasc** (nó an roghchlár trí phonc → **Stórtha saincheaptha**), iontráil
`StrausbergAutomationWorks/LiveTrackIntercityRail`, roghnaigh **Comhtháthú** má
iarrtar an cineál, agus ansin lean ar aghaidh ó chéim 3.

Tairgeann an Margadh gach eisiúint nua mar nuashonrú ina dhiaidh sin.

### De láimh

1. Íoslódáil cód foinse na
   [heisiúna is déanaí](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/releases/latest).
2. Cóipeáil a fhillteán `custom_components/live_track_intercity_rail` isteach
   i bhfillteán `custom_components` d'fhillteán cumraíochta Home Assistant
   (cruthaigh `custom_components` mura bhfuil sé ann).
3. Atosaigh Home Assistant.

Chun é a nuashonrú de láimh, cuir fillteán na heisiúna nua in áit an
fhillteáin agus atosaigh.

---

## Socraigh é, céim ar chéim

1. Oscail **Socruithe → Gléasanna & seirbhísí**.
2. Roghnaigh **Cuir comhtháthú leis** (thíos ar dheis) agus cuardaigh
   **Live Track Intercity Rail**.
3. **Region** (réigiún): roghnaigh tír an iarnróid. Ní liostaítear ach tíortha
   a bhfuil iarnród amháin ar a laghad iontu. Roghnaigh **Cuir isteach**.
4. **Railroad** (iarnród): roghnaigh an t-iarnród. Roghnaigh **Cuir
   isteach**.
5. **API key** (eochair API): do NSW TrainLink, do V/Line, do na trí iarnród
   Ollannacha agus do na cúig iarnród déag Sualannacha amháin. Greamaigh
   d'eochair ([conas ceann a fháil](#eochracha-saor-in-aisce-a-chuireann-tuilleadh-ar-siúl-céim-ar-chéim))
   agus roghnaigh **Cuir isteach**. Scipeálann na hiarnróid eile an chéim
   seo.

Sin é. Feictear na traenacha laistigh de nóiméad nó dhó. Nuair a thagann
línte iarnróid óna amchlár, tosaíonn na traenacha ag leanúint a línte nuair
atá an t-amchlár íoslódáilte, rud a d'fhéadfadh cúpla nóiméad a thógáil an
chéad uair. Chun faire ar iarnród eile, cuir an comhtháthú leis arís. Diúltaítear
don iarnród céanna faoi dhó.

### Athraigh a dtaispeánann sé: na roghanna

Oscail **Socruithe → Gléasanna & seirbhísí → Live Track Intercity Rail →
Cumraigh** (an roth fiaclach) ar an iarnród is mian leat a athrú. Tá rogha
amháin ann:

| Rogha | Cad a dhéanann sí | Réamhshocrú |
|---|---|---|
| **Poll interval** (eatramh ceistiúcháin) | cé chomh minic a léitear foinse an iarnróid, 15 go 600 soicind. Ní thaispeánann eatramh níos giorra ná athnuachan na foinse féin aon rud breise | socraithe de réir iarnróid: 15 soicind do Renfe (Spain) agus do na trí iarnród Ollannacha; 60 soicind do Brightline, NSW TrainLink, Irish Rail agus SJ Nord; 30 soicind do na cinn eile |

---

## Eochracha saor in aisce a chuireann tuilleadh ar siúl, céim ar chéim

Iarrann fiche iarnród a eochair féin ar gach úsáideoir, ó cheithre sholáthraí.
Tá gach ceann de na heochracha seo saor in aisce, agus faigheann gach duine a
shuiteálann Live Track Intercity Rail a eochair féin. Greamaíonn tú an eochair
nuair a iarrann an dialóg socraithe í ([céim 5 thuas](#socraigh-é-céim-ar-chéim)).
Ní iarrtar ach an eochair: gan pasfhocal agus gan rún. Stóráiltear an eochair
in Home Assistant leis an gcomhtháthú, ní sheoltar í ach chuig a soláthraí
féin, agus ní scríobhtar riamh sa loga í. Má dhiúltaíonn an soláthraí di ar
feadh deich nóiméad, iarrann Home Assistant eochair nua ort.

### Transport for NSW (NSW TrainLink, New South Wales, An Astráil)

1. Oscail <https://opendata.transport.nsw.gov.au/>, roghnaigh **Register**,
   cruthaigh cuntas, agus logáil isteach.
2. Roghnaigh deilbhín do phróifíle úsáideora, ansin **API Tokens**.
3. Clóscríobh ainm don eochair agus roghnaigh **CREATE API TOKEN**. Cóipeáil
   an eochair láithreach: ní thaispeánann an suíomh í ach uair amháin.
4. Greamaigh í in **API key** nuair a chuireann tú NSW TrainLink leis.
   Greamaigh an eochair amháin: cuireann Live Track Intercity Rail an focal
   `apikey` leis féin.

### Transport Victoria (V/Line, Victoria, An Astráil)

1. Oscail <https://opendata.transport.vic.gov.au/>, roghnaigh **Login**, ansin
   **Sign up**.
2. Iontráil do shonraí agus roghnaigh **Create Account**. Iontráil an cód ón
   ríomhphost a fhaigheann tú agus roghnaigh **Confirm**.
3. Iarrann an tairseach aip fhíordheimhnithe ar d'fhón: scan an cód QR léi,
   iontráil cód na haipe agus roghnaigh **Confirm**. Ansin sínigh isteach le
   do ríomhphost, do phasfhocal agus cód na haipe.
4. Roghnaigh **My Account** → **Profile** → **API tokens**. Tá d'eochair ann
   cheana. Greamaigh í in **API key** nuair a chuireann tú V/Line leis.

### NS (NS, Arriva agus Keolis, An Ísiltír)

1. Oscail <https://apiportal.ns.nl/>, roghnaigh **Inloggen** (logáil isteach),
   ansin **Externe bezoeker** (cuairteoir seachtrach).
2. Líon isteach an fhoirm agus seol í. Deimhníonn ríomhphost an clárú. Is
   féidir go dtógfaidh sé suas le 5 nóiméad sula bhfeictear na APIanna sa
   tairseach.
3. Oscail leathanach an **Virtual Train API** (suíomhanna traenacha NS). Faoi
   **Related Products**, oscail a tháirge, tabhair ainm do do shíntiús, agus
   roghnaigh **Subscribe**.
4. Nuair a bheidh an síntiús ceadaithe ag NS, beidh d'eochair ar leathanach do
   phróifíle. Greamaigh í in **API key** nuair a chuireann tú NS, Arriva nó
   Keolis leis. Freastalaíonn eochair amháin ar an triúr.

### Trafikverket (na 15 iarnród Sualannacha)

1. Oscail <https://data.trafikverket.se/oauth2/Account/register>.
2. Líon isteach **Email**, **Displayname**, **Password** agus **Confirm
   password**, cuir tic le **Accept license and Agreement**, agus roghnaigh
   **Register**.
3. Oscail <https://data.trafikverket.se/get-started> agus roghnaigh **Create
   key**, faoi **Create a key**. Sínigh isteach leis an gcuntas a rinne tú, agus
   cruthaigh an eochair.
4. Greamaigh í in **API key** nuair a chuireann tú iarnród Sualannach leis.
   Freastalaíonn eochair amháin ar an gcúig cinn déag.

---

## Cuir an léarscáil ar phainéal

Is é [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
an léarscáil, an cárta a dtarraingíonn gach modúl Live Track air. **Suiteáiltear
é le Live Track Intercity Rail**: faic le híoslódáil, faic le cóipeáil, gan
acmhainn le cur leis.

1. Oscail painéal, roghnaigh an peann luaidhe (**Cuir painéal in eagar**),
   ansin **Cuir cárta leis**.
2. Scrollaigh go dtí an bun agus roghnaigh **Lámhleabhar**.
3. Greamaigh é seo, agus roghnaigh **Sábháil**:

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

Téann modúil eile Live Track in `entity_filter` ar an mbealach céanna: riail
`- domain: geo_location` eile do gach foinse.

**Ar an léarscáil:**

* Is marcóir i ndathanna a hiarnróid gach traein, lipéadaithe lena huimhir nó
  lena líne. Is réaltaí iad traenacha Amtrak, tá an duilleog mhailpe ar
  thraenacha VIA Rail, is seamróga iad traenacha InterCity Irish Rail, agus is
  pictiúir iad roinnt traenacha (deir gach iarnród thíos cé acu).
* Ar fhormhór na n-iarnród malartaíonn na dathanna leis an treo: dath amháin ag
  fágáil na príomhchathrach, an dath eile ag dul i dtreo uirthi.
* Taispeánann saighead an treo ina dtaistealaíonn an traein. Coinníonn traein
  atá ina seasamh a treo deireanach. Fanann pictiúir ina seasamh díreach agus
  níl saighead acu.
* **Dírigh** ar thraein chun a hiarnród, a huimhir, a líne agus cá dtaistealaíonn
  sí a fheiceáil. **Cliceáil** uirthi chun a sonraí go léir a fheiceáil, an
  chéad stad eile agus a moill san áireamh.

Má tá acmhainní do phainéal socraithe i YAML (`lovelace: resource_mode: yaml`),
ní féidir aon rud a chlárú duit: tugann fadhb faoi **Deisiúcháin** ansin na
línte cruinne le cur le `configuration.yaml`. Breathnaíonn siad mar seo, le
seoladh an chomhtháthaithe féin in áit na sealbhóirí áite:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_intercity_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Tá cóip den chárta ag gach modúl Live Track agus cláraíonn sé í nuair a
thosaíonn Home Assistant. Le chéile coinníonn siad díreach sraith amháin in
**Socruithe → Deais → Acmhainní**: an leagan is nuaí den chárta atá ag aon cheann
acu, riamh leagan níos sine. Fágtar cárta a shuiteáil tú féin tríd an Margadh
mar atá sé. Nuair a bhaineann tú an t-iarnród deireanach den mhodúl seo, téann
an tsraith chuig modúl Live Track eile, nó baintear í mura bhfuil ceann ar bith
fágtha. Má bhaintear comhaid an chomhtháthaithe fad atá a hiarnróid socraithe
fós, agus nach bhfuil aon mhodúl Live Track eile suiteáilte, bain an tsraith tú
féin in **Socruithe → Deais → Acmhainní**.

**Chun an cárta a shuiteáil de láimh ina ionad sin**, lean na céimeanna in
[README an chárta](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
Ní athraítear agus ní bhaintear choíche sraith a rinne tú féin do chóip faoi
`/local/` nó ag seoladh ar bith eile. Fad is a lódálann sí an cárta, fágann gach
modúl Live Track an cárta fúithi, fiú nuair atá eisiúint níos nuaí ag modúl,
agus ní luann aon rud in **Deisiúcháin** é. Chun filleadh ar chóip an mhodúil,
bain do shraith in **Socruithe → Deais → Acmhainní** agus atosaigh Home
Assistant. Má scriosann tú comhad do chóipe, bain a sraith freisin: fad is a
fhanann sraith nach bhfuil a comhad ann a thuilleadh, ní chuireann an modúl
sraith dá chuid féin leis.

Taispeánann aon chárta léarscáile eile a thaispeánann aonáin `geo_location`
na traenacha freisin, mar ghnáthmharcóirí.

---

## Úsáid é in uathoibrithe

Is gnáthaonán Home Assistant gach rud, mar sin oibríonn an t-eagarthóir
uathoibrithe leo, gan cód.

**Fógra ar d'fhón nuair a stopann sonraí d'iarnróid** (fágann na traenacha an
léarscáil ansin):

1. **Socruithe → Uathoibriú agus radhairc → Cruthaigh uathoibriú → Cruthaigh
   uathoibriú nua**.
2. **Cathain**: **Cuir truicear leis** → **Aonán** → **State changed**.
   Roghnaigh aonán **Trains in service** (traenacha i seirbhís) an iarnróid,
   agus faoi **Go (roghnach)** roghnaigh **Níl fáil air**.
3. **Ansin a dhéanamh**: **Cuir gníomh leis**, cuardaigh gníomh fógra d'fhóin
   (tá ainm d'fhóin air), agus iontráil teachtaireacht, mar shampla:

   ```text
   Níl aon traein idirchathrach ar an léarscáil: stop sonraí an iarnróid
   ```

4. **Sábháil**.

**Smaointe eile:** solas a lasann nuair atá traein Amtrak laistigh de 2 km (1.2
míle) de do theach i Stáit Aontaithe Mheiriceá, ó fhad na marcóirí; líon ar
phainéal de na traenacha a ritheann VR san Fhionlainn i rith an lae;
teachtaireacht nuair a fhágann an chéad traein den lá de chuid Queensland Rail
Travel (An Astráil), nuair a éiríonn **Trains in service** os cionn 0.

---

## Gach rud ar an léarscáil, go mion

### Traenacha

Is marcóir amháin gach traein. Is é a staid a fad ó do theach, i
gciliméadair. Feictear an marcóir nuair a thuairiscíonn an t-iarnród an
traein, nó nuair a deir a hamchlár go bhfuil sí ag rith, agus baintear é nuair
a fhágann an traein sonraí an iarnróid nó nuair atá a turas thart.

* **Idir dhá thuairisc** gluaiseann traein feadh a líne féin i dtreo a chéad
  stad eile: ag an luas a thuairiscíonn an t-iarnród, nó, mura dtuairiscíonn
  sé aon luas, ag an luas idir a dhá thuairisc dheireanacha. Ní théann sí
  thar a chéad stad eile riamh, agus stopann sí ag gluaiseacht 30 nóiméad tar
  éis na tuairisce deireanaí. Tarraingítear traein ar líne aitheanta ar an
  líne; coinnítear tuairisc an iarnróid féin lena taobh.
* **Má theipeann ar shonraí iarnróid**, leanann a thraenacha ag gluaiseacht ar
  a dtuairisc mhaith dheireanach ar feadh suas le 10 nóiméad. Ina dhiaidh sin
  níl fáil orthu agus fágann siad an léarscáil go dtí go dtagann na sonraí ar
  ais.
* **Déanach agus an-déanach**: nuair a fhoilsíonn an t-iarnród a riail féin do
  thraein dhéanach, úsáideann an comhtháthú í. Mura bhfoilsíonn sé aon riail,
  bíonn traein déanach de réir chomh fada is a thaistealaíonn sí, le tairseacha
  Amtrak Status Maps (asm.transitdocs.com). Deir gach iarnród thíos cé acu.

Ar gach traein: `marker_label`, `train`, `line_name`, `observed_at` (cathain a
bhí a tuairisc fíor), `course_deg` (fad atá sí ag gluaiseacht), `next_stop`
agus `arrival_estimated_at` (nuair is eol), `delay_min`, `late_threshold_min`
agus `very_late_threshold_min`, `speed_kmh` (nuair a thuairiscíonn an
t-iarnród é), `attribution`, agus, idir dhá thuairisc, `previous_latitude`,
`previous_longitude`, `previous_observed_at` agus `segment_duration_s`. Tá
`position_source: estimated` ar thraein a bogadh feadh a líne, le tuairisc an
iarnróid in `fix_latitude` agus `fix_longitude`.

### Journey Beyond (An Astráil)

⚠ **Ní fhoilsíonn Journey Beyond aon suíomh.** Tarraingítear gach traein óna
hamchlár foilsithe, tras-scríofa i gcomhad a sheoltar leis an gcomhtháthú
(imeachtaí go dtí 29 Nollaig 2027), mar sin ní íoslódáiltear faic. Cuirtear
gach traein ar a líne de réir a hamanna, marcáilte mar mheastachán, gan moill:
tarraingítear traein dhéanach nó chealaithe in am mar sin féin. Is pictiúr dá
chuid féin gach seirbhís (an camall agus a mharcach, éan, cangarú, eimiú), ina
dathanna ag dul amach agus malartaithe ag teacht ar ais, gan lipéad: dírigh
air chun an traein agus a turas a fheiceáil.

### NSW TrainLink (New South Wales, An Astráil)

Ó fhotha NSW TrainLink de chuid Transport for NSW, le d'eochair féin, suíomh
nua timpeall uair sa nóiméad. Is é uimhir na traenach an lipéad. Oráiste NSW
le fáinne bán ag fágáil Sydney, malartaithe ag dul ann. Níl luas san fhotha,
mar sin gluaiseann traein feadh a líne ag an luas idir a dhá shuíomh
dheireanacha. Déanach ó 11 nóiméad (áiríonn NSW TrainLink traein in am laistigh
de 10 nóiméad), an-déanach ó 30.

### Queensland Rail Travel (An Astráil)

⚠ **Ní fhoilsíonn Queensland Rail Travel aon suíomh.** Léann do Home Assistant
na hamanna a thaispeánann leathanach Service Updates Queensland Rail Travel:
liosta thraenacha an lae gach 5 nóiméad ar a mhéad, agus amanna gach traenach
gach 5 nóiméad ar a mhéad ó 30 nóiméad sula bhfágann sí go dtí 15 nóiméad tar
éis di teacht. Cuirtear gach traein ar a líne de réir na n-amanna sin agus
marcáiltear í mar mheastachán. Is pictiúr dá chuid féin gach líne, ina dathanna
ag fágáil Brisbane agus malartaithe ag dul ann, le huimhir na traenach i
gclib lena taobh. Ní thaispeántar déanach ná an-déanach.

### V/Line (Victoria, An Astráil)

Ó fhotha V/Line de chuid Transport Victoria, le d'eochair féin: na línte
fadachair go Albury, Ararat, Bairnsdale, Echuca, Maryborough, Shepparton, Swan
Hill agus Warrnambool. Is é uimhir na traenach an lipéad. Corcra V/Line le
fáinne buí ag fágáil Melbourne, malartaithe ag dul ann. Níl luas san fhotha,
mar sin gluaiseann traein ag an luas idir a dhá shuíomh dheireanacha; tar éis
10 nóiméad gan suíomh nua, amaítear í go dtí a chéad stad eile. Déanach ó 11
nóiméad ar na línte fada agus ó 6 ar na cinn ghearra (liosta V/Line féin),
an-déanach ó 30.

### WA Trains (Iarthar na hAstráile, An Astráil)

⚠ **Ní fhoilsítear aon suíomh beo.** Tarraingítear gach traein ó amchlár
údarás iompair phoiblí Iarthar na hAstráile: curtha feadh a líne de réir a
hamanna sceidealta, marcáilte mar mheastachán, gan moill. Seiceáiltear an
t-amchlár uair sa lá. Is iad na chéad trí litir den bhealach an lipéad: AUS
(Australind, corcra), PRO (Prospector, oráiste), MER (MerredinLink, glas) agus
AVO (AvonLink, glas), mar an gcéanna sa dá threo.

### VR (An Fhionlainn)

Ó Digitraffic de chuid Fintraffic, suíomh nua timpeall gach 30 soicind. Is é an
cineál traenach agus an uimhir an lipéad, mar a scríobhann VR é (`IC 23`).
Glas VR le fáinne dorcha ag fágáil Heilsincí, malartaithe ag dul ann. Níl treo
sna sonraí, mar sin leanann an tsaighead an líne. Déanach ó 6 nóiméad (áiríonn
VR traein déanach nuair atá sí níos mó ná cúig nóiméad déanach), an-déanach ó
12.

* **Traein Dhaidí na Nollag** (Santa Claus Express), ón gcéad Domhnach den
  Aidbhint go dtí 6 Eanáir: fear sneachta ag dul ó thuaidh, réinfhia ag teacht
  ar ais, gan uimhir. Ó 12 nóiméad déanach casann an fhíor thart gach cúpla
  soicind.
* **An teachín samhraidh**, ó Oíche Fhéile Eoin go dtí 31 Iúil: tarraingítear
  gach traein fhadachair VR mar theachín, lena huimhir lena taobh.

### Irish Rail (Éire)

Ó sheirbhís bheo Irish Rail (Iarnród Éireann) agus ó amchlár an Údaráis
Náisiúnta Iompair. ⚠ Ní thuairiscíonn Irish Rail traein ach nuair a théann sí
thar phointí comharthaíochta atá cúpla nóiméad óna chéile, mar sin tarraingítear
gach traein óna hamchlár agus óna moill is déanaí, bogtha feadh a bealaigh. Is é
uimhir na traenach gan a litir an lipéad (taispeántar A700 mar 700). Is seamróg
ghlas í traein InterCity le himlíne agus uimhir oráiste ag fágáil Bhaile Átha
Cliath, na dathanna malartaithe ag dul ann. Is diosca airgid í an Enterprise le
fáinne seachtrach dearg, banda maigeanta agus uimhir mhaigeanta; ag dul go
Baile Átha Cliath tá an diosca maigeanta. Déanach ó 10 nóiméad (riail an
Údaráis Náisiúnta Iompair), an-déanach ó 20.

### NS, Arriva agus Keolis (An Ísiltír)

Ó shonraí feithiclí NS, le d'eochair féin, suíomh nua timpeall gach 10 soicind.
Tuairiscíonn an fotha seo luas agus treo na traenach féin, agus cuirtear an dá
cheann ar aghaidh. Tagann an chéad stad eile agus an mhoill ó amchlár OVapi; is
é an rian léarscáil NS féin dá línte, íoslódáilte uair sa lá. Is é uimhir na
traenach an lipéad. Tá traenacha NS buí le fáinne gorm NS; tá cuma chárta na
léarscáile féin ar thraenacha Arriva agus Keolis faoi láthair. Déanach ó 3
nóiméad (sainmhíniú NS féin), an-déanach ó 10.

### Vy, Go-Ahead Norge agus SJ Nord (An Iorua)

Ó Entur, gach iarnród ina iontráil féin. Is é cód na líne an lipéad (F4, RE10,
R50). Dath na líne féin le fáinne bán ag fágáil Oslo S (ar thuras nach sroicheann
Oslo S, an chathair cinn scríbe is mó aige), malartaithe ag dul ann. Ní
fhoilsíonn Entur luas ná treo, mar sin gluaiseann traein ag an luas idir a dhá
shuíomh dheireanacha, agus leanann an tsaighead a líne. I dtolláin fhada Oslo,
bogtar traein a stopann a suíomhanna feadh a líne go dtí go dtagann siad ar ais.
⚠ **Ní fhoilsíonn SJ Nord aon suíomh:** cuirtear gach ceann dá thraenacha ar a
líne de réir a hamanna ionchais. Déanach ó 4 nóiméad, agus ó 6 ar na línte F
agus ar na línte go Göteborg (An tSualainn), riail Bane NOR agus Vy; an-déanach
ag a dhá oiread sin.

### Renfe (Spain) agus Renfe Regionals (Catalunya), An Spáinn

Léann **Renfe (Spain)** fotha fadachair Renfe, suíomh nua timpeall gach 15
soicind. Is é uimhir na traenach an lipéad; tá an tseirbhís (AVE, Avlo, Alvia
agus mar sin de) sa bhosca ainlithe. AVE dúghorm, Avlo turcaidghorm, gach
seirbhís eile corcra Renfe, gach ceann líonta ag fágáil Mhaidrid (ar thuras
nach sroicheann Maidrid, an chathair cinn scríbe is mó aige) agus malartaithe
ag dul ann. Ní fhoilsíonn Renfe línte bealaigh, mar sin tógadh na línte ó
OpenStreetMap agus seoltar iad leis an gcomhtháthú. Ní fhoilsíonn Renfe aon
riail do thraein dhéanach, mar sin bíonn traein déanach de réir fhad a turais:
ó 10 nóiméad suas go 400 km (250 míle), 15 suas go 560 km (350 míle), 20 suas
go 725 km (450 míle), 25 suas go 885 km (550 míle), 30 níos faide ná sin;
an-déanach ag a dhá oiread sin.

Tarraingíonn **Renfe Regionals (Catalunya)** línte réigiúnacha R11 go R17
Rodalies de Catalunya. Is é uimhir na traenach an lipéad, i ndath na líne
féin, líonta ag fágáil Barcelona agus malartaithe ag dul ann. Lasmuigh de
Barcelona is é suíomh traenach an stáisiún deireanach a ndeachaigh sí thairis,
mar sin amaítear an traein idir stáisiúin de réir an amchláir agus a moille.
Déanach ó 10 nóiméad, an-déanach ó 20, de réir fhad na líne is faide. Leis an
dá iarnród Renfe socraithe, tarraingítear gach traein uair amháin.

### Iarnróid na Sualainne (An tSualainn)

Ó Trafikverket, le d'eochair féin (eochair amháin don chúig cinn déag). Is é
uimhir na traenach ar an ticéad an lipéad; tá an branda, an uimhir agus na
stáisiúin cinn scríbe sa bhosca ainlithe. Tá a dhathanna féin ag gach branda,
malartaithe ag dul go Stockholm C (ar thuras nach sroicheann Stockholm C, an
chathair cinn scríbe is mó aige). Tugann Trafikverket luas ar thart ar leath
dá shuíomhanna; gluaiseann na traenacha eile ag an luas idir a dhá shuíomh
dheireanacha. Ní fhoilsíonn an tSualainn línte bealaigh, mar sin tógadh na
línte ó OpenStreetMap agus seoltar iad leis an gcomhtháthú. Déanach ó 6
nóiméad (áiríonn Trafikverket traein in am go dtí 5 nóiméad 59 soicind),
an-déanach ó 12.

### VIA Rail (Ceanada)

Ó shonraí stádais traenach VIA Rail féin. Is diosca gach traein leis an
duilleog mhailpe agus banda i ndath a grúpa bealaí (Atlantic, Western, Ontario
agus Quebec, Prince Rupert, Churchill, Sudbury go White River, bealaí radhairc
Montréal), le huimhir na traenach i gclib ina seasamh. Tá diosca buí ag
corruimhreacha, agus diosca i ndath an bhanda ag ré-uimhreacha. Gluaiseann
traein gan suíomh nua i dtreo a chéad stad eile chun teacht ann ag meastachán
VIA féin. Ní fhoilsíonn VIA aon riail do thraein dhéanach, mar sin bíonn traein
déanach ó 10 nóiméad ar an gconair ó Québec City go Windsor agus ó 60 in áiteanna
eile (luachanna Amtrak Status Maps do VIA), an-déanach ag a dhá oiread sin.

### Amtrak (Stáit Aontaithe Mheiriceá)

Ní fhoilsíonn Amtrak aon sonraí beo oscailte. Athsheolann Amtraker rianú
traenacha Amtrak féin, le suíomh nua gach 3 go 5 nóiméad, agus bogann an
comhtháthú gach traein feadh a líne ag an luas a thuairiscíonn Amtrak. Is réalta
gach traein lena huimhir trasna uirthi, i ndathanna a bealaigh (bealaí an
Oirthuaiscirt, Cascades, Pacific Surfliner, Acela agus tuilleadh), nó réalta na
brataí murach sin. Athraíonn an Maple Leaf (Nua-Eabhrac go Toronto) go mall idir
réalta Amtrak agus suaitheantas VIA. Taispeánann traein atá ina seasamh ag an
teorainn ag Lacolle, Rouses Point nó Niagara Falls "Customs" (custaim) in áit a
moille. Déanach ó 16 nóiméad (áiríonn Amtrak traein in am laistigh de 15
nóiméad), an-déanach ó 30. Is féidir leis an uimhir traenach chéanna rith ar dhá
nó trí lá ag an am céanna, mar sin is marcóir dá chuid féin gach turas.

### Brightline (Stáit Aontaithe Mheiriceá)

Ó fhotha Brightline féin, suíomh nua timpeall gach 60 soicind. Is é uimhir an
turais an lipéad, dubh le himlíne bhán, ar dhiosca i ndath cheann scríbe na
traenach, le fáinne dubh. Ní úsáidtear suíomh atá níos sine ná 5 nóiméad. Níl
luas san fhotha, mar sin gluaiseann traein ag an luas idir a dhá shuíomh
dheireanacha. Ní fhoilsíonn Brightline aon riail do thraein dhéanach, mar sin
bíonn traein déanach ó 10 nóiméad, an-déanach ó 20, de réir fhad a turais.

---

## Na haonáin go léir a chruthaíonn sé

Do gach iarnród:

| Aonán | Cad é |
|---|---|
| `sensor.<railroad>_trains_in_service` | **Trains in service** (traenacha i seirbhís): cé mhéad traein atá an t-iarnród ag rith ar an léarscáil anois. Do Amtrak: `sensor.amtrak_trains_in_service` |
| `geo_location.<railroad>_train_…` | ceann in aghaidh na traenach (`geo_location.amtrak_train_5_17`); tagann agus imíonn sé leis an traein. Tá `source: live_track_intercity_rail` ar gach ceann, agus is é a staid a fad ó do theach i gciliméadair |

Tagann aitheantas aonáin marcóra ón iarnród agus ón turas, riamh óna lipéad:
is é `geo_location.amtrak_train_5_17` traein 5 Amtrak a d'fhág ar an 17ú lá den
mhí, mar sin coinníonn traein an t-aitheantas aonáin céanna ar feadh a turais
ar fad, agus faigheann turas eile leis an uimhir chéanna a cheann féin.
Baintear an marcóir nuair a fhágann an turas sonraí an iarnróid nó nuair a
chríochnaíonn sé. Níl aitheantas uathúil (unique ID) ag na marcóirí, mar nach
bhfuil ag aon mharcóir léarscáile Live Track, mar sin ní féidir iad a
athainmniú, a fholú ná limistéar a thabhairt dóibh sa chomhéadan. Tá
aitheantas uathúil ag an mbraiteoir agus is féidir é a athainmniú.

Taifeadtar tréithe a athraíonn ag gach ceistiú, suíomhanna agus amanna na
marcóirí, i stair Home Assistant, mar atá d'aon aonán. Níl aon tréithe ag an
mbraiteoir, mar sin is beag a chosnaíonn sé é a choinneáil, agus is é an
taifead é ar cé mhéad traein a rith ar lá. Chun na marcóirí a choinneáil as an
stair, cuir é seo le `configuration.yaml`, ansin atosaigh:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_train_*
```

Má tá rannán `recorder:` i do `configuration.yaml` cheana, cuir an patrún
`geo_location.*_train_*` amháin leis, faoi `exclude:` agus `entity_globs:`.
Ní mheaitseálann an patrún ach marcóirí traenach an mhodúil seo. Ní bheidh aon
rian le tarraingt ansin ag cárta léarscáile atá socraithe chun stair a
tharraingt.

---

## Cad a sheolann sé agus a íoslódálann sé

**Faoi do shuíomh.** Faic. Ní úsáidtear suíomh do thí ach taobh istigh de do
Home Assistant, chun fad gach traenach a thabhairt. Ní sheoltar d'eochair, nuair
a theastaíonn ceann ó iarnród, ach chuig soláthraí an iarnróid sin. Ní sheoltar
aon rud eile fút áit ar bith. Feiceann gach seirbhís do sheoladh idirlín, mar a
fheiceann aon suíomh gréasáin.

**Cé mhéad.** Léitear gach foinse bheo ag gach ceistiú, ag eatramh an iarnróid
féin de réir réamhshocraithe (**Poll interval**, 15 go 600 soicind), nó níos
annaimhe nuair a deir an tábla é. Nuair a léann roinnt modúl Live Track nó
iarnród an fhoinse chéanna, léann cliant comhroinnte amháin í uair amháin dóibh
go léir. Tomhaiste ar 19 Samhain 2026, 02:44 go 02:49 UTC:

| Iarnród | Sonraí beo, léamh amháin | Amchlár agus línte |
|---|---|---|
| Journey Beyond (An Astráil) | faic: ní íoslódáiltear faic | faic: seoltar a amchlár agus a línte leis an gcomhtháthú |
| NSW TrainLink (An Astráil) | 124 KB ó dhá fhotha, uair gach 55 soicind ar a mhéad | 40 MB, nuair a athraítear é, seiceáilte go laethúil |
| Queensland Rail Travel (An Astráil) | an liosta, 5.5 KB, gach 5 nóiméad; amanna gach traenach atá ag rith, 6 go 8 KB, gach 5 nóiméad | faic: seoltar a línte leis an gcomhtháthú |
| V/Line (An Astráil) | 14 KB ó dhá fhotha | 58 MB (cuid V/Line de chomhad 311 MB Transport Victoria, léite leis féin), nuair a athraítear é, seiceáilte go laethúil |
| WA Trains (An Astráil) | faic: níl aon fhotha beo ann | 28 MB, nuair a athraítear é, seiceáilte go laethúil |
| VR (An Fhionlainn) | 1.4 KB comhbhrúite do na suíomhanna; traenacha an lae, 0.5 MB comhbhrúite an chéad uair, ansin na hathruithe amháin, uair sa nóiméad | 3.1 MB, gach lá |
| Irish Rail (Éire) | 0.2 KB, uair gach 55 soicind ar a mhéad | 6.6 MB, nuair a athraítear é, seiceáilte go laethúil; liosta na stáisiún, 46 KB, uair sa tseachtain |
| NS, Arriva, Keolis (An Ísiltír) | 1.5 KB, uair gach 9 soicind ar a mhéad; moilleanna ó OVapi, 5.3 MB, gach 5 nóiméad agus nuair a athraítear iad amháin | amchlár OVapi, 267 MB, uair sa tseachtain ar a mhéad agus nuair a athraítear é amháin; léarscáil rianta NS, 1.3 MB, gach lá |
| Vy, Go-Ahead Norge, SJ Nord (An Iorua) | Vy 510 KB ó dhá fhotha, Go-Ahead Norge 7 KB, SJ Nord 0.7 KB uair sa nóiméad | Vy 67 MB, Go-Ahead Norge 20 MB, SJ Nord 26 MB, nuair a athraítear iad, seiceáilte go laethúil |
| Renfe (Spain) | 2.1 KB ó dhá fhotha | 0.7 MB, gach lá; seoltar a línte leis an gcomhtháthú |
| Renfe Regionals (Catalunya) | 0.2 KB ó dhá fhotha a iompraíonn líonraí áitiúla Renfe go léir | 16 MB, gach lá |
| Iarnróid na Sualainne (An tSualainn) | 474 KB an chéad uair, ansin 5 go 9 KB d'athruithe | faic; liosta na stáisiún, 0.15 MB, gach lá; seoltar na línte leis an gcomhtháthú |
| VIA Rail (Ceanada) | 353 KB, seolta comhbhrúite mar 33 KB | 1.0 MB, uair sa tseachtain |
| Amtrak (Stáit Aontaithe Mheiriceá) | 1.2 MB, seolta comhbhrúite mar 113 KB | 18.6 MB, uair sa tseachtain |
| Brightline (Stáit Aontaithe Mheiriceá) | 1.3 KB ó dhá fhotha | 29 KB, uair sa tseachtain |

⚠ Nuair a tomhaiseadh é seo bhí sé ina lá san Astráil, ina tráthnóna i
Meiriceá Thuaidh agus ina oíche san Eoraip. Bíonn fotha beo ag a laghad san
oíche: i rith an lae bíonn fothaí na hEorpa níos mó ná mar a thaispeánann an
tábla.

**Tar éis earráide.** Leanann na traenacha ag gluaiseacht ar na sonraí maithe
deireanacha ar feadh suas le 10 nóiméad; ansin marcáiltear iad mar "níl fáil
orthu" go dtí go bhfreagraíonn an fhoinse. Déantar iarracht arís níos déanaí ar
amchlár nach n-éiríonn lena íoslódáil, agus fanann an chóip atá agat in úsáid.
Má leanann soláthraí ag diúltú d'eochair ar feadh deich nóiméad, iarrann Home
Assistant ceann nua.

**Ar an diosca.** Coinnítear amchláir agus línte bealaigh i bhfillteán
`.storage` Home Assistant faoi ainmneacha a thosaíonn le `saw_`, comhroinnte leis
na modúil Live Track eile a léann an t-iarnród céanna. Má bhaineann tú Live
Track Intercity Rail agus mura n-úsáideann aon mhodúl Live Track eile iad, is
féidir leat iad a scriosadh de láimh.

---

## Cuidigh leis fás

Tá Live Track Intercity Rail fós ag fás. Cuirimid iarnróid agus tíortha leis de
réir mar a aimsímid iad, agus ba mhaith linn a fháil amach cad ba mhaith leat
ina dhiaidh seo.

### Mol rud éigin

An bhfuil do thír nó d'iarnród in easnamh? An bhfuil rud éigin mícheart, nó
deacair a thuiscint? Inis dúinn cibé bealach is fusa duit:

* [**Líon isteach foirm ghearr**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=ga.yml)
  i nGaeilge. Teastaíonn cuntas GitHub saor in aisce uait.
* **Scríobh ríomhphost** chuig
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Níl cuntas de dhíth.

Cibé bealach, cabhraíonn sé má insíonn tú dúinn:

* cad ba mhaith leat a fheiceáil, agus cén áit ar domhan;
* nasc chuig an áit a bhfoilsítear na sonraí, má tá ceann ar eolas agat
  (leathanach sonraí oscailte, foinse phoiblí, suíomh gréasáin seirbhíse): níl
  sé riachtanach, ach cabhraíonn sé;
* teanga do Home Assistant, más é an fhoclaíocht nó aistriúchán an fhadhb.

Scríobh i mBéarla nó i do theanga féin, cibé acu is fusa duit.

### Cuir leis tú féin é, le cabhair uainn

Más mian leat rud éigin a chur leis tú féin, cabhróimid leat é a dhéanamh, ón
gcéad cheist go dtí an eisiúint chríochnaithe. Ní gá duit a bheith i do
fhorbróir chun tosú:

* **Aistriúchán.** Is liosta gearr frásaí i gcomhad téacs amháin iad focail na
  dialóige socraithe. Taispeánfaimid duit cén comhad agus cé na línte.
* **Iarnród nua.** Inis dúinn cá bhfoilsítear na sonraí. Is féidir linn an cód
  a scríobh le chéile, nó féachaint ar do chuid féin.
* **Tástáil san áit a bhfuil tú i do chónaí.** Suiteáil é, féach ar do chuid
  féin den léarscáil, agus inis dúinn cad atá ceart agus cad nach bhfuil.
* **Ceartúchán ar an README seo.** Mura raibh céim ag teacht leis an méid a
  chonaic tú, inis dúinn cad a chonaic tú.

[**Inis dúinn cad atá ar intinn agat**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=ga.yml)
nó scríobh chuig
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
agus freagróimid leis na chéad chéimeanna eile.

---

## Teangacha

An README seo: [English](README.md), [Deutsch](README.de.md), [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md), [Español](README.es.md),
[Italiano](README.it.md), [Dansk](README.da.md), [Suomi](README.fi.md), [Svenska](README.sv.md),
[Norsk bokmål](README.nb.md), **Gaeilge**. Tá gach README aistrithe iomlán.
Níor léigh cainteoir dúchais aon cheann acu fós. Más í an Ghaeilge do theanga
dhúchais, inis dúinn an léann an README seo go maith: féach
[Cuidigh leis fás](#cuidigh-leis-fás).

Tá an dialóg socraithe agus na roghanna i mBéarla amháin faoi láthair, cibé
teanga atá ar do Home Assistant. Má labhraíonn tú teanga eile, is féidir leat
iad a aistriú tú féin: liosta gearr frásaí in aon chomhad amháin atá ann, agus
[cuideoimid leat é a dhéanamh](#cuir-leis-tú-féin-é-le-cabhair-uainn).

Ar aimsigh tú botún in aistriúchán, nó an bhfuil teanga eile de dhíth ort?
Inis dúinn ag <https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues>,
nó [aistrigh é le cabhair uainn](#cuir-leis-tú-féin-é-le-cabhair-uainn).

---

## Creidiúintí agus ceadúnais

Léann do Home Assistant gach foinse bheo agus é ag rith; níl aon rud ó fhotha
beo sa stór seo. Luann gach traein a foinse ina tréith `attribution`. Ceanglaíonn
téarmaí gach foinse tú, mar an duine a fhaigheann a sonraí.

* **Amtraker** (amtraker.com), a athsheolann rianú traenacha Amtrak (Stáit
  Aontaithe Mheiriceá): sonraí faoin
  [Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/),
  sannadh riachtanach. Amchlár **Amtrak** féin do na línte bealaigh.
* **Brightline** (Stáit Aontaithe Mheiriceá): a fhothaí GTFS agus
  GTFS-Realtime; ní fhoilsíonn Brightline aon téarmaí.
* **VIA Rail** (Ceanada): a shonraí stádais traenach, nach bhfoilsíonn VIA aon
  téarmaí ina leith; a amchlár faoin Open Government Licence - Canada 2.0
  ([developer resources](https://www.viarail.ca/en/developer-resources)).
* **Fintraffic / digitraffic.fi** (An Fhionlainn): sonraí faoi CC BY 4.0.
* **Transport for NSW** (An Astráil): sonraí faoi CC BY 4.0
  ([ceadúnas sonraí](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (An Astráil): sonraí faoi CC BY 4.0
  ([sonraí oscailte](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Queensland Rail Travel** (An Astráil): na hamanna a thaispeánann a
  leathanach Service Updates, léite ag do Home Assistant; féach
  [leathanach cóipchirt Queensland Rail](https://www.queenslandrailtravel.com.au/copyright).
  Ní sheoltar aon rud de chuid Queensland Rail Travel leis an gcomhtháthú.
* **Journey Beyond** (An Astráil): a amchláir foilsithe, tras-scríofa in
  `data/journey_beyond_timetable.json`; ní fhoilsíonn Journey Beyond aon téarmaí
  ina leith.
* **Údarás iompair phoiblí Iarthar na hAstráile** (Public Transport Authority
  of Western Australia): sonraí amchláir ar fáil saor in aisce ó
  www.transperth.wa.gov.au
  ([spatial data access](https://www.transperth.wa.gov.au/About/Spatial-Data-Access);
  ní CC BY).
* **Renfe** (An Spáinn): sonraí faoi CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)).
* **Entur** (An Iorua): tá sonraí ann faoi cheadúnas na hIorua do shonraí
  oscailte rialtais ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)), dáilte ag
  Entur.
* **Trafikverket** (An tSualainn): sonraí faoi [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Éire): sonraí beo; ní fhoilsíonn Irish Rail aon téarmaí.
  Amchlár ón [Údarás Náisiúnta Iompair](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Éire), CC BY 4.0, mar atá.
* **NS** (An Ísiltír): sonraí feithiclí agus léarscáil rianta, le d'eochair
  féin, faoi théarmaí an [NS API portal](https://apiportal.ns.nl/). Amchlár agus
  moilleanna ó [OVapi](https://gtfs.ovapi.nl/), CC0.
* **Comhaid a sheoltar in `data/`**: línte bealaigh do Journey Beyond,
  Queensland Rail Travel, Renfe (Spain) agus an tSualainn, tógtha ó
  [OpenStreetMap](https://www.openstreetmap.org/copyright), © rannpháirtithe
  OpenStreetMap, faoin
  [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/);
  bardais stáisiúin chinn scríbe thurais Renfe (OpenStreetMap, ODbL 1.0) agus
  a ndaonra (airí Wikidata P1082, CC0, nó OpenStreetMap murach sin); daonra
  chathracha cinn scríbe na Sualainne ó Statistics Sweden (SCB) agus ó
  Trafikverket, iad araon CC0 1.0; daonra chathracha cinn scríbe na hIorua ó
  Statistics Norway, tábla 04859, CC BY 4.0.
* **Is é an cárta léarscáile** [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, cóip de [ha-map-card](https://github.com/nathan-gs/ha-map-card) le
  nathan-gs, MIT, seolta in `frontend/`. Tá a thíleanna léarscáile agus a
  gcreidiúintí ina README.

Ní dhearna aon cheann de na heagraíochtaí seo an comhtháthú seo ná níor
fhormhuinigh siad é.

**Cód**: MIT, in [LICENSE](LICENSE). Coinníonn na comhaid in `data/` ceadúnais
a bhfoinsí, liostaithe thuas.

**D'fhorbróirí:** is modúl amháin gach iarnród in
`custom_components/live_track_intercity_rail/operators/`, a léann cuibheoir
foinse in `sources/`; atógtar na línte bealaigh a sheoltar leis na scripteanna
in `tools/` (`journey_beyond.py`, `qrt_lines.py`, `renfe_spain_lines.py`,
`sweden_lines.py`). Ritheann na tástálacha le
`python -m unittest discover -s tests`.

---

## Eochairfhocail

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

**Aitheantas.** Aithníonn StrausbergAutomationWorks pobail dhúchasacha gach tíre
agus gach uisce ar an léarscáil seo, ar fud an domhain, agus tugann sé ómós dá
Seanóirí, san am a caitheadh agus inniu.
