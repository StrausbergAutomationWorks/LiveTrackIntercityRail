# Live Track Intercity Rail

[English](README.md) · [Deutsch](README.de.md) · **Français** · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · [Gaeilge](README.ga.md) · [Toutes les langues](#langues)

**Les trains grandes lignes pour Home Assistant, sur une seule carte.** Live
Track Intercity Rail place sur votre carte Home Assistant chaque train des
compagnies ferroviaires intercités et grandes lignes que vous choisissez : où
il se trouve, son numéro, s'il est en retard selon la règle de la compagnie,
et son prochain arrêt. Chaque compagnie est ajoutée séparément, à partir de
ses propres données publiées.

> **Live Track Intercity Rail est un module de Live Track**, une famille
> d'intégrations Home Assistant qui dessinent tout ce qui bouge, et la météo
> qu'il traverse, sur une seule carte partagée : avions, navires, trains et
> météo. Installez-le seul, ou à côté des autres modules
> ([liste ci-dessous](#les-autres-modules-de-live-track)).

> **Il grandit, et il est ouvert aux idées.** Live Track Intercity Rail couvre
> aujourd'hui 33 compagnies ferroviaires dans 9 pays sur 3 continents, et nous
> ajoutons d'autres compagnies et d'autres pays. La vôtre manque ?
> [Proposez-la](#aidez-le-à-grandir), ou ajoutez-la vous-même : nous vous
> aiderons à le faire.

**État : 0.1.4, publié.** Dans le catalogue du Marketplace ([l'installer
ci-dessous](#linstaller-étape-par-étape)).

Travail original de StrausbergAutomationWorks. Ni affilié à, ni approuvé par
Amtrak, Amtraker, Brightline, VIA Rail, Fintraffic, VR, Transport for NSW,
NSW TrainLink, Transport Victoria, V/Line, Queensland Rail, Journey Beyond,
la Public Transport Authority of Western Australia, Transwa, Renfe, Rodalies
de Catalunya, Entur, Vy, Go-Ahead Norge, SJ Nord, Trafikverket, SJ, VR
Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen,
Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget,
Värmlandstrafik, Tågab, Inlandsbanan, Irish Rail, la National Transport
Authority (Irlande), NS, Arriva, Keolis, OVapi, ni aucune autre compagnie
ferroviaire.

---

## Sommaire

1. [Tout ce qu'il fait](#tout-ce-quil-fait)
2. [Où il fonctionne](#où-il-fonctionne)
3. [Les autres modules de Live Track](#les-autres-modules-de-live-track)
4. [Avant de commencer](#avant-de-commencer)
5. [L'installer, étape par étape](#linstaller-étape-par-étape)
6. [Le configurer, étape par étape](#le-configurer-étape-par-étape)
7. [Clés gratuites qui activent plus, étape par étape](#clés-gratuites-qui-activent-plus-étape-par-étape)
8. [Mettre la carte sur un tableau de bord](#mettre-la-carte-sur-un-tableau-de-bord)
9. [L'utiliser dans des automatisations](#lutiliser-dans-des-automatisations)
10. [Tout ce qui est sur la carte, en détail](#tout-ce-qui-est-sur-la-carte-en-détail)
11. [Toutes les entités qu'il crée](#toutes-les-entités-quil-crée)
12. [Ce qu'il envoie et télécharge](#ce-quil-envoie-et-télécharge)
13. [Aidez-le à grandir](#aidez-le-à-grandir)
14. [Langues](#langues)
15. [Crédits et licences](#crédits-et-licences)
16. [Mots-clés](#mots-clés)

---

## Tout ce qu'il fait

### Sur la carte, sans rien configurer

Vous ajoutez une **compagnie ferroviaire** : vous choisissez un pays, puis
l'une de ses compagnies grandes lignes. Tout ce qui suit apparaît alors pour
cette compagnie. Ajoutez de nouveau l'intégration pour chaque autre compagnie
que vous voulez.

| Quoi | Où | Source |
|---|---|---|
| **Trains en service** : un marqueur par train, avec son numéro ou sa ligne, aux couleurs de la compagnie, tourné dans son sens de marche | chaque compagnie | les données publiées de chaque compagnie |
| **Retard** : un train apparaît en retard ou très en retard selon la règle de la compagnie ; là où une compagnie ne publie aucune règle, selon la longueur de son trajet | chaque compagnie qui publie des retards | le flux de chaque compagnie |
| **Prochain arrêt et son heure** : la gare où un train s'arrête ensuite, et quand il y est attendu | chaque compagnie dont le flux ou l'horaire l'indique | le flux et l'horaire de chaque compagnie |
| **Des trains qui suivent les voies** : entre deux rapports, un train avance sur sa propre ligne à sa dernière vitesse, et non en ligne droite | chaque compagnie dont la ligne est connue | l'horaire de chaque compagnie, ou des lignes livrées avec l'intégration |
| **Des trains d'après l'horaire** : là où une compagnie ne publie aucune position, chaque train est placé sur sa ligne selon ses horaires, et marqué comme estimation | Journey Beyond, Queensland Rail Travel et WA Trains (Australie), SJ Nord (Norvège) ; Irish Rail avec son dernier retard | l'horaire ou les heures de chaque compagnie |
| **Des images pour certains trains** : le Santa Claus Express et un chalet d'été (Finlande), les animaux des trains de Journey Beyond, une image pour chaque ligne de Queensland Rail Travel | Finlande, Australie | dessinées pour cette intégration |
| **Arrêté à la frontière** : un train à l'arrêt à un poste frontière entre les États-Unis et le Canada affiche « Customs » à la place de son retard | les trains d'Amtrak vers et depuis le Canada | les positions d'Amtrak |
| **Un compteur par compagnie** : trains en service | chaque compagnie | les mêmes données |

### Activé par votre propre clé ou compte gratuit

| Clé ou compte gratuit | Ce qu'il ajoute |
|---|---|
| Clé **Transport for NSW Open Data** | les trains régionaux de NSW TrainLink (Nouvelle-Galles du Sud, Australie) |
| Clé **Transport Victoria Open Data** | les trains grandes lignes de V/Line (Victoria, Australie) |
| Clé du **NS API portal** | NS Intercity, les trains régionaux d'Arriva et de Keolis (Pays-Bas) ; une seule clé pour les trois |
| Clé **Trafikverket** | les 15 compagnies suédoises ; une seule clé pour les quinze |

Chacune s'obtient en quelques minutes : [étape par étape ci-dessous](#clés-gratuites-qui-activent-plus-étape-par-étape).
Les 13 autres compagnies n'ont besoin d'aucune clé.

---

## Où il fonctionne

| Région | Ce que vous obtenez | Source | Il faut |
|---|---|---|---|
| **Australie** : dans tout le pays | Journey Beyond : The Ghan, The Ghan Expedition, Indian Pacific, Great Southern, The Overland, d'après l'horaire seulement ([pourquoi](#journey-beyond-australie)) | Journey Beyond | rien |
| **Australie** : Nouvelle-Galles du Sud | les trains régionaux de NSW TrainLink (XPT et Xplorer), aussi vers le Queensland, le Victoria et le Territoire de la capitale australienne | Transport for NSW | une clé gratuite |
| **Australie** : Queensland | Queensland Rail Travel : Spirit of Queensland, Spirit of the Outback, Tilt Train, Westlander, Inlander, Kuranda Scenic Railway, Gulflander, d'après leurs heures publiées ([pourquoi](#queensland-rail-travel-australie)) | Queensland Rail Travel | rien |
| **Australie** : Victoria | les trains grandes lignes de V/Line (ses lignes de banlieue sont dans Live Track Commuter Rail), aussi vers la Nouvelle-Galles du Sud | Transport Victoria | une clé gratuite |
| **Australie** : Australie-Occidentale | WA Trains : l'Australind, le Prospector, le MerredinLink et l'AvonLink, d'après l'horaire seulement ([pourquoi](#wa-trains-australie-occidentale-australie)) | Public Transport Authority of Western Australia | rien |
| **Europe** : Finlande | les trains grandes lignes de VR | Fintraffic Digitraffic | rien |
| **Europe** : Irlande | les trains InterCity d'Irish Rail, et l'Enterprise de Dublin à Belfast (Royaume-Uni) | Irish Rail, National Transport Authority | rien |
| **Europe** : Pays-Bas | NS Intercity, et les trains régionaux d'Arriva (Arriva, RRReis, Blauwnet) et de Keolis (Blauwnet, RRReis) ; les Sprinter de NS sont dans Live Track Commuter Rail | NS, OVapi | une clé gratuite |
| **Europe** : Norvège | les lignes F, RE, RX et R de Vy (F1 aussi vers la Suède), F5 et R50 de Go-Ahead Norge, F6, F7 et R60 à R75 de SJ Nord | Entur | rien |
| **Europe** : Espagne | les trains AVE, Avlo, Alvia, Avant, Euromed, Intercity, MD et Regional de Renfe, aussi vers la France et le Portugal ; les lignes régionales R11 à R17 de Rodalies de Catalunya | Renfe | rien |
| **Europe** : Suède | SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget, Värmlandstrafik, Tågab et Inlandsbanan, chacune comme compagnie à part ; Öresundståg aussi jusqu'au Danemark | Trafikverket | une clé gratuite |
| **Amérique du Nord** : Canada | VIA Rail, toutes les lignes | VIA Rail | rien |
| **Amérique du Nord** : États-Unis | Amtrak, toutes les lignes, aussi vers le Canada | Amtraker | rien |
| **Amérique du Nord** : États-Unis | Brightline (Floride) | Brightline | rien |

Elle n'est pas dans la liste ? [Dites-le-nous](#aidez-le-à-grandir). Là où
quelqu'un publie les données ouvertement, nous étudierons leur ajout.

⚠ **Un train ne vaut que ce que valent les données de sa compagnie.** Certaines
compagnies signalent un train toutes les quelques secondes, d'autres toutes
les quelques minutes, d'autres seulement quand il passe des signaux, et
certaines ne publient aucune position. Les limites de chaque compagnie sont
dans [Tout ce qui est sur la carte, en détail](#tout-ce-qui-est-sur-la-carte-en-détail).

⚠ **Ce ne sont pas les informations officielles de la compagnie.** Avant de
voyager, consultez l'application ou le site de la compagnie.

---

## Les autres modules de Live Track

Live Track est un ensemble d'intégrations Home Assistant, une par type d'objet
en mouvement, toutes dessinées sur la même carte. Chacune fonctionne seule ;
ensemble, elles forment une seule image en direct. Elles partagent la carte et
une bibliothèque Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
donc en installer une autre n'ajoute aucune requête à une source qu'une autre
lit déjà.

| Module | Ce qu'il met sur la carte | État |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | les avions au-dessus de vous via l'ADS-B, avec routes et icônes par type | publié |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | navires et bateaux via l'AIS, près de chez vous ou n'importe où | publié |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | trains de banlieue en Amérique du Nord, en Europe et en Australie | publié |
| **Live Track Intercity Rail** | trains intercités et grandes lignes en Amérique du Nord, en Europe et en Australie (ce module) | publié |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | avions et navires des services d'immigration et des forces de l'ordre fédérales, d'après des listes publiques | publié |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | météo, tempêtes et risques naturels | publié |
| [Live Track Internet](https://github.com/StrausbergAutomationWorks/LiveTrackInternet) | pannes d'internet, câbles sous-marins et liaisons terrestres | publié |
| Live Track Stations | tableaux des départs et rappels « il est temps de partir » pour chaque gare | prévu |
| Live Track Satellites | les satellites qui passent au-dessus de vous | prévu |
| Live Track Freight Trains | trains de marchandises et de travaux là où les chemins de fer les publient | prévu |
| Live Track Transit | bus urbains, tramways, ferries et métros | prévu |
| Live Track Intercity Buses | autocars interurbains et régionaux | prévu |
| Live Track Commuter Buses | bus de banlieue | prévu |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la carte partagée sur laquelle dessine chaque module | publiée, installée avec chaque module |

Tout est gratuit et libre. Rien n'est réservé aux sponsors.

---

## Avant de commencer

* **Home Assistant** 2026.11 ou plus récent.
* **Le Marketplace** (HACS) dans votre Home Assistant, pour l'installer et le
  mettre à jour facilement. Sans lui, vous pouvez copier les fichiers à la
  main.
* **Un accès à Internet** pour Home Assistant : chaque train vient des données
  publiées par sa compagnie.
* Rien à payer. 13 des 33 compagnies n'ont besoin d'aucun compte ; les 20
  autres ont besoin de votre propre clé gratuite, et quatre clés les couvrent
  toutes ([ci-dessus](#activé-par-votre-propre-clé-ou-compte-gratuit)).
* Home Assistant installe lui-même les paquets Python dont il a besoin
  (`saw-livetrack`, `gtfs-realtime-bindings` et `tzdata`) la première fois
  que l'intégration se charge.

---

## L'installer, étape par étape

### Depuis le Marketplace (recommandé)

1. Dans Home Assistant, ouvrez **Paramètres → Marketplace** (HACS).
2. Recherchez **Live Track Intercity Rail** et ouvrez-le.
3. Choisissez **Télécharger** (ou **Installer**).
4. **Redémarrez Home Assistant** : **Paramètres → Système → Corrections**
   propose le redémarrage, ou utilisez **Paramètres → Système → Redémarrer**.

Si la recherche ne le trouve pas, ajoutez-le par son lien : choisissez **Ajouter
grâce à un lien** (ou le menu à trois points → **Dépôts personnalisés**),
saisissez `StrausbergAutomationWorks/LiveTrackIntercityRail`, choisissez
**Intégration** si le type est demandé, puis reprenez à l'étape 3.

Le Marketplace propose ensuite chaque nouvelle version comme mise à jour.

### À la main

1. Téléchargez le code source de la
   [dernière version](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/releases/latest).
2. Copiez son dossier `custom_components/live_track_intercity_rail` dans le
   dossier `custom_components` du dossier de configuration de votre Home
   Assistant (créez `custom_components` s'il n'existe pas).
3. Redémarrez Home Assistant.

Pour mettre à jour à la main, remplacez le dossier par celui de la nouvelle
version et redémarrez.

---

## Le configurer, étape par étape

1. Ouvrez **Paramètres → Appareils et services**.
2. Choisissez **Ajouter une intégration** (en bas à droite) et cherchez
   **Live Track Intercity Rail**.
3. **Region** (la région) : choisissez le pays de la compagnie. Seuls les pays
   ayant au moins une compagnie sont listés. Choisissez **Valider**.
4. **Railroad** (la compagnie) : choisissez la compagnie. Choisissez
   **Valider**.
5. **API key** (la clé) : seulement pour NSW TrainLink, V/Line, les trois
   compagnies néerlandaises et les quinze compagnies suédoises. Collez votre
   clé ([comment en obtenir une](#clés-gratuites-qui-activent-plus-étape-par-étape))
   et choisissez **Valider**. Les autres compagnies sautent cette étape.

C'est tout. Les trains apparaissent en une ou deux minutes. Là où les lignes
d'une compagnie viennent de son horaire, les trains suivent leurs lignes une
fois l'horaire téléchargé, ce qui peut prendre quelques minutes la première
fois. Pour suivre une autre compagnie, ajoutez de nouveau l'intégration. La
même compagnie deux fois est refusée.

### Changer ce qu'il affiche : les options

Ouvrez **Paramètres → Appareils et services → Live Track Intercity Rail →
Configurer** (la roue dentée) sur la compagnie que vous voulez modifier. Il y
a une option :

| Option | Ce qu'elle fait | Par défaut |
|---|---|---|
| **Poll interval** (intervalle de lecture) | la fréquence de lecture de la source de la compagnie, de 15 à 600 secondes. Un intervalle plus court que la mise à jour de la source n'affiche rien de plus | selon la compagnie : 15 secondes pour Renfe (Spain) et les trois compagnies néerlandaises ; 60 secondes pour Brightline, NSW TrainLink, Irish Rail et SJ Nord ; 30 secondes pour les autres |

---

## Clés gratuites qui activent plus, étape par étape

Vingt compagnies demandent à chaque utilisateur sa propre clé, auprès de
quatre fournisseurs. Chacune de ces clés est gratuite, et chaque personne qui
installe Live Track Intercity Rail obtient la sienne. Vous collez la clé quand
la boîte de dialogue de configuration la demande
([étape 5 ci-dessus](#le-configurer-étape-par-étape)). Seule la clé est
demandée : aucun mot de passe et aucun secret. La clé est enregistrée dans
Home Assistant avec l'intégration, envoyée seulement à son propre fournisseur,
et jamais écrite dans le journal. Si le fournisseur la refuse pendant dix
minutes, Home Assistant vous en demande une nouvelle.

### Transport for NSW (NSW TrainLink, Nouvelle-Galles du Sud, Australie)

1. Ouvrez <https://opendata.transport.nsw.gov.au/>, choisissez **Register**,
   créez un compte, et connectez-vous.
2. Choisissez l'icône de votre profil, puis **API Tokens**.
3. Saisissez un nom pour la clé et choisissez **CREATE API TOKEN**. Copiez la
   clé tout de suite : le site ne l'affiche qu'une fois.
4. Collez-la dans **API key** quand vous ajoutez NSW TrainLink. Collez la clé
   seule : Live Track Intercity Rail ajoute lui-même le mot `apikey`.

### Transport Victoria (V/Line, Victoria, Australie)

1. Ouvrez <https://opendata.transport.vic.gov.au/>, choisissez **Login**,
   puis **Sign up**.
2. Saisissez vos informations et choisissez **Create Account**. Saisissez le
   code de l'e-mail que vous recevez et choisissez **Confirm**.
3. Le portail demande une application d'authentification sur votre
   téléphone : scannez le code QR avec elle, saisissez le code de
   l'application et choisissez **Confirm**. Connectez-vous ensuite avec votre
   e-mail, votre mot de passe et le code de l'application.
4. Choisissez **My Account** → **Profile** → **API tokens**. Votre clé y est
   déjà. Collez-la dans **API key** quand vous ajoutez V/Line.

### NS (NS, Arriva et Keolis, Pays-Bas)

1. Ouvrez <https://apiportal.ns.nl/>, choisissez **Inloggen** (se connecter),
   puis **Externe bezoeker** (visiteur externe).
2. Remplissez le formulaire et envoyez-le. Un e-mail confirme l'inscription.
   Les API peuvent mettre jusqu'à 5 minutes à apparaître dans le portail.
3. Ouvrez la page de la **Virtual Train API** (les positions des trains de
   NS). Sous **Related Products**, ouvrez son produit, donnez un nom à votre
   abonnement, et choisissez **Subscribe**.
4. Quand NS a approuvé l'abonnement, votre clé se trouve sur votre page de
   profil. Collez-la dans **API key** quand vous ajoutez NS, Arriva ou Keolis.
   Une seule clé sert pour les trois.

### Trafikverket (les 15 compagnies suédoises)

1. Ouvrez <https://data.trafikverket.se/oauth2/Account/register>.
2. Remplissez **Email**, **Displayname**, **Password** et **Confirm
   password**, cochez **Accept license and Agreement**, et choisissez
   **Register**.
3. Ouvrez <https://data.trafikverket.se/get-started> et choisissez **Create
   key**, sous **Create a key**. Connectez-vous avec le compte que vous avez
   créé, et créez la clé.
4. Collez-la dans **API key** quand vous ajoutez une compagnie suédoise. Une
   seule clé sert pour les quinze.

---

## Mettre la carte sur un tableau de bord

La carte est [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la carte sur laquelle dessine chaque module Live Track. **Elle est installée
avec Live Track Intercity Rail** : rien à télécharger, rien à copier, aucune
ressource à ajouter.

1. Ouvrez un tableau de bord, choisissez le crayon (**Modifier le tableau de
   bord**), puis **Ajouter une carte**.
2. Faites défiler jusqu'en bas et choisissez **Manuel**.
3. Collez ceci, et choisissez **Enregistrer** :

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

Les autres modules Live Track vont dans `entity_filter` de la même façon : une
règle `- domain: geo_location` de plus pour chaque source.

**Sur la carte :**

* Chaque train est un marqueur aux couleurs de sa compagnie, avec son numéro
  ou sa ligne. Les trains d'Amtrak sont des étoiles, ceux de VIA Rail portent
  la feuille d'érable, les trains InterCity d'Irish Rail sont des trèfles, et
  certains trains sont des images (chaque compagnie ci-dessous dit
  lesquels).
* Sur la plupart des compagnies, les couleurs s'inversent avec le sens : l'un
  en quittant la ville principale, l'autre en allant vers elle.
* Une flèche montre le sens de marche. Un train à l'arrêt garde son dernier
  sens. Les images restent droites et n'ont pas de flèche.
* **Pointez** un train pour voir sa compagnie, son numéro, sa ligne et son
  trajet. **Cliquez** dessus pour tous ses détails, y compris son prochain
  arrêt et son retard.

Si les ressources de vos tableaux de bord sont définies en YAML
(`lovelace: resource_mode: yaml`), rien ne peut être enregistré pour vous :
un élément dans **Corrections** donne alors les lignes exactes à ajouter à
`configuration.yaml`. Elles ressemblent à ceci, avec l'adresse propre de
l'intégration à la place des espaces réservés :

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_intercity_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Chaque module Live Track porte une copie de la carte et l'enregistre au
démarrage de Home Assistant. Ensemble, ils gardent exactement une ligne dans
**Paramètres → Tableaux de bord → Ressources** : la version de carte la plus
récente que l'un d'eux porte, jamais une plus ancienne. Une carte que vous
avez installée vous-même par le Marketplace n'est pas touchée. Quand vous
retirez la dernière compagnie de ce module, la ligne passe à un autre module
Live Track, ou elle est retirée s'il n'en reste aucun. Si les fichiers de
l'intégration sont retirés alors que ses compagnies sont encore configurées,
et qu'aucun autre module Live Track n'est installé, retirez vous-même la ligne
dans **Paramètres → Tableaux de bord → Ressources**.

**Pour installer plutôt la carte à la main**, suivez les étapes du
[README de la carte](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
Une ligne que vous avez créée vous-même, pour une copie sous `/local/` ou à
toute autre adresse, n'est jamais modifiée ni supprimée. Tant qu'elle charge la
carte, chaque module Live Track lui laisse la carte, même quand un module
apporte une version plus récente, et rien dans **Corrections** ne le signale.
Pour revenir à la copie du module, supprimez votre ligne dans **Paramètres →
Tableaux de bord → Ressources** et redémarrez Home Assistant. Si vous supprimez
le fichier de votre copie, supprimez aussi sa ligne : tant qu'une ligne dont le
fichier a disparu reste en place, le module n'ajoute pas sa propre ligne.

Toute autre carte qui affiche les entités `geo_location` affiche aussi les
trains, comme de simples marqueurs.

---

## L'utiliser dans des automatisations

Tout est une entité Home Assistant ordinaire, donc l'éditeur d'automatisations
fonctionne avec, sans code.

**Une notification sur le téléphone quand les données de votre compagnie
s'arrêtent** (les trains quittent alors la carte) :

1. **Paramètres → Automatisations et scènes → Créer une automatisation →
   Créer une nouvelle automatisation**.
2. **Quand** : **Ajouter un déclencheur** → **Entité** → **L'état a changé**.
   Choisissez l'entité **Trains in service** de la compagnie, et sous **À
   (facultatif)** choisissez **Indisponible**.
3. **Alors faire** : **Ajouter une action**, cherchez l'action de
   notification de votre téléphone (elle porte le nom de votre téléphone), et
   saisissez un message, par exemple :

   ```text
   Aucun train grandes lignes sur la carte : les données de la compagnie se sont arrêtées
   ```

4. **Enregistrer**.

**Autres idées :** une lumière qui s'allume quand un train d'Amtrak est à
moins de 2 km (1,2 mille) de votre domicile aux États-Unis, d'après la
distance des marqueurs ; un compteur sur un tableau de bord des trains que VR
fait rouler en Finlande au fil de la journée ; un message quand le premier
train du jour de Queensland Rail Travel part (Australie), d'après **Trains in
service** qui passe au-dessus de 0.

---

## Tout ce qui est sur la carte, en détail

### Les trains

Chaque train est un marqueur. Son état est sa distance à votre domicile, en
kilomètres. Le marqueur apparaît quand la compagnie signale le train, ou quand
son horaire dit qu'il roule, et il est retiré quand le train quitte les
données de la compagnie ou que son trajet est terminé.

* **Entre deux rapports**, un train avance sur sa propre ligne vers son
  prochain arrêt : à la vitesse que la compagnie signale, ou, là où elle n'en
  signale aucune, à la vitesse entre ses deux derniers rapports. Il ne dépasse
  jamais son prochain arrêt, et s'arrête 30 minutes après le dernier rapport.
  Un train sur une ligne connue est dessiné sur la ligne ; le rapport de la
  compagnie est gardé à côté.
* **Si les données d'une compagnie tombent en panne**, ses trains continuent
  d'avancer sur le dernier bon rapport pendant 10 minutes au plus. Ensuite,
  ils sont indisponibles et quittent la carte jusqu'au retour des données.
* **En retard et très en retard** : là où la compagnie publie sa propre règle
  pour un train en retard, l'intégration l'utilise. Là où elle n'en publie
  aucune, un train est en retard selon la longueur de son trajet, avec les
  seuils d'Amtrak Status Maps (asm.transitdocs.com). Chaque compagnie
  ci-dessous dit laquelle.

Sur chaque train : `marker_label`, `train`, `line_name`, `observed_at` (quand
son rapport était vrai), `course_deg` (quand il roule), `next_stop` et
`arrival_estimated_at` (si connus), `delay_min`, `late_threshold_min` et
`very_late_threshold_min`, `speed_kmh` (si la compagnie la signale),
`attribution`, et, entre deux rapports, `previous_latitude`,
`previous_longitude`, `previous_observed_at` et `segment_duration_s`. Un train
avancé sur sa ligne porte `position_source: estimated`, avec le rapport de la
compagnie dans `fix_latitude` et `fix_longitude`.

### Journey Beyond (Australie)

⚠ **Journey Beyond ne publie aucune position.** Chaque train est dessiné
d'après son horaire publié, recopié dans un fichier livré avec l'intégration
(départs jusqu'au 29 décembre 2027), donc rien n'est téléchargé. Chaque train
est placé sur sa ligne selon ses horaires, marqué comme estimation, sans
retard : un train en retard ou supprimé est quand même dessiné à l'heure.
Chaque service a sa propre image (le chameau et son cavalier, un oiseau, un
kangourou, un émeu), dans ses couleurs à l'aller et inversées au retour, sans
étiquette : pointez-le pour voir le train et son trajet.

### NSW TrainLink (Nouvelle-Galles du Sud, Australie)

D'après le flux NSW TrainLink de Transport for NSW, avec votre propre clé, une
nouvelle position environ une fois par minute. L'étiquette est le numéro du
train. Orange NSW avec un anneau blanc en quittant Sydney, inversé en y
allant. Le flux n'a pas de vitesse, donc un train avance sur sa ligne à la
vitesse entre ses deux dernières positions. En retard à partir de 11 minutes
(NSW TrainLink compte un train à l'heure dans les 10 minutes), très en retard
à partir de 30.

### Queensland Rail Travel (Australie)

⚠ **Queensland Rail Travel ne publie aucune position.** Votre Home Assistant
lit les heures que montre la page « Service Updates » de Queensland Rail
Travel : la liste des trains du jour au plus toutes les 5 minutes, et les
heures de chaque train au plus toutes les 5 minutes, de 30 minutes avant son
départ jusqu'à 15 minutes après son arrivée. Chaque train est placé sur sa
ligne selon ces heures et marqué comme estimation. Chaque ligne a sa propre
image, dans ses couleurs en quittant Brisbane et inversées en y allant, avec
le numéro du train dans une étiquette à côté. Aucun retard ni grand retard
n'est affiché.

### V/Line (Victoria, Australie)

D'après le flux V/Line de Transport Victoria, avec votre propre clé : les
lignes grandes lignes vers Albury, Ararat, Bairnsdale, Echuca, Maryborough,
Shepparton, Swan Hill et Warrnambool. L'étiquette est le numéro du train.
Violet V/Line avec un anneau jaune en quittant Melbourne, inversé en y allant.
Le flux n'a pas de vitesse, donc un train avance à la vitesse entre ses deux
dernières positions ; après 10 minutes sans nouvelle position, il est mené à
son prochain arrêt selon l'horaire. En retard à partir de 11 minutes sur les
longues lignes et de 6 sur les courtes (la liste propre de V/Line), très en
retard à partir de 30.

### WA Trains (Australie-Occidentale, Australie)

⚠ **Aucune position en direct n'est publiée.** Chaque train est dessiné
d'après l'horaire de la Public Transport Authority of Western Australia :
placé sur sa ligne selon ses heures prévues, marqué comme estimation, sans
retard. L'horaire est vérifié une fois par jour. L'étiquette est faite des
trois premières lettres de la ligne : AUS (Australind, violet), PRO
(Prospector, orange), MER (MerredinLink, vert) et AVO (AvonLink, vert), les
mêmes dans les deux sens.

### VR (Finlande)

D'après Digitraffic de Fintraffic, une nouvelle position environ toutes les
30 secondes. L'étiquette est le type et le numéro du train, comme VR les
écrit (`IC 23`). Vert VR avec un anneau sombre en quittant Helsinki, inversé
en y allant. Les données n'ont pas de sens de marche, donc la flèche suit la
ligne. En retard à partir de 6 minutes (VR compte un train en retard quand il
a plus de cinq minutes de retard), très en retard à partir de 12.

* **Le Santa Claus Express**, du premier dimanche de l'Avent au 6 janvier : un
  bonhomme de neige vers le nord, un renne au retour, sans numéro. À partir de
  12 minutes de retard, la figure se retourne toutes les quelques secondes.
* **Le chalet d'été**, de la veille de la Saint-Jean au 31 juillet : chaque
  train grandes lignes de VR est dessiné comme un chalet, avec son numéro à
  côté.

### Irish Rail (Irlande)

D'après le service en direct d'Irish Rail et l'horaire de la National
Transport Authority. ⚠ Irish Rail ne signale un train que lorsqu'il passe des
points de signalisation espacés de quelques minutes, donc chaque train est
dessiné d'après son horaire et son dernier retard, avancé sur son itinéraire.
L'étiquette est le numéro du train sans sa lettre (A700 affiche 700). Un train
InterCity est un trèfle vert avec un contour et un numéro orange en quittant
Dublin, les couleurs inversées en y allant. L'Enterprise est un disque argenté
avec un anneau extérieur rouge, une bande magenta et un numéro magenta ; en
allant vers Dublin, le disque est magenta. En retard à partir de 10 minutes
(la règle de la National Transport Authority), très en retard à partir de 20.

### NS, Arriva et Keolis (Pays-Bas)

D'après les données de véhicules de NS, avec votre propre clé, une nouvelle
position environ toutes les 10 secondes. Ce flux signale la vitesse et le sens
propres du train, et les deux sont transmis. Le prochain arrêt et le retard
viennent de l'horaire d'OVapi ; les voies sont la carte des lignes de NS,
téléchargée une fois par jour. L'étiquette est le numéro du train. Les trains
de NS sont jaunes avec un anneau bleu NS ; ceux d'Arriva et de Keolis ont pour
l'instant l'apparence par défaut de la carte. En retard à partir de 3 minutes
(la définition propre de NS), très en retard à partir de 10.

### Vy, Go-Ahead Norge et SJ Nord (Norvège)

D'après Entur, chaque compagnie dans sa propre entrée. L'étiquette est le code
de la ligne (F4, RE10, R50). La couleur propre de la ligne avec un anneau
blanc en quittant Oslo S (sur un trajet qui n'atteint pas Oslo S, sa plus
grande ville terminus), inversée en y allant. Entur ne publie ni vitesse ni
sens de marche, donc un train avance à la vitesse entre ses deux dernières
positions, et la flèche suit sa ligne. Dans les longs tunnels d'Oslo, un train
dont les positions s'arrêtent est avancé sur sa ligne jusqu'à leur retour.
⚠ **SJ Nord ne publie aucune position :** chacun de ses trains est placé sur
sa ligne selon ses heures prévues. En retard à partir de 4 minutes, et de 6
sur les lignes F et les lignes vers Göteborg (Suède), la règle de Bane NOR et
de Vy ; très en retard au double.

### Renfe (Spain) et Renfe Regionals (Catalogne, Espagne)

**Renfe (Spain)** lit le flux grandes lignes de Renfe, une nouvelle position
environ toutes les 15 secondes. L'étiquette est le numéro du train ; le
service (AVE, Avlo, Alvia, etc.) est dans l'info-bulle. AVE bleu marine, Avlo
turquoise, tout autre service violet Renfe, chacun plein en quittant Madrid
(sur un trajet qui n'atteint pas Madrid, sa plus grande ville terminus) et
inversé en y allant. Renfe ne publie pas le tracé des lignes, donc les lignes
sont construites à partir d'OpenStreetMap et livrées avec l'intégration. Renfe
ne publie aucune règle pour un train en retard, donc un train est en retard
selon la longueur de son trajet : à partir de 10 minutes jusqu'à 400 km
(250 milles), 15 jusqu'à 560 km (350 milles), 20 jusqu'à 725 km
(450 milles), 25 jusqu'à 885 km (550 milles), 30 au-delà ; très en retard au
double.

**Renfe Regionals (Catalunya)** dessine les lignes régionales R11 à R17 de
Rodalies de Catalunya. L'étiquette est le numéro du train, dans la couleur
propre de la ligne, plein en quittant Barcelone et inversé en y allant. Hors
de Barcelone, une position est la dernière gare qu'un train a passée, donc le
train est mené entre les gares selon l'horaire et son retard. En retard à
partir de 10 minutes, très en retard à partir de 20, selon la longueur de la
plus longue ligne. Avec les deux compagnies Renfe configurées, chaque train
est dessiné une seule fois.

### Les compagnies suédoises (Suède)

D'après Trafikverket, avec votre propre clé (une seule clé pour les quinze).
L'étiquette est le numéro du train sur le billet ; la marque, le numéro et les
gares terminus sont dans l'info-bulle. Chaque marque a ses propres couleurs,
inversées en allant vers Stockholm C (sur un trajet qui n'atteint pas
Stockholm C, sa plus grande ville terminus). Trafikverket donne une vitesse
pour environ la moitié de ses positions ; les autres trains avancent à la
vitesse entre leurs deux dernières positions. La Suède ne publie pas le tracé
des lignes, donc les lignes sont construites à partir d'OpenStreetMap et
livrées avec l'intégration. En retard à partir de 6 minutes (Trafikverket
compte un train à l'heure jusqu'à 5 minutes 59 secondes), très en retard à
partir de 12.

### VIA Rail (Canada)

D'après les données d'état des trains de VIA Rail. Chaque train est un disque
avec la feuille d'érable et une bande à la couleur de son groupe de lignes
(Atlantique, Ouest, Ontario et Québec, Prince Rupert, Churchill, Sudbury à
White River, Montréal panoramique), avec le numéro du train dans une étiquette
droite. Les numéros impairs ont un disque jaune, les pairs un disque à la
couleur de la bande. Un train sans nouvelle position avance vers son prochain
arrêt pour arriver à l'heure estimée par VIA. VIA ne publie aucune règle pour
un train en retard, donc un train est en retard à partir de 10 minutes sur le
corridor Québec–Windsor et de 60 ailleurs (les valeurs d'Amtrak Status Maps
pour VIA), très en retard au double.

### Amtrak (États-Unis)

Amtrak ne publie aucune donnée en direct ouverte. Amtraker relaie le suivi des
trains d'Amtrak, avec une nouvelle position toutes les 3 à 5 minutes, et
l'intégration fait avancer chaque train sur sa ligne à la vitesse signalée par
Amtrak. Chaque train est une étoile avec son numéro au milieu, aux couleurs de
sa ligne (les lignes du Nord-Est, Cascades, Pacific Surfliner, Acela et
d'autres), sinon l'étoile du drapeau. Le Maple Leaf (New York à Toronto)
passe lentement de l'étoile d'Amtrak à l'insigne de VIA. Un train à l'arrêt à
la frontière, à Lacolle, Rouses Point ou Niagara Falls, affiche « Customs » à
la place de son retard. En retard à partir de 16 minutes (Amtrak compte un
train à l'heure dans les 15 minutes), très en retard à partir de 30. Le même
numéro de train peut rouler deux ou trois jours à la fois, donc chaque trajet
est son propre marqueur.

### Brightline (États-Unis)

D'après le flux de Brightline, une nouvelle position environ toutes les
60 secondes. L'étiquette est le numéro du trajet, en noir bordé de blanc, sur
un disque à la couleur de la destination du train, avec un anneau noir. Une
position de plus de 5 minutes n'est pas utilisée. Le flux n'a pas de vitesse,
donc un train avance à la vitesse entre ses deux dernières positions.
Brightline ne publie aucune règle pour un train en retard, donc un train est
en retard à partir de 10 minutes, très en retard à partir de 20, selon la
longueur de son trajet.

---

## Toutes les entités qu'il crée

Pour chaque compagnie :

| Entité | Ce qu'elle est |
|---|---|
| `sensor.<railroad>_trains_in_service` | **Trains in service** (trains en service) : combien de trains la compagnie fait rouler sur la carte en ce moment. Pour Amtrak : `sensor.amtrak_trains_in_service` |
| `geo_location.<railroad>_train_…` | une par train (`geo_location.amtrak_train_5_17`) ; elle vient et part avec le train. Chacune porte `source: live_track_intercity_rail`, et son état est sa distance à votre domicile en kilomètres |

L'identifiant d'entité d'un marqueur vient de la compagnie et du trajet,
jamais de son étiquette : `geo_location.amtrak_train_5_17` est le train 5
d'Amtrak parti le 17 du mois. Ainsi un train garde le même identifiant pendant
tout son trajet, et un autre trajet du même numéro a le sien. Le marqueur est
retiré quand le trajet quitte les données de la compagnie ou se termine. Les
marqueurs n'ont pas d'identifiant unique, comme aucun marqueur de carte Live
Track, donc ils ne peuvent pas être renommés, masqués ou affectés à une pièce
dans l'interface. Le capteur a un identifiant unique et peut être renommé.

Les attributs qui changent à chaque lecture, les positions et les heures des
marqueurs, sont enregistrés dans l'historique de Home Assistant, comme pour
toute entité. Le capteur n'a pas d'attributs, il coûte donc peu à garder, et
il est la trace du nombre de trains qui ont roulé un jour donné. Pour garder
les marqueurs hors de l'historique, ajoutez ceci à `configuration.yaml`, puis
redémarrez :

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_train_*
```

Si votre `configuration.yaml` a déjà une section `recorder:`, ajoutez-y
seulement le motif `geo_location.*_train_*`, sous `exclude:` et
`entity_globs:`. Le motif ne correspond qu'aux marqueurs de trains de ce
module. Une carte réglée pour dessiner l'historique n'a alors aucune trace à
dessiner.

---

## Ce qu'il envoie et télécharge

**Sur votre position.** Rien. La position de votre domicile n'est utilisée
que dans votre Home Assistant, pour donner la distance de chaque train. Votre
clé, là où une compagnie en demande une, n'est envoyée qu'au fournisseur de
cette compagnie. Rien d'autre sur vous n'est envoyé nulle part. Chaque service
voit votre adresse Internet, comme tout site web.

**Combien.** Chaque source en direct est lue à chaque lecture, à l'intervalle
propre de la compagnie par défaut (**Poll interval**, de 15 à 600 secondes),
ou moins souvent là où le tableau le dit. Là où plusieurs modules Live Track
ou compagnies lisent la même source, un seul client partagé la lit une fois
pour tous. Mesuré le 19 novembre 2026, de 02:44 à 02:49 UTC :

| Compagnie | Données en direct, une lecture | Horaire et lignes |
|---|---|---|
| Journey Beyond (Australie) | aucune : rien n'est téléchargé | aucun : son horaire et ses lignes sont livrés avec l'intégration |
| NSW TrainLink (Australie) | 124 Ko de deux flux, au plus une fois toutes les 55 secondes | 40 Mo, quand il change, vérifié chaque jour |
| Queensland Rail Travel (Australie) | la liste, 5,5 Ko, toutes les 5 minutes ; les heures de chaque train en route, 6 à 8 Ko, toutes les 5 minutes | aucun : ses lignes sont livrées avec l'intégration |
| V/Line (Australie) | 14 Ko de deux flux | 58 Mo (la partie V/Line du fichier de 311 Mo de Transport Victoria, lue seule), quand il change, vérifié chaque jour |
| WA Trains (Australie) | aucune : il n'existe pas de flux en direct | 28 Mo, quand il change, vérifié chaque jour |
| VR (Finlande) | 1,4 Ko compressé pour les positions ; les trains du jour, 0,5 Mo compressé la première fois, puis seulement les changements, une fois par minute | 3,1 Mo, chaque jour |
| Irish Rail (Irlande) | 0,2 Ko, au plus une fois toutes les 55 secondes | 6,6 Mo, quand il change, vérifié chaque jour ; la liste des gares, 46 Ko, une fois par semaine |
| NS, Arriva, Keolis (Pays-Bas) | 1,5 Ko, au plus une fois toutes les 9 secondes ; les retards d'OVapi, 5,3 Mo, toutes les 5 minutes et seulement s'ils changent | l'horaire d'OVapi, 267 Mo, au plus une fois par semaine et seulement s'il change ; la carte des lignes de NS, 1,3 Mo, chaque jour |
| Vy, Go-Ahead Norge, SJ Nord (Norvège) | Vy 510 Ko de deux flux, Go-Ahead Norge 7 Ko, SJ Nord 0,7 Ko une fois par minute | Vy 67 Mo, Go-Ahead Norge 20 Mo, SJ Nord 26 Mo, quand il change, vérifié chaque jour |
| Renfe (Spain) (Espagne) | 2,1 Ko de deux flux | 0,7 Mo, chaque jour ; ses lignes sont livrées avec l'intégration |
| Renfe Regionals (Catalogne, Espagne) | 0,2 Ko de deux flux qui portent tous les réseaux locaux de Renfe | 16 Mo, chaque jour |
| Les compagnies suédoises (Suède) | 474 Ko la première fois, puis 5 à 9 Ko de changements | aucun ; la liste des gares, 0,15 Mo, chaque jour ; les lignes sont livrées avec l'intégration |
| VIA Rail (Canada) | 353 Ko, envoyés compressés en 33 Ko | 1,0 Mo, une fois par semaine |
| Amtrak (États-Unis) | 1,2 Mo, envoyés compressés en 113 Ko | 18,6 Mo, une fois par semaine |
| Brightline (États-Unis) | 1,3 Ko de deux flux | 29 Ko, une fois par semaine |

⚠ Au moment de la mesure, il faisait jour en Australie, c'était le soir en
Amérique du Nord et la nuit en Europe. Un flux en direct est au plus petit la
nuit : le jour, les flux européens sont plus gros que ne le montre le tableau.

**Après une erreur.** Les trains continuent d'avancer sur les dernières bonnes
données pendant 10 minutes au plus ; ensuite ils sont marqués indisponibles
jusqu'à ce que la source réponde. Un horaire dont le téléchargement échoue est
retenté plus tard, et la copie que vous avez reste utilisée. Si un
fournisseur refuse votre clé pendant dix minutes, Home Assistant vous en
demande une nouvelle.

**Sur le disque.** Les horaires et les lignes sont gardés dans le dossier
`.storage` de Home Assistant sous des noms commençant par `saw_`, partagés
avec les autres modules Live Track qui lisent la même compagnie. Si vous
retirez Live Track Intercity Rail et qu'aucun autre module Live Track ne les
utilise, vous pouvez les supprimer à la main.

---

## Aidez-le à grandir

Live Track Intercity Rail continue de grandir. Nous ajoutons des compagnies
ferroviaires et des pays à mesure que nous les trouvons, et nous voulons
savoir ce que vous aimeriez ensuite.

### Proposer quelque chose

Votre pays ou votre compagnie ferroviaire manque ? Quelque chose est faux, ou
difficile à comprendre ? Dites-le-nous de la façon la plus simple pour vous :

* [**Remplissez un court formulaire**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=fr.yml)
  en français. Il vous faut un compte GitHub gratuit.
* **Écrivez un e-mail** à
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Aucun compte n'est nécessaire.

Dans les deux cas, il nous aide que vous nous disiez :

* ce que vous aimeriez voir, et où dans le monde ;
* un lien vers l'endroit où les données sont publiées, si vous en connaissez
  un (une page de données ouvertes, un flux public, le site d'un service) : ce
  n'est pas nécessaire, mais cela aide ;
* la langue de votre Home Assistant, si le problème concerne la formulation ou
  une traduction.

Écrivez en anglais ou dans votre propre langue, ce qui est le plus simple pour
vous.

### L'ajouter vous-même, avec notre aide

Si vous souhaitez ajouter quelque chose vous-même, nous vous aiderons à le
faire, de la première question jusqu'à la version terminée. Vous n'avez pas
besoin d'être développeur pour commencer :

* **Une traduction.** Les textes de la boîte de dialogue de configuration sont
  une courte liste de phrases dans un seul fichier texte. Nous vous montrerons
  quel fichier et quelles lignes.
* **Une nouvelle compagnie ferroviaire.** Dites-nous où les données sont
  publiées. Nous pouvons écrire le code ensemble, ou relire le vôtre.
* **Le tester là où vous habitez.** Installez-le, regardez votre partie de la
  carte, et dites-nous ce qui est juste et ce qui ne l'est pas.
* **Une correction de ce README.** Si une étape ne correspondait pas à ce que
  vous avez vu, dites-nous ce que vous avez vu.

[**Dites-nous ce que vous avez en tête**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=fr.yml)
ou écrivez à
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
et nous vous répondrons avec les prochaines étapes.

---

## Langues

Ce README : [English](README.md), [Deutsch](README.de.md), **Français**,
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md),
[Suomi](README.fi.md), [Svenska](README.sv.md),
[Norsk bokmål](README.nb.md), [Gaeilge](README.ga.md). Chaque README traduit
est complet. Aucun n'a encore été lu par une personne de langue maternelle.
Si l'une de ces langues est la vôtre, dites-nous s'il vous plaît si son README
se lit bien : voir [Aidez-le à grandir](#aidez-le-à-grandir).

La boîte de dialogue de configuration et les options sont pour l'instant en
anglais seulement, quelle que soit la langue de votre Home Assistant. Si vous
parlez une autre langue, vous pouvez les traduire vous-même : c'est une courte
liste de phrases dans un seul fichier, et [nous vous aiderons à le
faire](#lajouter-vous-même-avec-notre-aide).

Vous avez trouvé une erreur dans une traduction, ou il vous faut une autre
langue ? Dites-le-nous sur
<https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues>, ou
[traduisez avec notre aide](#lajouter-vous-même-avec-notre-aide).

---

## Crédits et licences

Chaque source en direct est lue à l'exécution, par votre Home Assistant ;
rien d'un flux en direct ne se trouve dans ce dépôt. Chaque train cite sa
source dans son attribut `attribution`. Les conditions de chaque source vous
engagent, en tant que personne qui reçoit ses données.

* **Amtraker** (amtraker.com), qui relaie le suivi des trains d'Amtrak
  (États-Unis) : données sous la
  [Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/),
  attribution requise. L'horaire d'**Amtrak** pour les lignes.
* **Brightline** (États-Unis) : ses flux GTFS et GTFS-Realtime ; Brightline ne
  publie aucune condition.
* **VIA Rail** (Canada) : ses données d'état des trains, pour lesquelles VIA
  ne publie aucune condition ; son horaire sous la Open Government Licence -
  Canada 2.0 ([developer resources](https://www.viarail.ca/en/developer-resources)).
* **Fintraffic / digitraffic.fi** (Finlande) : données sous CC BY 4.0.
* **Transport for NSW** (Australie) : données sous CC BY 4.0
  ([licence des données](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australie) : données sous CC BY 4.0
  ([données ouvertes](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Queensland Rail Travel** (Australie) : les heures que montre sa page
  « Service Updates », lues par votre Home Assistant ; voir
  [la page des droits d'auteur de Queensland Rail](https://www.queenslandrailtravel.com.au/copyright).
  Rien de Queensland Rail Travel n'est livré avec l'intégration.
* **Journey Beyond** (Australie) : ses horaires publiés, recopiés dans
  `data/journey_beyond_timetable.json` ; Journey Beyond ne publie aucune
  condition pour eux.
* **Public Transport Authority of Western Australia** : timetable data
  available free of charge from www.transperth.wa.gov.au
  ([spatial data access](https://www.transperth.wa.gov.au/About/Spatial-Data-Access) ;
  pas CC BY).
* **Renfe** (Espagne) : données sous CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)).
* **Entur** (Norvège) : contains data under the Norwegian licence for Open
  Government data ([NLOD 2.0](https://data.norge.no/nlod/en/2.0)) distributed
  by Entur.
* **Trafikverket** (Suède) : données sous [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Irlande) : données en direct ; Irish Rail ne publie aucune
  condition. Horaire de la
  [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Irlande), CC BY 4.0, fourni tel quel.
* **NS** (Pays-Bas) : données de véhicules et carte des lignes, avec votre
  propre clé, selon les conditions du [NS API portal](https://apiportal.ns.nl/).
  Horaire et retards d'[OVapi](https://gtfs.ovapi.nl/), CC0.
* **Fichiers livrés dans `data/`** : les lignes de Journey Beyond, Queensland
  Rail Travel, Renfe (Spain) et de la Suède, construites à partir
  d'[OpenStreetMap](https://www.openstreetmap.org/copyright), © les
  contributeurs d'OpenStreetMap, sous la
  [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/) ;
  les communes des gares terminus des trajets de Renfe (OpenStreetMap,
  ODbL 1.0) et leurs populations (propriété Wikidata P1082, CC0, sinon
  OpenStreetMap) ; les populations des villes terminus suédoises de
  Statistics Sweden (SCB) et de Trafikverket, toutes deux CC0 1.0 ; les
  populations des villes terminus norvégiennes de Statistics Norway, table
  04859, CC BY 4.0.
* **La carte** est [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, une copie de [ha-map-card](https://github.com/nathan-gs/ha-map-card) de
  nathan-gs, MIT, livrée dans `frontend/`. Ses fonds de carte et leurs crédits
  sont dans son README.

Aucune de ces organisations n'a créé ni approuvé cette intégration.

**Code** : MIT, dans [LICENSE](LICENSE). Les fichiers de `data/` gardent les
licences de leurs sources, listées ci-dessus.

**Pour les développeurs :** chaque compagnie est un module dans
`custom_components/live_track_intercity_rail/operators/`, qui lit un
adaptateur de source dans `sources/` ; les lignes livrées sont reconstruites
avec les scripts de `tools/` (`journey_beyond.py`, `qrt_lines.py`,
`renfe_spain_lines.py`, `sweden_lines.py`). Les tests se lancent avec
`python -m unittest discover -s tests`.

---

## Mots-clés

Home Assistant trains · suivi des trains Home Assistant · carte des trains en
direct · trains grandes lignes · intercités · trains en temps réel ·
GTFS-Realtime · Amtrak · Amtraker · Brightline · VIA Rail · VR · kaukojunat ·
NSW TrainLink · XPT · V/Line · The Ghan · Indian Pacific · Spirit of
Queensland · Transwa · Renfe · AVE · Avlo · Alvia · Rodalies · trenes en
tiempo real · Vy · SJ Nord · tog i sanntid · SJ · Snälltåget · Öresundståg ·
tåg i realtid · Irish Rail · Enterprise · traenacha beo · NS Intercity ·
Arriva · treinen live · Zugverkehr · treni in tempo reale · togtrafik ·
火车实时地图 · geo_location · carte · Lovelace · HACS · Marketplace ·
Live Track · LiveTrack · StrausbergAutomationWorks

---

**Reconnaissance.** StrausbergAutomationWorks reconnaît les peuples autochtones
de toutes les terres et de toutes les eaux de cette carte, partout dans le
monde, et rend hommage à leurs Aînés d'hier et d'aujourd'hui.
