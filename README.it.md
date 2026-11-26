# Live Track Intercity Rail

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · **Italiano** · [Dansk](README.da.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · [Gaeilge](README.ga.md) · [Tutte le lingue](#lingue)

**Treni intercity per Home Assistant, su un'unica mappa.** Live Track
Intercity Rail mette sulla tua mappa di Home Assistant ogni treno delle
ferrovie intercity e a lunga percorrenza che scegli: dove si trova, il suo
numero, se è in ritardo secondo la regola della ferrovia stessa, e la sua
prossima fermata. Ogni ferrovia si aggiunge da sola, dai propri dati
pubblicati.

> **Live Track Intercity Rail è un modulo di Live Track**, una famiglia di
> integrazioni di Home Assistant che disegnano tutto ciò che si muove, e il
> meteo che attraversa, su un'unica mappa condivisa: aerei, navi, treni e
> meteo. Installalo da solo, o accanto agli altri moduli
> ([elenco più sotto](#parte-di-live-track-gli-altri-moduli)).

> **In crescita, e aperto alle idee.** Live Track Intercity Rail copre oggi
> 33 ferrovie in 9 paesi di 3 continenti, e stiamo aggiungendo altre ferrovie
> e altri paesi. Manca la tua? [Suggeriscila](#aiutaci-a-farlo-crescere), o
> aggiungila tu: ti aiuteremo a farlo.

**Stato: 0.1.3, pubblicato.** Nel catalogo del Marketplace ([installalo più
sotto](#installazione-passo-dopo-passo)).

Opera originale di StrausbergAutomationWorks. Non affiliato a, né approvato
da, Amtrak, Amtraker, Brightline, VIA Rail, Fintraffic, VR, Transport for
NSW, NSW TrainLink, Transport Victoria, V/Line, Queensland Rail, Journey
Beyond, la Public Transport Authority of Western Australia, Transwa, Renfe,
Rodalies de Catalunya, Entur, Vy, Go-Ahead Norge, SJ Nord, Trafikverket, SJ,
VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen,
Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget,
Värmlandstrafik, Tågab, Inlandsbanan, Irish Rail, la National Transport
Authority (Irlanda), NS, Arriva, Keolis, OVapi, né alcun'altra ferrovia.

---

## Indice

1. [Tutto quello che fa](#tutto-quello-che-fa)
2. [Dove funziona](#dove-funziona)
3. [Parte di Live Track: gli altri moduli](#parte-di-live-track-gli-altri-moduli)
4. [Prima di iniziare](#prima-di-iniziare)
5. [Installazione, passo dopo passo](#installazione-passo-dopo-passo)
6. [Configurazione, passo dopo passo](#configurazione-passo-dopo-passo)
7. [Chiavi gratuite che attivano di più, passo dopo passo](#chiavi-gratuite-che-attivano-di-più-passo-dopo-passo)
8. [Mettere la mappa su una plancia](#mettere-la-mappa-su-una-plancia)
9. [Usarlo nelle automazioni](#usarlo-nelle-automazioni)
10. [Tutto sulla mappa, nel dettaglio](#tutto-sulla-mappa-nel-dettaglio)
11. [Tutte le entità che crea](#tutte-le-entità-che-crea)
12. [Cosa invia e scarica](#cosa-invia-e-scarica)
13. [Aiutaci a farlo crescere](#aiutaci-a-farlo-crescere)
14. [Lingue](#lingue)
15. [Riconoscimenti e licenze](#riconoscimenti-e-licenze)
16. [Parole chiave](#parole-chiave)

---

## Tutto quello che fa

### Sulla mappa, senza configurare nulla

Aggiungi una **ferrovia**: scegli un paese, poi una delle sue ferrovie
intercity. Tutto ciò che segue appare allora per quella ferrovia. Aggiungi di
nuovo l'integrazione per ogni altra ferrovia che vuoi.

| Cosa | Dove | Da |
|---|---|---|
| **Treni in servizio**: un indicatore per treno, con il suo numero di treno o la sua linea come etichetta, nei colori della ferrovia, girato nella direzione in cui viaggia | ogni ferrovia | i dati pubblicati da ogni ferrovia |
| **Ritardo**: un treno appare in ritardo o in forte ritardo secondo la regola della ferrovia stessa; dove una ferrovia non pubblica alcuna regola, secondo la distanza che il treno percorre | ogni ferrovia che comunica i ritardi | il feed di ogni ferrovia |
| **Prossima fermata e il suo orario**: la stazione in cui il treno ferma subito dopo, e quando vi è atteso | ogni ferrovia il cui feed o orario lo indica | il feed e l'orario di ogni ferrovia |
| **Treni che seguono i binari**: tra due rilevamenti un treno avanza lungo la propria linea alla sua ultima velocità, non in linea retta | ogni ferrovia di cui è nota la linea | l'orario di ogni ferrovia, o linee fornite con l'integrazione |
| **Treni dall'orario**: dove una ferrovia non pubblica posizioni, ogni treno è posto sulla sua linea secondo i suoi orari e segnato come stima | Journey Beyond, Queensland Rail Travel e WA Trains (Australia), SJ Nord (Norvegia); Irish Rail con il suo ultimo ritardo | l'orario o gli orari di ogni ferrovia |
| **Disegni per alcuni treni**: il Treno di Babbo Natale e una casetta estiva (Finlandia), gli animali dei treni di Journey Beyond, un disegno per ogni linea di Queensland Rail Travel | Finlandia, Australia | disegnati per questa integrazione |
| **Fermo al confine**: un treno fermo a un valico tra Stati Uniti e Canada mostra "Customs" al posto del suo ritardo | i treni di Amtrak da e per il Canada | le posizioni di Amtrak |
| **Un conteggio per ferrovia**: treni in servizio | ogni ferrovia | gli stessi dati |

### Attivato dalla tua chiave o dal tuo account gratuiti

| Chiave o account gratuiti | Cosa aggiunge |
|---|---|
| Chiave di **Transport for NSW Open Data** | i treni regionali di NSW TrainLink (Nuovo Galles del Sud, Australia) |
| Chiave di **Transport Victoria Open Data** | i treni a lunga percorrenza di V/Line (Victoria, Australia) |
| Chiave del **portale API di NS** | NS Intercity e i treni regionali di Arriva e Keolis (Paesi Bassi); una sola chiave vale per tutti e tre |
| Chiave di **Trafikverket** | le 15 ferrovie svedesi; una sola chiave vale per tutte e quindici |

Ognuna si ottiene in pochi minuti: [passo dopo passo più sotto](#chiavi-gratuite-che-attivano-di-più-passo-dopo-passo).
Le altre 13 ferrovie non hanno bisogno di chiave.

---

## Dove funziona

| Regione | Cosa ottieni | Da | Serve |
|---|---|---|---|
| **Australia**: tutto il paese | Journey Beyond: The Ghan, The Ghan Expedition, Indian Pacific, Great Southern, The Overland, solo dall'orario ([perché](#journey-beyond-australia)) | Journey Beyond | niente |
| **Australia**: Nuovo Galles del Sud | i treni regionali di NSW TrainLink (XPT e Xplorer), anche verso il Queensland, il Victoria e il Territorio della Capitale Australiana | Transport for NSW | una chiave gratuita |
| **Australia**: Queensland | Queensland Rail Travel: Spirit of Queensland, Spirit of the Outback, Tilt Train, Westlander, Inlander, Kuranda Scenic Railway, Gulflander, dai loro orari pubblicati ([perché](#queensland-rail-travel-australia)) | Queensland Rail Travel | niente |
| **Australia**: Victoria | i treni a lunga percorrenza di V/Line (le sue linee suburbane sono in Live Track Commuter Rail), anche verso il Nuovo Galles del Sud | Transport Victoria | una chiave gratuita |
| **Australia**: Australia Occidentale | WA Trains: l'Australind, il Prospector, il MerredinLink e l'AvonLink, solo dall'orario ([perché](#wa-trains-australia-occidentale-australia)) | Public Transport Authority of Western Australia | niente |
| **Europa**: Finlandia | i treni a lunga percorrenza di VR | Fintraffic Digitraffic | niente |
| **Europa**: Irlanda | i treni InterCity di Irish Rail, e l'Enterprise da Dublino a Belfast (Regno Unito) | Irish Rail, National Transport Authority | niente |
| **Europa**: Paesi Bassi | NS Intercity, e i treni regionali di Arriva (Arriva, RRReis, Blauwnet) e Keolis (Blauwnet, RRReis); gli Sprinter di NS sono in Live Track Commuter Rail | NS, OVapi | una chiave gratuita |
| **Europa**: Norvegia | le linee F, RE, RX e R di Vy (la F1 anche verso la Svezia), la F5 e la R50 di Go-Ahead Norge, la F6, la F7 e dalla R60 alla R75 di SJ Nord | Entur | niente |
| **Europa**: Spagna | i treni AVE, Avlo, Alvia, Avant, Euromed, Intercity, MD e Regional di Renfe, anche verso Francia e Portogallo; le linee regionali da R11 a R17 di Rodalies de Catalunya | Renfe | niente |
| **Europa**: Svezia | SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget, Värmlandstrafik, Tågab e Inlandsbanan, ciascuna come ferrovia a sé; Öresundståg anche fino in Danimarca | Trafikverket | una chiave gratuita |
| **Nord America**: Canada | VIA Rail, ogni percorso | VIA Rail | niente |
| **Nord America**: Stati Uniti | Amtrak, ogni percorso, anche verso il Canada | Amtraker | niente |
| **Nord America**: Stati Uniti | Brightline (Florida) | Brightline | niente |

Non è nell'elenco? [Diccelo](#aiutaci-a-farlo-crescere). Dove qualcuno
pubblica i dati apertamente, valuteremo di aggiungerlo.

⚠ **Un treno è buono quanto i dati della sua ferrovia.** Alcune ferrovie
comunicano un treno ogni pochi secondi, altre ogni pochi minuti, altre solo
quando passa i segnali, e altre non pubblicano alcuna posizione. I limiti di
ogni ferrovia sono in [Tutto sulla mappa, nel dettaglio](#tutto-sulla-mappa-nel-dettaglio).

⚠ **Non è l'informazione ufficiale della ferrovia.** Prima di viaggiare,
controlla l'app o il sito della ferrovia stessa.

---

## Parte di Live Track: gli altri moduli

Live Track è un insieme di integrazioni di Home Assistant, una per ogni tipo
di cosa che si muove, tutte disegnate sulla stessa scheda mappa. Ognuna
funziona da sola; insieme formano un'unica immagine dal vivo. Condividono la
scheda mappa e una libreria Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
quindi installarne un'altra non aggiunge richieste a una fonte che un'altra
legge già.

| Modulo | Cosa mette sulla mappa | Stato |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aerei sopra di te tramite ADS-B, con rotte e icone per tipo | pubblicato |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | navi e barche tramite AIS, vicino a te o ovunque | pubblicato |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | treni suburbani in Nord America, Europa e Australia | pubblicato |
| **Live Track Intercity Rail** | treni intercity e a lunga percorrenza in Nord America, Europa e Australia (questo modulo) | pubblicato |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | aerei e navi dell'immigrazione e delle forze dell'ordine federali, da elenchi pubblici | pubblicato |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | meteo, tempeste e rischi naturali | pubblicato |
| Live Track Stations | tabelloni delle partenze e avvisi "è ora di andare" per ogni stazione | previsto |
| Live Track Satellites | satelliti che passano sopra di te | previsto |
| Live Track Freight Trains | treni merci e di servizio dove le ferrovie li pubblicano | previsto |
| Live Track Transit | autobus urbani, tram, traghetti e metropolitane | previsto |
| Live Track Intercity Buses | autobus interurbani e regionali | previsto |
| Live Track Commuter Buses | autobus per pendolari | previsto |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la scheda mappa condivisa su cui disegna ogni modulo | pubblicata, installata con ogni modulo |

Tutto è gratuito e open source. Niente è riservato agli sponsor.

---

## Prima di iniziare

* **Home Assistant** 2026.11 o successivo.
* **Il Marketplace** (HACS) nel tuo Home Assistant, per installarlo e
  aggiornarlo nel modo facile. Senza, puoi copiare i file a mano.
* **Accesso a Internet** per Home Assistant: ogni treno viene dai dati
  pubblicati dalla sua ferrovia.
* Niente da pagare. 13 delle 33 ferrovie non hanno bisogno di un account; le
  altre 20 hanno bisogno di una tua chiave gratuita, e quattro chiavi le
  coprono tutte ([più sopra](#attivato-dalla-tua-chiave-o-dal-tuo-account-gratuiti)).
* Home Assistant installa da solo i pacchetti Python di cui ha bisogno
  (`saw-livetrack`, `gtfs-realtime-bindings` e `tzdata`) la prima volta che
  l'integrazione si carica.

---

## Installazione, passo dopo passo

### Dal Marketplace (consigliato)

1. In Home Assistant, apri **Impostazioni → Marketplace** (HACS).
2. Cerca **Live Track Intercity Rail** e aprilo.
3. Scegli **Scarica** (o **Installa**).
4. **Riavvia Home Assistant**: **Impostazioni → Sistema → Riparazioni** offre
   il riavvio, oppure usa **Impostazioni → Sistema → Riavvia**.

Se la ricerca non lo trova, aggiungilo tramite il suo link: scegli **Aggiungi
dal collegamento** (o il menu a tre puntini → **Repository personalizzate**),
inserisci `StrausbergAutomationWorks/LiveTrackIntercityRail`, scegli
**Integrazione** se viene chiesto il tipo, poi prosegui dal passo 3.

Il Marketplace ti offre poi ogni nuova versione come aggiornamento.

### A mano

1. Scarica il codice sorgente dell'[ultima versione](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/releases/latest).
2. Copia la sua cartella `custom_components/live_track_intercity_rail` nella
   cartella `custom_components` della cartella di configurazione del tuo Home
   Assistant (crea `custom_components` se non c'è).
3. Riavvia Home Assistant.

Per aggiornare a mano, sostituisci la cartella con quella della nuova versione
e riavvia.

---

## Configurazione, passo dopo passo

1. Apri **Impostazioni → Dispositivi e servizi**.
2. Scegli **Aggiungi integrazione** (in basso a destra) e cerca **Live Track
   Intercity Rail**.
3. **Region** (regione): scegli il paese della ferrovia. Sono elencati solo i
   paesi con almeno una ferrovia. Scegli **Invia**.
4. **Railroad** (ferrovia): scegli la ferrovia. Scegli **Invia**.
5. **API key** (chiave API): solo per NSW TrainLink, V/Line, le tre ferrovie
   olandesi e le quindici ferrovie svedesi. Incolla la tua chiave
   ([come ottenerne una](#chiavi-gratuite-che-attivano-di-più-passo-dopo-passo))
   e scegli **Invia**. Le altre ferrovie saltano questo passo.

È tutto. I treni compaiono entro un minuto o due. Dove le linee di una
ferrovia vengono dal suo orario, i treni iniziano a seguire le loro linee non
appena l'orario è stato scaricato, il che la prima volta può richiedere
qualche minuto. Per seguire un'altra ferrovia, aggiungi di nuovo
l'integrazione. La stessa ferrovia due volte viene rifiutata.

### Cambiare ciò che mostra: le opzioni

Apri **Impostazioni → Dispositivi e servizi → Live Track Intercity Rail →
Configura** (l'ingranaggio) sulla ferrovia che vuoi cambiare. C'è una sola
opzione:

| Opzione | Cosa fa | Predefinito |
|---|---|---|
| **Poll interval** (intervallo di interrogazione) | ogni quanto viene letta la fonte della ferrovia, da 15 a 600 secondi. Un intervallo più breve dell'aggiornamento della fonte stessa non mostra nulla di più | secondo la ferrovia: 15 secondi per Renfe (Spain) e le tre ferrovie olandesi; 60 secondi per Brightline, NSW TrainLink, Irish Rail e SJ Nord; 30 secondi per le altre |

---

## Chiavi gratuite che attivano di più, passo dopo passo

Venti ferrovie chiedono a ogni utente una chiave propria, da quattro
fornitori. Ognuna di queste chiavi è gratuita, e ogni persona che installa
Live Track Intercity Rail ottiene la propria. Incolli la chiave quando la
finestra di configurazione la chiede ([passo 5 più sopra](#configurazione-passo-dopo-passo)).
Viene chiesta solo la chiave: nessuna password e nessun segreto. La chiave è
conservata in Home Assistant con l'integrazione, inviata solo al proprio
fornitore e mai scritta nel registro. Se il fornitore la rifiuta per dieci
minuti, Home Assistant te ne chiede una nuova.

### Transport for NSW (NSW TrainLink, Nuovo Galles del Sud, Australia)

1. Apri <https://opendata.transport.nsw.gov.au/>, scegli **Register**, crea
   un account e accedi.
2. Scegli l'icona del tuo profilo, poi **API Tokens**.
3. Scrivi un nome per la chiave e scegli **CREATE API TOKEN**. Copia subito la
   chiave: il sito la mostra una sola volta.
4. Incollala in **API key** quando aggiungi NSW TrainLink. Incolla solo la
   chiave: Live Track Intercity Rail aggiunge da sé la parola `apikey`.

### Transport Victoria (V/Line, Victoria, Australia)

1. Apri <https://opendata.transport.vic.gov.au/>, scegli **Login**, poi
   **Sign up**.
2. Inserisci i tuoi dati e scegli **Create Account**. Inserisci il codice
   dell'email che ricevi e scegli **Confirm**.
3. Il portale chiede un'app di autenticazione sul tuo telefono: inquadra con
   essa il codice QR, inserisci il codice dell'app e scegli **Confirm**. Poi
   accedi con la tua email, la tua password e il codice dell'app.
4. Scegli **My Account** → **Profile** → **API tokens**. La tua chiave è già
   lì. Incollala in **API key** quando aggiungi V/Line.

### NS (NS, Arriva e Keolis, Paesi Bassi)

1. Apri <https://apiportal.ns.nl/>, scegli **Inloggen** (accedi), poi
   **Externe bezoeker** (visitatore esterno).
2. Compila il modulo e invialo. Un'email conferma la registrazione. Le API
   possono impiegare fino a 5 minuti per comparire nel portale.
3. Apri la pagina della **Virtual Train API** (le posizioni dei treni di NS).
   Sotto **Related Products**, apri il suo prodotto, dai un nome al tuo
   abbonamento e scegli **Subscribe**.
4. Quando NS ha approvato l'abbonamento, la tua chiave è nella pagina del tuo
   profilo. Incollala in **API key** quando aggiungi NS, Arriva o Keolis. Una
   sola chiave vale per tutti e tre.

### Trafikverket (le 15 ferrovie svedesi)

1. Apri <https://data.trafikverket.se/oauth2/Account/register>.
2. Compila **Email**, **Displayname** (nome visualizzato), **Password** e
   **Confirm password**, spunta **Accept license and Agreement** e scegli
   **Register**.
3. Apri <https://data.trafikverket.se/get-started> e scegli **Create key**,
   sotto **Create a key**. Accedi con l'account che hai creato e crea la
   chiave.
4. Incollala in **API key** quando aggiungi una ferrovia svedese. Una sola
   chiave vale per tutte e quindici.

---

## Mettere la mappa su una plancia

La mappa è [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la scheda su cui disegna ogni modulo di Live Track. **Si installa con Live
Track Intercity Rail**: niente da scaricare, niente da copiare, nessuna
risorsa da aggiungere.

1. Apri una plancia, scegli la matita (**Modifica la plancia**), poi
   **Aggiungi scheda**.
2. Scorri fino in fondo e scegli **Manuale**.
3. Incolla questo e scegli **Salva**:

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

Gli altri moduli di Live Track vanno in `entity_filter` allo stesso modo: una
regola `- domain: geo_location` in più per ogni fonte.

**Sulla mappa:**

* Ogni treno è un indicatore nei colori della sua ferrovia, con il suo numero
  di treno o la sua linea come etichetta. I treni di Amtrak sono stelle,
  quelli di VIA Rail portano la foglia d'acero, gli InterCity di Irish Rail
  sono trifogli, e alcuni treni sono disegni (ogni ferrovia più sotto dice
  quali).
* Sulla maggior parte delle ferrovie i colori si scambiano con la direzione:
  in un modo uscendo dalla città principale, nell'altro andando verso di essa.
* Una freccia mostra la direzione in cui viaggia il treno. Un treno fermo
  mantiene la sua ultima direzione. I disegni restano dritti e non hanno
  freccia.
* **Punta** un treno per vedere la sua ferrovia, il numero, la linea e il
  percorso. **Fai clic** su di esso per tutti i suoi dettagli, compresi la
  prossima fermata e il ritardo.

Se le risorse delle tue plance sono definite in YAML
(`lovelace: resource_mode: yaml`), non si può registrare nulla per te: una
segnalazione in **Riparazioni** ti dà allora le righe esatte da aggiungere a
`configuration.yaml`. Sono così, con l'indirizzo proprio dell'integrazione al
posto dei segnaposto:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_intercity_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Ogni modulo di Live Track porta una copia della scheda e la registra quando
Home Assistant si avvia. Insieme mantengono esattamente una riga in
**Impostazioni → Plance → Risorse**: la versione più recente della scheda che
uno di loro porta, mai una più vecchia. Una scheda che hai installato tu dal
Marketplace viene lasciata stare. Quando rimuovi l'ultima ferrovia di questo
modulo, la riga passa a un altro modulo di Live Track, o viene rimossa se non
ne resta nessuno. Se i file dell'integrazione vengono rimossi mentre le sue
ferrovie sono ancora configurate, e non è installato nessun altro modulo di
Live Track, rimuovi tu la riga in **Impostazioni → Plance → Risorse**.

**Per installare invece la scheda a mano**, segui i passi del
[README della scheda](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
Una riga che hai creato tu, per una copia sotto `/local/` o a qualsiasi altro
indirizzo, non viene mai modificata né rimossa. Finché carica la scheda, ogni
modulo Live Track le lascia la scheda, anche quando un modulo porta una versione
più recente, e nulla in **Riparazioni** lo segnala. Per tornare alla copia del
modulo, rimuovi la tua riga in **Impostazioni → Plance → Risorse** e riavvia
Home Assistant. Se elimini il file della tua copia, rimuovi anche la sua riga:
finché resta una riga il cui file non c'è più, il modulo non aggiunge una riga
propria.

Qualsiasi altra scheda mappa che mostra entità `geo_location` mostra anche i
treni, come indicatori semplici.

---

## Usarlo nelle automazioni

Tutto è una normale entità di Home Assistant, quindi l'editor delle
automazioni ci lavora, senza codice.

**Una notifica sul telefono quando i dati della tua ferrovia si fermano** (i
treni allora lasciano la mappa):

1. **Impostazioni → Automazioni e scenari → Crea automazione → Crea una
   nuova automazione**.
2. **Quando**: **Aggiungi attivazione** → **Entità** → **Stato modificato**.
   Scegli l'entità **Trains in service** (treni in servizio) della ferrovia,
   e sotto **A (facoltativo)** scegli **Non disponibile**.
3. **Allora**: **Aggiungi azione**, cerca l'azione di notifica del tuo
   telefono (porta il nome del tuo telefono) e scrivi un messaggio, per
   esempio:

   ```text
   Nessun treno intercity sulla mappa: i dati della ferrovia si sono fermati
   ```

4. **Salva**.

**Altre idee:** una luce che si accende quando un treno di Amtrak è entro 2 km
(1,2 miglia) da casa tua negli Stati Uniti, dalla distanza degli indicatori;
un conteggio sulla plancia dei treni che VR fa circolare in Finlandia nel
corso della giornata; un messaggio quando parte il primo treno del giorno di
Queensland Rail Travel (Australia), da **Trains in service** che supera 0.

---

## Tutto sulla mappa, nel dettaglio

### Treni

Ogni treno è un indicatore. Il suo stato è la sua distanza da casa tua, in
chilometri. L'indicatore compare quando la ferrovia comunica il treno, o
quando il suo orario dice che è in viaggio, e viene rimosso quando il treno
esce dai dati della ferrovia o la sua corsa è finita.

* **Tra due rilevamenti** un treno avanza lungo la propria linea verso la
  prossima fermata: alla velocità che la ferrovia comunica o, dove non ne
  comunica, alla velocità tra i suoi ultimi due rilevamenti. Non supera mai
  la prossima fermata, e smette di muoversi 30 minuti dopo l'ultimo
  rilevamento. Un treno su una linea nota è disegnato sulla linea; il
  rilevamento della ferrovia stessa è conservato accanto.
* **Se i dati di una ferrovia vengono a mancare**, i suoi treni continuano a
  muoversi sul loro ultimo rilevamento valido per un massimo di 10 minuti.
  Dopo sono non disponibili e lasciano la mappa finché i dati non tornano.
* **In ritardo e in forte ritardo**: dove la ferrovia pubblica la propria
  regola per un treno in ritardo, l'integrazione la usa. Dove non ne pubblica
  alcuna, un treno è in ritardo secondo la distanza che percorre, con le
  soglie di Amtrak Status Maps (asm.transitdocs.com). Ogni ferrovia più sotto
  dice quale.

Su ogni treno: `marker_label`, `train`, `line_name`, `observed_at` (quando il
suo rilevamento era vero), `course_deg` (mentre si muove), `next_stop` e
`arrival_estimated_at` (dove noti), `delay_min`, `late_threshold_min` e
`very_late_threshold_min`, `speed_kmh` (dove la ferrovia la comunica),
`attribution` e, tra due rilevamenti, `previous_latitude`,
`previous_longitude`, `previous_observed_at` e `segment_duration_s`. Un treno
spostato lungo la sua linea porta `position_source: estimated`, con il
rilevamento della ferrovia in `fix_latitude` e `fix_longitude`.

### Journey Beyond (Australia)

⚠ **Journey Beyond non pubblica posizioni.** Ogni treno è disegnato dal suo
orario pubblicato, trascritto in un file fornito con l'integrazione (partenze
fino al 29 dicembre 2027), quindi non si scarica nulla. Ogni treno è posto
sulla sua linea secondo i suoi orari, segnato come stima, senza ritardo: un
treno in ritardo o soppresso è comunque disegnato in orario. Ogni servizio è
il proprio disegno (il cammello con il cavaliere, un uccello, un canguro, un
emù), nei suoi colori all'andata e scambiati al ritorno, senza etichetta:
puntalo per vedere il treno e la sua corsa.

### NSW TrainLink (Nuovo Galles del Sud, Australia)

Dal feed NSW TrainLink di Transport for NSW, con la tua chiave, una nuova
posizione circa una volta al minuto. L'etichetta è il numero del treno.
Arancione NSW con un anello bianco uscendo da Sydney, scambiati andando verso
di essa. Il feed non ha velocità, quindi un treno avanza lungo la sua linea
alla velocità tra le sue ultime due posizioni. In ritardo da 11 minuti (NSW
TrainLink considera puntuale un treno entro 10 minuti), in forte ritardo da
30.

### Queensland Rail Travel (Australia)

⚠ **Queensland Rail Travel non pubblica posizioni.** Il tuo Home Assistant
legge gli orari che mostra la pagina Service Updates di Queensland Rail
Travel: l'elenco dei treni di oggi al massimo ogni 5 minuti, e gli orari di
ogni treno al massimo ogni 5 minuti da 30 minuti prima della sua partenza
fino a 15 minuti dopo il suo arrivo. Ogni treno è posto sulla sua linea
secondo quegli orari e segnato come stima. Ogni linea è il proprio disegno,
nei suoi colori uscendo da Brisbane e scambiati andando verso di essa, con il
numero del treno in un'etichetta accanto. Ritardo e forte ritardo non sono
mostrati.

### V/Line (Victoria, Australia)

Dal feed V/Line di Transport Victoria, con la tua chiave: le linee a lunga
percorrenza verso Albury, Ararat, Bairnsdale, Echuca, Maryborough,
Shepparton, Swan Hill e Warrnambool. L'etichetta è il numero del treno. Viola
V/Line con un anello giallo uscendo da Melbourne, scambiati andando verso di
essa. Il feed non ha velocità, quindi un treno avanza alla velocità tra le sue
ultime due posizioni; dopo 10 minuti senza nuova posizione viene cronometrato
fino alla prossima fermata. In ritardo da 11 minuti sulle linee lunghe e da 6
su quelle corte (l'elenco di V/Line stessa), in forte ritardo da 30.

### WA Trains (Australia Occidentale, Australia)

⚠ **Non sono pubblicate posizioni in tempo reale.** Ogni treno è disegnato
dall'orario della Public Transport Authority of Western Australia: posto
lungo la sua linea secondo gli orari previsti, segnato come stima, senza
ritardo. L'orario viene controllato una volta al giorno. L'etichetta sono le
prime tre lettere del percorso: AUS (Australind, viola), PRO (Prospector,
arancione), MER (MerredinLink, verde) e AVO (AvonLink, verde), uguali in
entrambe le direzioni.

### VR (Finlandia)

Da Digitraffic di Fintraffic, una nuova posizione circa ogni 30 secondi.
L'etichetta è il tipo e il numero del treno, come li scrive VR (`IC 23`).
Verde VR con un anello scuro uscendo da Helsinki, scambiati andando verso di
essa. I dati non hanno direzione, quindi la freccia segue la linea. In
ritardo da 6 minuti (VR considera in ritardo un treno che ha più di cinque
minuti di ritardo), in forte ritardo da 12.

* **Il Treno di Babbo Natale**, dalla prima domenica di Avvento al 6 gennaio:
  un pupazzo di neve verso nord, una renna al ritorno, senza numero. Da 12
  minuti di ritardo la figura si gira ogni pochi secondi.
* **La casetta estiva**, dalla vigilia di mezza estate al 31 luglio: ogni
  treno a lunga percorrenza di VR è disegnato come una casetta, con il suo
  numero accanto.

### Irish Rail (Irlanda)

Dal servizio in tempo reale di Irish Rail e dall'orario della National
Transport Authority. ⚠ Irish Rail comunica un treno solo quando passa punti di
segnalamento distanti pochi minuti, quindi ogni treno è disegnato dal suo
orario e dal suo ultimo ritardo, spostato lungo il suo percorso. L'etichetta è
il numero del treno senza la sua lettera (A700 mostra 700). Un treno
InterCity è un trifoglio verde con contorno e numero arancioni uscendo da
Dublino, con i colori scambiati andando verso di essa. L'Enterprise è un disco
argentato con un anello esterno rosso, una fascia magenta e un numero
magenta; verso Dublino il disco è magenta. In ritardo da 10 minuti (la regola
della National Transport Authority), in forte ritardo da 20.

### NS, Arriva e Keolis (Paesi Bassi)

Dai dati dei veicoli di NS, con la tua chiave, una nuova posizione circa ogni
10 secondi. Questo feed comunica la velocità e la direzione proprie di un
treno, ed entrambe vengono trasmesse. La prossima fermata e il ritardo vengono
dall'orario di OVapi; il binario è la mappa delle linee di NS stessa,
scaricata una volta al giorno. L'etichetta è il numero del treno. I treni di
NS sono gialli con un anello blu NS; i treni di Arriva e Keolis hanno per ora
l'aspetto proprio della scheda mappa. In ritardo da 3 minuti (la definizione
di NS stessa), in forte ritardo da 10.

### Vy, Go-Ahead Norge e SJ Nord (Norvegia)

Da Entur, ogni ferrovia con la propria voce. L'etichetta è il codice della
linea (F4, RE10, R50). Il colore proprio della linea con un anello bianco
uscendo da Oslo S (in un viaggio che non arriva a Oslo S, la sua città
capolinea più grande), scambiati andando verso di essa. Entur non pubblica
velocità né direzione, quindi un treno avanza alla velocità tra le sue ultime
due posizioni, e la freccia segue la sua linea. Nelle lunghe gallerie di Oslo
un treno le cui posizioni si interrompono viene spostato lungo la sua linea
finché non ritornano. ⚠ **SJ Nord non pubblica posizioni:** ognuno dei suoi
treni è posto sulla sua linea secondo gli orari previsti. In ritardo da 4
minuti, e da 6 sulle linee F e sulle linee per Göteborg (Svezia), la regola di
Bane NOR e Vy; in forte ritardo al doppio.

### Renfe (Spain) e Renfe Regionals (Catalunya, Spagna)

**Renfe (Spain)** legge il feed a lunga percorrenza di Renfe, una nuova
posizione circa ogni 15 secondi. L'etichetta è il numero del treno; il
servizio (AVE, Avlo, Alvia e così via) è nel riquadro al passaggio del
puntatore. AVE blu navy, Avlo turchese, ogni altro servizio viola Renfe,
ciascuno pieno uscendo da Madrid (in un viaggio che non arriva a Madrid, la
sua città capolinea più grande) e scambiato andando verso di essa. Renfe non
pubblica i tracciati dei percorsi, quindi le linee sono costruite da
OpenStreetMap e fornite con l'integrazione. Renfe non pubblica alcuna regola
per un treno in ritardo, quindi un treno è in ritardo secondo la lunghezza
del suo viaggio: da 10 minuti fino a 400 km (250 miglia), 15 fino a 560 km
(350 miglia), 20 fino a 725 km (450 miglia), 25 fino a 885 km (550 miglia),
30 oltre; in forte ritardo al doppio.

**Renfe Regionals (Catalunya)** disegna le linee regionali da R11 a R17 di
Rodalies de Catalunya. L'etichetta è il numero del treno, nel colore proprio
della linea, pieno uscendo da Barcellona e scambiato andando verso di essa.
Fuori da Barcellona una posizione è l'ultima stazione che un treno ha passato,
quindi il treno è cronometrato tra le stazioni con l'orario e il suo ritardo.
In ritardo da 10 minuti, in forte ritardo da 20, secondo la lunghezza della
linea più lunga. Con entrambe le ferrovie di Renfe configurate, ogni treno è
disegnato una sola volta.

### Le ferrovie svedesi (Svezia)

Da Trafikverket, con la tua chiave (una chiave per tutte e quindici).
L'etichetta è il numero del treno sul biglietto; il marchio, il numero e le
stazioni capolinea sono nel riquadro al passaggio del puntatore. Ogni marchio
ha i propri colori, scambiati andando verso Stockholm C (in un viaggio che non
arriva a Stockholm C, la sua città capolinea più grande). Trafikverket dà una
velocità su circa metà delle sue posizioni; gli altri treni avanzano alla
velocità tra le loro ultime due posizioni. La Svezia non pubblica i tracciati
dei percorsi, quindi le linee sono costruite da OpenStreetMap e fornite con
l'integrazione. In ritardo da 6 minuti (Trafikverket considera puntuale un
treno fino a 5 minuti e 59 secondi), in forte ritardo da 12.

### VIA Rail (Canada)

Dai dati sullo stato dei treni di VIA Rail stessa. Ogni treno è un disco con
la foglia d'acero e una fascia nel colore del suo gruppo di percorsi
(Atlantic, Western, Ontario e Quebec, Prince Rupert, Churchill, Sudbury a
White River, Montréal scenic), con il numero del treno in un'etichetta dritta.
I numeri dispari hanno un disco giallo, i pari un disco del colore della
fascia. Un treno senza nuova posizione avanza verso la prossima fermata per
arrivare alla stima di VIA stessa. VIA non pubblica alcuna regola per un treno
in ritardo, quindi un treno è in ritardo da 10 minuti sul corridoio da Québec
City a Windsor e da 60 altrove (i valori di Amtrak Status Maps per VIA), in
forte ritardo al doppio.

### Amtrak (Stati Uniti)

Amtrak non pubblica dati aperti in tempo reale. Amtraker ritrasmette il
tracciamento dei treni di Amtrak stessa, con una nuova posizione ogni 3-5
minuti, e l'integrazione sposta ogni treno lungo la sua linea alla velocità
che Amtrak comunica. Ogni treno è una stella con il suo numero sopra, nei
colori del suo percorso (le linee del Nord-Est, Cascades, Pacific Surfliner,
Acela e altre), altrimenti la stella della bandiera. Il Maple Leaf (da New
York a Toronto) passa lentamente dalla stella di Amtrak al distintivo di VIA.
Un treno fermo al confine a Lacolle, Rouses Point o Niagara Falls mostra
"Customs" al posto del suo ritardo. In ritardo da 16 minuti (Amtrak considera
puntuale un treno entro 15 minuti), in forte ritardo da 30. Lo stesso numero
di treno può viaggiare in due o tre giorni contemporaneamente, quindi ogni
corsa è il proprio indicatore.

### Brightline (Stati Uniti)

Dal feed di Brightline stessa, una nuova posizione circa ogni 60 secondi.
L'etichetta è il numero della corsa, in nero con contorno bianco, su un disco
nel colore della destinazione del treno, con un anello nero. Una posizione più
vecchia di 5 minuti non viene usata. Il feed non ha velocità, quindi un treno
avanza alla velocità tra le sue ultime due posizioni. Brightline non pubblica
alcuna regola per un treno in ritardo, quindi un treno è in ritardo da 10
minuti, in forte ritardo da 20, secondo la lunghezza del suo viaggio.

---

## Tutte le entità che crea

Per ogni ferrovia:

| Entità | Cos'è |
|---|---|
| `sensor.<ferrovia>_trains_in_service` | **Trains in service** (treni in servizio): quanti treni la ferrovia fa circolare ora sulla mappa. Per Amtrak: `sensor.amtrak_trains_in_service` |
| `geo_location.<ferrovia>_train_…` | uno per treno (`geo_location.amtrak_train_5_17`); compare e scompare con il treno. Ognuno porta `source: live_track_intercity_rail`, e il suo stato è la sua distanza da casa tua in chilometri |

L'ID entità di un indicatore viene dalla ferrovia e dalla corsa, mai dalla
sua etichetta: `geo_location.amtrak_train_5_17` è il treno 5 di Amtrak
partito il giorno 17 del mese, quindi un treno mantiene lo stesso ID entità
per tutta la corsa, e un'altra corsa con lo stesso numero riceve il proprio.
L'indicatore viene rimosso quando la corsa esce dai dati della ferrovia o
finisce. Gli indicatori non hanno ID univoco, come nessun indicatore di mappa
di Live Track, quindi non possono essere rinominati, nascosti o assegnati a
un'area nell'interfaccia. Il sensore ha un ID univoco e può essere rinominato.

Gli attributi che cambiano a ogni interrogazione, le posizioni e gli orari
degli indicatori, sono registrati nella cronologia di Home Assistant, come per
ogni entità. Il sensore non ha attributi, quindi conservarlo costa poco, ed è
la registrazione di quanti treni hanno circolato in un giorno. Per tenere gli
indicatori fuori dalla cronologia, aggiungi questo a `configuration.yaml` e
riavvia:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_train_*
```

Se il tuo `configuration.yaml` ha già una sezione `recorder:`, aggiungi solo
lo schema `geo_location.*_train_*`, sotto `exclude:` e `entity_globs:`. Lo
schema corrisponde solo agli indicatori dei treni di questo modulo. Una scheda
mappa impostata per disegnare la cronologia non ha allora più traccia da
disegnare.

---

## Cosa invia e scarica

**Sulla tua posizione.** Niente. La posizione di casa tua è usata solo
all'interno del tuo Home Assistant, per dare la distanza di ogni treno. La tua
chiave, dove una ferrovia ne ha bisogno, è inviata solo al fornitore di quella
ferrovia. Nient'altro su di te viene inviato da nessuna parte. Ogni servizio
vede il tuo indirizzo Internet, come qualsiasi sito web.

**Quanto.** Ogni fonte in tempo reale è letta a ogni interrogazione, per
impostazione predefinita all'intervallo proprio della ferrovia (**Poll
interval**, da 15 a 600 secondi), o meno spesso dove la tabella lo dice. Dove
più moduli di Live Track o più ferrovie leggono la stessa fonte, un unico
client condiviso la legge una volta per tutti. Misurato il 19 novembre 2026,
dalle 02:44 alle 02:49 UTC:

| Ferrovia | Dati in tempo reale, una lettura | Orario e linee |
|---|---|---|
| Journey Beyond (Australia) | niente: non si scarica nulla | niente: orario e linee sono forniti con l'integrazione |
| NSW TrainLink (Australia) | 124 KB da due feed, al massimo una volta ogni 55 secondi | 40 MB, quando cambia, controllato ogni giorno |
| Queensland Rail Travel (Australia) | l'elenco, 5,5 KB, ogni 5 minuti; gli orari di ogni treno in viaggio, da 6 a 8 KB, ogni 5 minuti | niente: le linee sono fornite con l'integrazione |
| V/Line (Australia) | 14 KB da due feed | 58 MB (la parte di V/Line del file da 311 MB di Transport Victoria, letta da sola), quando cambia, controllato ogni giorno |
| WA Trains (Australia) | niente: non esiste un feed in tempo reale | 28 MB, quando cambia, controllato ogni giorno |
| VR (Finlandia) | 1,4 KB compressi per le posizioni; i treni del giorno, 0,5 MB compressi la prima volta, poi solo le modifiche, una volta al minuto | 3,1 MB, ogni giorno |
| Irish Rail (Irlanda) | 0,2 KB, al massimo una volta ogni 55 secondi | 6,6 MB, quando cambia, controllato ogni giorno; l'elenco delle stazioni, 46 KB, una volta alla settimana |
| NS, Arriva, Keolis (Paesi Bassi) | 1,5 KB, al massimo una volta ogni 9 secondi; ritardi da OVapi, 5,3 MB, ogni 5 minuti e solo quando cambiano | l'orario di OVapi, 267 MB, al massimo una volta alla settimana e solo quando cambia; la mappa dei binari di NS, 1,3 MB, ogni giorno |
| Vy, Go-Ahead Norge, SJ Nord (Norvegia) | Vy 510 KB da due feed, Go-Ahead Norge 7 KB, SJ Nord 0,7 KB una volta al minuto | Vy 67 MB, Go-Ahead Norge 20 MB, SJ Nord 26 MB, quando cambiano, controllati ogni giorno |
| Renfe (Spain) | 2,1 KB da due feed | 0,7 MB, ogni giorno; le linee sono fornite con l'integrazione |
| Renfe Regionals (Catalunya, Spagna) | 0,2 KB da due feed che portano tutte le reti locali di Renfe | 16 MB, ogni giorno |
| Le ferrovie svedesi (Svezia) | 474 KB la prima volta, poi da 5 a 9 KB di modifiche | niente; l'elenco delle stazioni, 0,15 MB, ogni giorno; le linee sono fornite con l'integrazione |
| VIA Rail (Canada) | 353 KB, inviati compressi come 33 KB | 1,0 MB, una volta alla settimana |
| Amtrak (Stati Uniti) | 1,2 MB, inviati compressi come 113 KB | 18,6 MB, una volta alla settimana |
| Brightline (Stati Uniti) | 1,3 KB da due feed | 29 KB, una volta alla settimana |

⚠ Quando è stato misurato era giorno in Australia, sera in Nord America e
notte in Europa. Un feed in tempo reale è più piccolo di notte: di giorno i
feed europei sono più grandi di quanto mostri la tabella.

**Dopo un errore.** I treni continuano a muoversi sugli ultimi dati validi per
un massimo di 10 minuti; poi sono segnati come non disponibili finché la fonte
non risponde. Un orario che non si riesce a scaricare viene riprovato più
tardi, e la copia che hai resta in uso. Se un fornitore continua a rifiutare
la tua chiave per dieci minuti, Home Assistant te ne chiede una nuova.

**Su disco.** Orari e tracciati dei percorsi sono conservati nella cartella
`.storage` di Home Assistant con nomi che iniziano per `saw_`, condivisi con
gli altri moduli di Live Track che leggono la stessa ferrovia. Se rimuovi Live
Track Intercity Rail e nessun altro modulo di Live Track li usa, puoi
eliminarli a mano.

---

## Aiutaci a farlo crescere

Live Track Intercity Rail sta ancora crescendo. Aggiungiamo ferrovie e paesi
man mano che li troviamo, e vogliamo sapere cosa ti piacerebbe in seguito.

### Suggerire qualcosa

Manca il tuo paese o la tua ferrovia? Qualcosa è sbagliato, o difficile da
capire? Diccelo nel modo più facile per te:

* [**Compila un breve modulo**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=it.yml)
  in italiano. Ti serve un account GitHub gratuito.
* **Scrivi un'email** a
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Non serve un account.

In entrambi i casi, ci aiuta se ci dici:

* cosa ti piacerebbe vedere, e in quale parte del mondo;
* un link a dove sono pubblicati i dati, se ne conosci uno (una pagina di
  dati aperti, un feed pubblico, il sito di un servizio): non è necessario,
  ma aiuta;
* la lingua del tuo Home Assistant, se il problema è la formulazione o una
  traduzione.

Scrivi in inglese o nella tua lingua, come ti è più facile.

### Aggiungerlo tu, con il nostro aiuto

Se vuoi aggiungere qualcosa tu, ti aiuteremo a farlo, dalla prima domanda
alla versione finita. Non serve essere sviluppatori per iniziare:

* **Una traduzione.** I testi della finestra di configurazione sono un breve
  elenco di frasi in un solo file di testo. Ti mostreremo quale file e quali
  righe.
* **Una nuova ferrovia.** Dicci dove sono pubblicati i dati. Possiamo scrivere
  il codice insieme, o rivedere il tuo.
* **Provarlo dove vivi.** Installalo, guarda la tua parte della mappa e
  dicci cosa va bene e cosa no.
* **Una correzione di questo README.** Se un passo non corrispondeva a ciò
  che hai visto, dicci cosa hai visto.

[**Dicci cosa hai in mente**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=it.yml)
o scrivi a
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
e ti risponderemo con i passi successivi.

---

## Lingue

Questo README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), [Español](README.es.md), **Italiano**,
[Dansk](README.da.md), [Suomi](README.fi.md), [Svenska](README.sv.md),
[Norsk bokmål](README.nb.md), [Gaeilge](README.ga.md). Ogni README tradotto
è completo. Nessuno è stato ancora letto da un madrelingua. Se una di queste
lingue è la tua, dicci se il suo README si legge bene: vedi
[Aiutaci a farlo crescere](#aiutaci-a-farlo-crescere).

La finestra di configurazione e le opzioni sono per ora solo in inglese,
qualunque sia la lingua del tuo Home Assistant. Se parli un'altra lingua, puoi
tradurle tu: è un breve elenco di frasi in un solo file, e [ti aiuteremo a
farlo](#aggiungerlo-tu-con-il-nostro-aiuto).

Hai trovato un errore in una traduzione, o ti serve un'altra lingua? Diccelo
su <https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues>,
o [traducilo con il nostro aiuto](#aggiungerlo-tu-con-il-nostro-aiuto).

---

## Riconoscimenti e licenze

Ogni fonte in tempo reale è letta durante l'esecuzione, dal tuo Home
Assistant; niente di un feed in tempo reale è in questo repository. Ogni
treno cita la sua fonte nel suo attributo `attribution`. Le condizioni di ogni
fonte vincolano te, in quanto persona che riceve i suoi dati.

* **Amtraker** (amtraker.com), che ritrasmette il tracciamento dei treni di
  Amtrak (Stati Uniti): dati sotto la
  [Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/),
  attribuzione obbligatoria. L'orario di **Amtrak** stessa per i tracciati dei
  percorsi.
* **Brightline** (Stati Uniti): i suoi feed GTFS e GTFS-Realtime; Brightline
  non pubblica condizioni.
* **VIA Rail** (Canada): i suoi dati sullo stato dei treni, per i quali VIA
  non pubblica condizioni; il suo orario sotto la Open Government Licence -
  Canada 2.0 ([developer resources](https://www.viarail.ca/en/developer-resources)).
* **Fintraffic / digitraffic.fi** (Finlandia): dati sotto CC BY 4.0.
* **Transport for NSW** (Australia): dati sotto CC BY 4.0
  ([licenza dei dati](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australia): dati sotto CC BY 4.0
  ([dati aperti](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Queensland Rail Travel** (Australia): gli orari che mostra la sua pagina
  Service Updates, letti dal tuo Home Assistant; vedi la
  [pagina sul copyright di Queensland Rail](https://www.queenslandrailtravel.com.au/copyright).
  Niente di Queensland Rail Travel è fornito con l'integrazione.
* **Journey Beyond** (Australia): i suoi orari pubblicati, trascritti in
  `data/journey_beyond_timetable.json`; Journey Beyond non pubblica condizioni
  per essi.
* **Public Transport Authority of Western Australia**: dati degli orari
  disponibili gratuitamente su www.transperth.wa.gov.au
  ([spatial data access](https://www.transperth.wa.gov.au/About/Spatial-Data-Access);
  non CC BY).
* **Renfe** (Spagna): dati sotto CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)).
* **Entur** (Norvegia): contiene dati sotto la licenza norvegese per i dati
  pubblici aperti ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)) distribuiti
  da Entur.
* **Trafikverket** (Svezia): dati sotto [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Irlanda): dati in tempo reale; Irish Rail non pubblica
  condizioni. Orario della [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Irlanda), CC BY 4.0, fornito così com'è.
* **NS** (Paesi Bassi): dati dei veicoli e mappa dei binari, con la tua
  chiave, secondo le condizioni del [portale API di NS](https://apiportal.ns.nl/).
  Orario e ritardi da [OVapi](https://gtfs.ovapi.nl/), CC0.
* **File forniti in `data/`**: tracciati dei percorsi per Journey Beyond,
  Queensland Rail Travel, Renfe (Spain) e la Svezia, costruiti da
  [OpenStreetMap](https://www.openstreetmap.org/copyright), © contributori di
  OpenStreetMap, sotto la
  [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/);
  i comuni delle stazioni capolinea dei viaggi di Renfe (OpenStreetMap, ODbL
  1.0) e le loro popolazioni (proprietà P1082 di Wikidata, CC0, altrimenti
  OpenStreetMap); popolazioni delle città capolinea svedesi da Statistics
  Sweden (SCB) e Trafikverket, entrambe CC0 1.0; popolazioni delle città
  capolinea norvegesi da Statistics Norway, tabella 04859, CC BY 4.0.
* **La scheda mappa** è [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, una copia di [ha-map-card](https://github.com/nathan-gs/ha-map-card) di
  nathan-gs, MIT, fornita in `frontend/`. Le sue tessere di mappa e i loro
  riconoscimenti sono nel suo README.

Nessuna di queste organizzazioni ha realizzato o approvato questa
integrazione.

**Codice**: MIT, in [LICENSE](LICENSE). I file in `data/` mantengono le
licenze delle loro fonti, elencate sopra.

**Per sviluppatori:** ogni ferrovia è un modulo in
`custom_components/live_track_intercity_rail/operators/`, che legge un
adattatore di fonte in `sources/`; i tracciati dei percorsi forniti si
ricostruiscono con gli script in `tools/` (`journey_beyond.py`,
`qrt_lines.py`, `renfe_spain_lines.py`, `sweden_lines.py`). I test si
eseguono con `python -m unittest discover -s tests`.

---

## Parole chiave

treni Home Assistant · tracciamento treni Home Assistant · mappa dei treni in
tempo reale · treni intercity · treni a lunga percorrenza · treni in tempo
reale · GTFS-Realtime · Amtrak · Amtraker · Brightline · VIA Rail · trains en
temps réel · VR · kaukojunat · NSW TrainLink · XPT · V/Line · The Ghan ·
Indian Pacific · Spirit of Queensland · Transwa · Renfe · AVE · Avlo · Alvia ·
Rodalies · trenes en tiempo real · Vy · SJ Nord · tog i sanntid · SJ ·
Snälltåget · Öresundståg · tåg i realtid · Irish Rail · Enterprise ·
traenacha beo · NS Intercity · Arriva · treinen live · Zugverkehr · togtrafik ·
火车实时地图 · geo_location · scheda mappa · Lovelace · HACS · Marketplace ·
Live Track · LiveTrack · StrausbergAutomationWorks

---

**Riconoscimento.** StrausbergAutomationWorks riconosce i popoli indigeni di
tutte le terre e le acque di questa mappa, in tutto il mondo, e rende omaggio ai
loro Anziani del passato e del presente.
