# Live Track Intercity Rail

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · **Español** · [Italiano](README.it.md) · [Dansk](README.da.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · [Gaeilge](README.ga.md) · [Todos los idiomas](#idiomas)

**Trenes interurbanos para Home Assistant, en un solo mapa.** Live Track
Intercity Rail pone en tu mapa de Home Assistant cada tren de los
ferrocarriles interurbanos y de larga distancia que elijas: dónde está, su
número, si va con retraso según la propia regla del ferrocarril, y su próxima
parada. Cada ferrocarril se añade por separado, a partir de sus propios datos
publicados.

> **Live Track Intercity Rail es un módulo de Live Track**, una familia de
> integraciones de Home Assistant que dibujan todo lo que se mueve, y el
> tiempo que atraviesa, en un mapa compartido: aviones, barcos, trenes y
> tiempo. Instálalo solo, o junto a los demás módulos
> ([lista más abajo](#parte-de-live-track-los-demás-módulos)).

> **En crecimiento, y abierto a ideas.** Live Track Intercity Rail cubre hoy
> 33 ferrocarriles en 9 países de 3 continentes, y vamos añadiendo más
> ferrocarriles y países. ¿Falta el tuyo? [Sugiérelo](#ayúdanos-a-hacerlo-crecer),
> o añádelo tú mismo: te ayudaremos a hacerlo.

**Estado: 0.1.3, publicado.** En el catálogo del Marketplace ([instálalo más
abajo](#instalación-paso-a-paso)).

Obra original de StrausbergAutomationWorks. Sin relación con, ni respaldo de,
Amtrak, Amtraker, Brightline, VIA Rail, Fintraffic, VR, Transport for NSW,
NSW TrainLink, Transport Victoria, V/Line, Queensland Rail, Journey Beyond,
la Public Transport Authority of Western Australia, Transwa, Renfe, Rodalies
de Catalunya, Entur, Vy, Go-Ahead Norge, SJ Nord, Trafikverket, SJ, VR
Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen,
Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget,
Värmlandstrafik, Tågab, Inlandsbanan, Irish Rail, la National Transport
Authority (Irlanda), NS, Arriva, Keolis, OVapi, ni ningún otro ferrocarril.

---

## Contenido

1. [Todo lo que hace](#todo-lo-que-hace)
2. [Dónde funciona](#dónde-funciona)
3. [Parte de Live Track: los demás módulos](#parte-de-live-track-los-demás-módulos)
4. [Antes de empezar](#antes-de-empezar)
5. [Instalación, paso a paso](#instalación-paso-a-paso)
6. [Configuración, paso a paso](#configuración-paso-a-paso)
7. [Claves gratuitas que activan más, paso a paso](#claves-gratuitas-que-activan-más-paso-a-paso)
8. [Poner el mapa en un panel](#poner-el-mapa-en-un-panel)
9. [Usarlo en automatizaciones](#usarlo-en-automatizaciones)
10. [Todo lo que hay en el mapa, en detalle](#todo-lo-que-hay-en-el-mapa-en-detalle)
11. [Todas las entidades que crea](#todas-las-entidades-que-crea)
12. [Qué envía y descarga](#qué-envía-y-descarga)
13. [Ayúdanos a hacerlo crecer](#ayúdanos-a-hacerlo-crecer)
14. [Idiomas](#idiomas)
15. [Créditos y licencias](#créditos-y-licencias)
16. [Palabras clave](#palabras-clave)

---

## Todo lo que hace

### En el mapa, sin configurar nada

Añades un **ferrocarril**: eliges un país y luego uno de sus ferrocarriles
interurbanos. Todo lo que sigue aparece entonces para ese ferrocarril. Vuelve
a añadir la integración para cada otro ferrocarril que quieras.

| Qué | Dónde | De dónde |
|---|---|---|
| **Trenes en servicio**: un marcador por tren, con su número de tren o su línea como etiqueta, en los colores propios del ferrocarril, girado en la dirección en que circula | cada ferrocarril | los propios datos publicados de cada ferrocarril |
| **Retraso**: un tren aparece con retraso o con mucho retraso según la propia regla del ferrocarril; donde un ferrocarril no publica ninguna regla, según la distancia que recorre el tren | cada ferrocarril que informa de retrasos | el propio canal de datos de cada ferrocarril |
| **Próxima parada y su hora**: la estación en la que el tren para a continuación, y cuándo se le espera allí | cada ferrocarril cuyo canal u horario lo indica | el propio canal y horario de cada ferrocarril |
| **Trenes que siguen la vía**: entre dos informes un tren avanza por su propia línea a su última velocidad, no en línea recta | cada ferrocarril cuya línea se conoce | el horario de cada ferrocarril, o líneas incluidas con la integración |
| **Trenes a partir del horario**: donde un ferrocarril no publica posiciones, cada tren se sitúa en su línea según sus horas y se marca como estimación | Journey Beyond, Queensland Rail Travel y WA Trains (Australia), SJ Nord (Noruega); Irish Rail con su último retraso | el horario o las horas de cada ferrocarril |
| **Dibujos para algunos trenes**: el Expreso de Papá Noel y una casita de verano (Finlandia), los animales de los trenes de Journey Beyond, un dibujo para cada línea de Queensland Rail Travel | Finlandia, Australia | dibujados para esta integración |
| **Detenido en la frontera**: un tren parado en un paso fronterizo entre Estados Unidos y Canadá muestra "Customs" en lugar de su retraso | los trenes de Amtrak hacia y desde Canadá | las posiciones de Amtrak |
| **Un recuento por ferrocarril**: trenes en servicio | cada ferrocarril | los mismos datos |

### Activado con tu propia clave o cuenta gratuita

| Clave o cuenta gratuita | Qué añade |
|---|---|
| Clave de **Transport for NSW Open Data** | los trenes regionales de NSW TrainLink (Nueva Gales del Sur, Australia) |
| Clave de **Transport Victoria Open Data** | los trenes de larga distancia de V/Line (Victoria, Australia) |
| Clave del **portal de API de NS** | NS Intercity y los trenes regionales de Arriva y Keolis (Países Bajos); una sola clave sirve para los tres |
| Clave de **Trafikverket** | los 15 ferrocarriles suecos; una sola clave sirve para los quince |

Cada una se consigue en unos minutos: [paso a paso más abajo](#claves-gratuitas-que-activan-más-paso-a-paso).
Los otros 13 ferrocarriles no necesitan clave.

---

## Dónde funciona

| Región | Qué obtienes | De dónde | Necesita |
|---|---|---|---|
| **Australia**: todo el país | Journey Beyond: The Ghan, The Ghan Expedition, Indian Pacific, Great Southern, The Overland, solo a partir del horario ([por qué](#journey-beyond-australia)) | Journey Beyond | nada |
| **Australia**: Nueva Gales del Sur | los trenes regionales de NSW TrainLink (XPT y Xplorer), también hacia Queensland, Victoria y el Territorio de la Capital Australiana | Transport for NSW | una clave gratuita |
| **Australia**: Queensland | Queensland Rail Travel: Spirit of Queensland, Spirit of the Outback, Tilt Train, Westlander, Inlander, Kuranda Scenic Railway, Gulflander, a partir de sus horas publicadas ([por qué](#queensland-rail-travel-australia)) | Queensland Rail Travel | nada |
| **Australia**: Victoria | los trenes de larga distancia de V/Line (sus líneas de cercanías están en Live Track Commuter Rail), también hacia Nueva Gales del Sur | Transport Victoria | una clave gratuita |
| **Australia**: Australia Occidental | WA Trains: el Australind, el Prospector, el MerredinLink y el AvonLink, solo a partir del horario ([por qué](#wa-trains-australia-occidental-australia)) | Public Transport Authority of Western Australia | nada |
| **Europa**: Finlandia | los trenes de larga distancia de VR | Fintraffic Digitraffic | nada |
| **Europa**: Irlanda | los trenes InterCity de Irish Rail, y el Enterprise de Dublín a Belfast (Reino Unido) | Irish Rail, National Transport Authority | nada |
| **Europa**: Países Bajos | NS Intercity, y los trenes regionales de Arriva (Arriva, RRReis, Blauwnet) y Keolis (Blauwnet, RRReis); los Sprinter de NS están en Live Track Commuter Rail | NS, OVapi | una clave gratuita |
| **Europa**: Noruega | las líneas F, RE, RX y R de Vy (la F1 también hacia Suecia), la F5 y la R50 de Go-Ahead Norge, la F6, la F7 y de la R60 a la R75 de SJ Nord | Entur | nada |
| **Europa**: España | los trenes AVE, Avlo, Alvia, Avant, Euromed, Intercity, MD y Regional de Renfe, también hacia Francia y Portugal; las líneas regionales R11 a R17 de Rodalies de Catalunya | Renfe | nada |
| **Europa**: Suecia | SJ, VR Snabbtåg, Snälltåget, Öresundståg, Pågatågen, Mälartåg, Västtågen, Krösatågen, Östgötapendeln, Norrtåg, Tåg i Bergslagen, X-Tåget, Värmlandstrafik, Tågab e Inlandsbanan, cada uno como su propio ferrocarril; Öresundståg también hasta Dinamarca | Trafikverket | una clave gratuita |
| **Norteamérica**: Canadá | VIA Rail, todas las rutas | VIA Rail | nada |
| **Norteamérica**: Estados Unidos | Amtrak, todas las rutas, también hacia Canadá | Amtraker | nada |
| **Norteamérica**: Estados Unidos | Brightline (Florida) | Brightline | nada |

¿No está en la lista? [Dínoslo](#ayúdanos-a-hacerlo-crecer). Donde alguien
publique los datos de forma abierta, estudiaremos añadirlo.

⚠ **Un tren es tan bueno como los datos de su ferrocarril.** Algunos
ferrocarriles informan de un tren cada pocos segundos, otros cada pocos
minutos, otros solo cuando pasa por las señales, y otros no publican ninguna
posición. Los límites de cada ferrocarril están en
[Todo lo que hay en el mapa, en detalle](#todo-lo-que-hay-en-el-mapa-en-detalle).

⚠ **No es la información oficial del ferrocarril.** Antes de viajar, consulta
la propia aplicación o web del ferrocarril.

---

## Parte de Live Track: los demás módulos

Live Track es un conjunto de integraciones de Home Assistant, una por cada
tipo de cosa que se mueve, todas dibujadas en la misma tarjeta de mapa. Cada
una funciona sola; juntas forman una sola imagen en vivo. Comparten la tarjeta
de mapa y una biblioteca de Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
así que instalar otra no añade peticiones a una fuente que otra ya lee.

| Módulo | Qué pone en el mapa | Estado |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aviones sobre ti por ADS-B, con rutas e iconos por tipo | publicado |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | buques y barcos por AIS, cerca de ti o en cualquier lugar | publicado |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | trenes de cercanías en Norteamérica, Europa y Australia | publicado |
| **Live Track Intercity Rail** | trenes interurbanos y de larga distancia en Norteamérica, Europa y Australia (este módulo) | publicado |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | aviones y buques de inmigración y de las fuerzas federales del orden, a partir de listas públicas | publicado |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | tiempo, tormentas y riesgos naturales | publicado |
| Live Track Stations | paneles de salidas y avisos de "hora de salir" para cada estación | previsto |
| Live Track Satellites | satélites que pasan sobre ti | previsto |
| Live Track Freight Trains | trenes de mercancías y de obras donde los ferrocarriles los publican | previsto |
| Live Track Transit | autobuses urbanos, tranvías, ferris y metro | previsto |
| Live Track Intercity Buses | autocares interurbanos y regionales | previsto |
| Live Track Commuter Buses | autobuses de cercanías | previsto |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la tarjeta de mapa compartida en la que dibuja cada módulo | publicada, instalada con cada módulo |

Todo es gratuito y de código abierto. Nada se reserva para patrocinadores.

---

## Antes de empezar

* **Home Assistant** 2026.11 o posterior.
* **El Marketplace** (HACS) en tu Home Assistant, para instalarlo y
  actualizarlo de la forma fácil. Sin él puedes copiar los archivos a mano.
* **Acceso a Internet** para Home Assistant: cada tren viene de los propios
  datos publicados de su ferrocarril.
* **Opcional: auto-entities** del Marketplace, para poner los marcadores en
  el mapa (ver [Poner el mapa en un panel](#poner-el-mapa-en-un-panel)).
* Nada que pagar. 13 de los 33 ferrocarriles no necesitan cuenta; los otros
  20 necesitan una clave gratuita propia, y cuatro claves los cubren todos
  ([más arriba](#activado-con-tu-propia-clave-o-cuenta-gratuita)).
* Home Assistant instala por sí solo los paquetes de Python que necesita
  (`saw-livetrack`, `gtfs-realtime-bindings` y `tzdata`) la primera vez que
  se carga la integración.

---

## Instalación, paso a paso

### Desde el Marketplace (recomendado)

1. En Home Assistant, abre **Configuración → Marketplace** (HACS).
2. Busca **Live Track Intercity Rail** y ábrelo.
3. Elige **Descargar** (o **Instalar**).
4. **Reinicia Home Assistant**: **Configuración → Sistema → Reparaciones**
   ofrece el reinicio, o usa **Configuración → Sistema → Reiniciar**.

Si la búsqueda no lo encuentra, añádelo por su enlace: elige **Añadir desde
enlace** (o el menú de tres puntos → **Repositorios personalizados**), escribe
`StrausbergAutomationWorks/LiveTrackIntercityRail`, elige **Integración** si te
pide el tipo y continúa desde el paso 3.

Después, el Marketplace te ofrece cada nueva versión como actualización.

### A mano

1. Descarga el código fuente de la
   [última versión](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/releases/latest).
2. Copia su carpeta `custom_components/live_track_intercity_rail` en la
   carpeta `custom_components` de la carpeta de configuración de tu Home
   Assistant (crea `custom_components` si no existe).
3. Reinicia Home Assistant.

Para actualizar a mano, sustituye la carpeta por la de la nueva versión y
reinicia.

---

## Configuración, paso a paso

1. Abre **Configuración → Dispositivos y servicios**.
2. Elige **Añadir integración** (abajo a la derecha) y busca **Live Track
   Intercity Rail**.
3. **Region** (región): elige el país del ferrocarril. Solo aparecen los
   países con al menos un ferrocarril. Elige **Enviar**.
4. **Railroad** (ferrocarril): elige el ferrocarril. Elige **Enviar**.
5. **API key** (clave de API): solo para NSW TrainLink, V/Line, los tres
   ferrocarriles neerlandeses y los quince ferrocarriles suecos. Pega tu clave
   ([cómo conseguir una](#claves-gratuitas-que-activan-más-paso-a-paso)) y
   elige **Enviar**. Los demás ferrocarriles se saltan este paso.

Eso es todo. Los trenes aparecen en un minuto o dos. Donde las líneas de un
ferrocarril vienen de su horario, los trenes empiezan a seguir sus líneas en
cuanto se ha descargado el horario, lo que la primera vez puede tardar unos
minutos. Para seguir otro ferrocarril, vuelve a añadir la integración. El
mismo ferrocarril dos veces se rechaza.

### Cambiar lo que muestra: las opciones

Abre **Configuración → Dispositivos y servicios → Live Track Intercity Rail →
Configurar** (la rueda dentada) en el ferrocarril que quieras cambiar. Hay una
opción:

| Opción | Qué hace | Por defecto |
|---|---|---|
| **Poll interval** (intervalo de consulta) | cada cuánto se lee la fuente del ferrocarril, de 15 a 600 segundos. Un intervalo más corto que la propia actualización de la fuente no muestra nada más | según el ferrocarril: 15 segundos para Renfe (Spain) y los tres ferrocarriles neerlandeses; 60 segundos para Brightline, NSW TrainLink, Irish Rail y SJ Nord; 30 segundos para los demás |

---

## Claves gratuitas que activan más, paso a paso

Veinte ferrocarriles piden a cada usuario su propia clave, de cuatro
proveedores. Todas estas claves son gratuitas, y cada persona que instala Live
Track Intercity Rail consigue la suya. Pegas la clave cuando el diálogo de
configuración te la pide ([paso 5 más arriba](#configuración-paso-a-paso)).
Solo se pide la clave: ni contraseña ni secreto. La clave se guarda en Home
Assistant con la integración, se envía solo a su propio proveedor y nunca se
escribe en el registro. Si el proveedor la rechaza durante diez minutos, Home
Assistant te pide una nueva.

### Transport for NSW (NSW TrainLink, Nueva Gales del Sur, Australia)

1. Abre <https://opendata.transport.nsw.gov.au/>, elige **Register**, crea
   una cuenta e inicia sesión.
2. Elige el icono de tu perfil y luego **API Tokens**.
3. Escribe un nombre para la clave y elige **CREATE API TOKEN**. Copia la
   clave en ese momento: el sitio la muestra una sola vez.
4. Pégala en **API key** cuando añadas NSW TrainLink. Pega solo la clave: Live
   Track Intercity Rail añade la palabra `apikey` por sí solo.

### Transport Victoria (V/Line, Victoria, Australia)

1. Abre <https://opendata.transport.vic.gov.au/>, elige **Login** y luego
   **Sign up**.
2. Escribe tus datos y elige **Create Account**. Escribe el código del correo
   que recibes y elige **Confirm**.
3. El portal pide una aplicación de autenticación en tu teléfono: escanea con
   ella el código QR, escribe el código de la aplicación y elige **Confirm**.
   Después inicia sesión con tu correo, tu contraseña y el código de la
   aplicación.
4. Elige **My Account** → **Profile** → **API tokens**. Tu clave ya está ahí.
   Pégala en **API key** cuando añadas V/Line.

### NS (NS, Arriva y Keolis, Países Bajos)

1. Abre <https://apiportal.ns.nl/>, elige **Inloggen** (iniciar sesión) y
   luego **Externe bezoeker** (visitante externo).
2. Rellena el formulario y envíalo. Un correo confirma el registro. Las API
   pueden tardar hasta 5 minutos en aparecer en el portal.
3. Abre la página de la **Virtual Train API** (las posiciones de los trenes
   de NS). En **Related Products**, abre su producto, ponle un nombre a tu
   suscripción y elige **Subscribe**.
4. Cuando NS apruebe la suscripción, tu clave está en tu página de perfil.
   Pégala en **API key** cuando añadas NS, Arriva o Keolis. Una sola clave
   sirve para los tres.

### Trafikverket (los 15 ferrocarriles suecos)

1. Abre <https://data.trafikverket.se/oauth2/Account/register>.
2. Rellena **Email**, **Displayname** (nombre visible), **Password**
   (contraseña) y **Confirm password**, marca **Accept license and
   Agreement** y elige **Register**.
3. Abre <https://data.trafikverket.se/get-started> y elige **Create key**,
   bajo **Create a key**. Inicia sesión con la cuenta que creaste y crea la
   clave.
4. Pégala en **API key** cuando añadas un ferrocarril sueco. Una sola clave
   sirve para los quince.

---

## Poner el mapa en un panel

El mapa es [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la tarjeta en la que dibuja cada módulo de Live Track. **Se instala con Live
Track Intercity Rail**: nada que descargar, nada que copiar, ningún recurso
que añadir.

1. Abre un panel, elige el lápiz (**Editar panel de control**) y luego
   **Añadir tarjeta**.
2. Baja hasta el final y elige **Manual**.
3. Pega esto y elige **Guardar**:

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

Esta forma necesita [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
del Marketplace. Con otros módulos de Live Track instalados, añade un filtro
`- domain: geo_location` más por cada una de sus fuentes
(`live_track_commuter_rail`, `live_track_aircraft`, etc.).

**Sin auto-entities:** LiveTrackMapCard puede elegir por sí misma qué muestra,
con `entity_filter`. Pega esto en su lugar; no hace falta instalar nada más:

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

Los otros módulos de Live Track van en `entity_filter` del mismo modo: una
regla `- domain: geo_location` más por cada fuente.

**En el mapa:**

* Cada tren es un marcador en los colores de su ferrocarril, con su número de
  tren o su línea como etiqueta. Los trenes de Amtrak son estrellas, los de
  VIA Rail llevan la hoja de arce, los InterCity de Irish Rail son tréboles, y
  algunos trenes son dibujos (cada ferrocarril más abajo dice cuáles).
* En la mayoría de los ferrocarriles los colores se intercambian con el
  sentido: de una forma al salir de la ciudad principal, de la otra al ir
  hacia ella.
* Una flecha muestra la dirección en que circula el tren. Un tren parado
  conserva su última dirección. Los dibujos se mantienen derechos y no tienen
  flecha.
* **Señala** un tren para ver su ferrocarril, número, línea y recorrido.
  **Haz clic** en él para ver todos sus detalles, incluidos su próxima parada
  y su retraso.

Si los recursos de tus paneles se definen en YAML
(`lovelace: resource_mode: yaml`), no se puede registrar nada por ti: un aviso
en **Reparaciones** te da entonces las líneas exactas que añadir a
`configuration.yaml`. Se parecen a esto, con la propia dirección de la
integración en lugar de los marcadores de posición:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_intercity_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Cada módulo de Live Track lleva una copia de la tarjeta y la registra cuando
Home Assistant arranca. Entre todos mantienen exactamente una fila en
**Configuración → Paneles de control → Recursos**: la versión más nueva de la
tarjeta que lleve cualquiera de ellos, nunca una más antigua. Una tarjeta que
hayas instalado tú mismo desde el Marketplace se deja en paz. Cuando quitas el
último ferrocarril de este módulo, la fila pasa a otro módulo de Live Track, o
se quita si no queda ninguno. Si se borran los archivos de la integración
mientras sus ferrocarriles siguen configurados, y no hay otro módulo de Live
Track instalado, quita tú mismo la fila en **Configuración → Paneles de
control → Recursos**.

**Para instalar la tarjeta a mano en su lugar**, sigue los pasos del
[README de la tarjeta](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).
Una fila que hayas creado tú, para una copia en `/local/` o en cualquier otra
dirección, nunca se cambia ni se elimina. Mientras cargue la tarjeta, todos los
módulos Live Track le dejan la tarjeta, incluso cuando un módulo trae una
versión más nueva, y nada en **Reparaciones** lo indica. Para volver a la copia
del módulo, elimina tu fila en **Configuración → Paneles de control → Recursos**
y reinicia Home Assistant. Si borras el archivo de tu copia, elimina también su
fila: mientras quede una fila cuyo archivo ya no existe, el módulo no añade
ninguna fila propia.

Cualquier otra tarjeta de mapa que muestre entidades `geo_location` también
muestra los trenes, como marcadores simples.

---

## Usarlo en automatizaciones

Todo es una entidad normal de Home Assistant, así que el editor de
automatizaciones trabaja con ella, sin código.

**Una notificación en el teléfono cuando se detienen los datos de tu
ferrocarril** (los trenes salen entonces del mapa):

1. **Configuración → Automatizaciones y escenas → Crear automatización →
   Crear nueva automatización**.
2. **Cuando**: **Añadir disparador** → **Entidad** → **El estado cambió**.
   Elige la entidad **Trains in service** (trenes en servicio) del
   ferrocarril, y en **A (opcional)** elige **No disponible**.
3. **Entonces hacer**: **Añadir acción**, busca la acción de notificación de
   tu teléfono (lleva el nombre de tu teléfono) y escribe un mensaje, por
   ejemplo:

   ```text
   No hay trenes interurbanos en el mapa: los datos del ferrocarril se han detenido
   ```

4. **Guardar**.

**Otras ideas:** una luz que se enciende cuando un tren de Amtrak está a menos
de 2 km (1,2 millas) de tu casa en Estados Unidos, a partir de la distancia de
los marcadores; un recuento en el panel de los trenes que VR hace circular en
Finlandia a lo largo del día; un mensaje cuando sale el primer tren del día de
Queensland Rail Travel (Australia), a partir de **Trains in service** al
superar 0.

---

## Todo lo que hay en el mapa, en detalle

### Trenes

Cada tren es un marcador. Su estado es su distancia a tu casa, en kilómetros.
El marcador aparece cuando el ferrocarril informa del tren, o cuando su
horario dice que está circulando, y se quita cuando el tren sale de los datos
del ferrocarril o termina su recorrido.

* **Entre dos informes** un tren avanza por su propia línea hacia su próxima
  parada: a la velocidad que informa el ferrocarril o, donde no informa de
  ninguna, a la velocidad entre sus dos últimos informes. Nunca pasa de su
  próxima parada, y deja de moverse 30 minutos después del último informe.
  Un tren en una línea conocida se dibuja sobre la línea; el propio informe
  del ferrocarril se guarda a su lado.
* **Si fallan los datos de un ferrocarril**, sus trenes siguen moviéndose con
  su último informe bueno durante hasta 10 minutos. Después quedan no
  disponibles y salen del mapa hasta que vuelven los datos.
* **Con retraso y con mucho retraso**: donde el ferrocarril publica su propia
  regla para un tren con retraso, la integración la usa. Donde no publica
  ninguna, un tren va con retraso según la distancia que recorre, con los
  umbrales de Amtrak Status Maps (asm.transitdocs.com). Cada ferrocarril más
  abajo dice cuál.

En cada tren: `marker_label`, `train`, `line_name`, `observed_at` (cuándo era
cierto su informe), `course_deg` (mientras se mueve), `next_stop` y
`arrival_estimated_at` (donde se conocen), `delay_min`, `late_threshold_min` y
`very_late_threshold_min`, `speed_kmh` (donde el ferrocarril la informa),
`attribution` y, entre dos informes, `previous_latitude`,
`previous_longitude`, `previous_observed_at` y `segment_duration_s`. Un tren
movido por su línea lleva `position_source: estimated`, con el informe del
ferrocarril en `fix_latitude` y `fix_longitude`.

### Journey Beyond (Australia)

⚠ **Journey Beyond no publica posiciones.** Cada tren se dibuja a partir de su
horario publicado, transcrito en un archivo que se incluye con la integración
(salidas hasta el 29 de diciembre de 2027), así que no se descarga nada. Cada
tren se sitúa en su línea según sus horas, marcado como estimación, sin
retraso: un tren retrasado o cancelado se dibuja igualmente a su hora. Cada
servicio es su propio dibujo (el camello con su jinete, un pájaro, un canguro,
un emú), en sus colores a la ida e intercambiados a la vuelta, sin etiqueta:
señálalo para ver el tren y su recorrido.

### NSW TrainLink (Nueva Gales del Sur, Australia)

Del canal de NSW TrainLink de Transport for NSW, con tu propia clave, una
nueva posición más o menos cada minuto. La etiqueta es el número de tren.
Naranja NSW con un anillo blanco al salir de Sídney, intercambiados al ir
hacia ella. El canal no tiene velocidad, así que un tren avanza por su línea a
la velocidad entre sus dos últimas posiciones. Con retraso desde 11 minutos
(NSW TrainLink considera puntual un tren dentro de 10 minutos), con mucho
retraso desde 30.

### Queensland Rail Travel (Australia)

⚠ **Queensland Rail Travel no publica posiciones.** Tu Home Assistant lee las
horas que muestra la página Service Updates de Queensland Rail Travel: la
lista de los trenes de hoy como mucho cada 5 minutos, y las horas de cada tren
como mucho cada 5 minutos desde 30 minutos antes de su salida hasta 15
minutos después de su llegada. Cada tren se sitúa en su línea según esas
horas y se marca como estimación. Cada línea es su propio dibujo, en sus
colores al salir de Brisbane e intercambiados al ir hacia ella, con el número
de tren en una etiqueta al lado. No se muestra retraso ni mucho retraso.

### V/Line (Victoria, Australia)

Del canal de V/Line de Transport Victoria, con tu propia clave: las líneas de
larga distancia a Albury, Ararat, Bairnsdale, Echuca, Maryborough,
Shepparton, Swan Hill y Warrnambool. La etiqueta es el número de tren. Morado
V/Line con un anillo amarillo al salir de Melbourne, intercambiados al ir
hacia ella. El canal no tiene velocidad, así que un tren avanza a la velocidad
entre sus dos últimas posiciones; tras 10 minutos sin nueva posición se
cronometra hasta su próxima parada. Con retraso desde 11 minutos en las
líneas largas y 6 en las cortas (la propia lista de V/Line), con mucho retraso
desde 30.

### WA Trains (Australia Occidental, Australia)

⚠ **No se publican posiciones en vivo.** Cada tren se dibuja a partir del
horario de la Public Transport Authority of Western Australia: situado a lo
largo de su línea según sus horas previstas, marcado como estimación, sin
retraso. El horario se comprueba una vez al día. La etiqueta son las tres
primeras letras de la ruta: AUS (Australind, morado), PRO (Prospector,
naranja), MER (MerredinLink, verde) y AVO (AvonLink, verde), igual en ambos
sentidos.

### VR (Finlandia)

De Digitraffic de Fintraffic, una nueva posición más o menos cada 30
segundos. La etiqueta es el tipo y el número del tren, como lo escribe VR
(`IC 23`). Verde VR con un anillo oscuro al salir de Helsinki, intercambiados
al ir hacia ella. Los datos no tienen dirección, así que la flecha sigue la
línea. Con retraso desde 6 minutos (VR considera que un tren va con retraso
cuando lleva más de cinco minutos), con mucho retraso desde 12.

* **El Expreso de Papá Noel**, del primer domingo de Adviento al 6 de enero:
  un muñeco de nieve hacia el norte, un reno a la vuelta, sin número. A partir
  de 12 minutos de retraso la figura se da la vuelta cada pocos segundos.
* **La casita de verano**, de la víspera de San Juan al 31 de julio: cada tren
  de larga distancia de VR se dibuja como una casita, con su número al lado.

### Irish Rail (Irlanda)

Del servicio en vivo de Irish Rail y del horario de la National Transport
Authority. ⚠ Irish Rail informa de un tren solo cuando pasa por puntos de
señalización separados por unos minutos, así que cada tren se dibuja a partir
de su horario y su último retraso, movido a lo largo de su ruta. La etiqueta
es el número de tren sin su letra (A700 muestra 700). Un tren InterCity es un
trébol verde con contorno y número naranjas al salir de Dublín, con los
colores intercambiados al ir hacia ella. El Enterprise es un disco plateado
con un anillo exterior rojo, una banda magenta y un número magenta; hacia
Dublín el disco es magenta. Con retraso desde 10 minutos (la regla de la
National Transport Authority), con mucho retraso desde 20.

### NS, Arriva y Keolis (Países Bajos)

De los datos de vehículos de NS, con tu propia clave, una nueva posición más o
menos cada 10 segundos. Este canal informa de la propia velocidad y dirección
de un tren, y ambas se transmiten. La próxima parada y el retraso vienen del
horario de OVapi; la vía es el propio mapa de NS de sus líneas, descargado una
vez al día. La etiqueta es el número de tren. Los trenes de NS son amarillos
con un anillo azul NS; los de Arriva y Keolis tienen por ahora el aspecto
propio de la tarjeta de mapa. Con retraso desde 3 minutos (la propia
definición de NS), con mucho retraso desde 10.

### Vy, Go-Ahead Norge y SJ Nord (Noruega)

De Entur, cada ferrocarril con su propia entrada. La etiqueta es el código de
línea (F4, RE10, R50). El color propio de la línea con un anillo blanco al
salir de Oslo S (en un viaje que no llega a Oslo S, su ciudad terminal más
grande), intercambiados al ir hacia ella. Entur no publica velocidad ni
dirección, así que un tren avanza a la velocidad entre sus dos últimas
posiciones, y la flecha sigue su línea. En los largos túneles de Oslo, un tren
cuyas posiciones se detienen se mueve por su línea hasta que vuelven. ⚠ **SJ
Nord no publica posiciones:** cada uno de sus trenes se sitúa en su línea
según sus horas previstas. Con retraso desde 4 minutos, y desde 6 en las
líneas F y las líneas a Gotemburgo (Suecia), la regla de Bane NOR y Vy; con
mucho retraso al doble.

### Renfe (Spain) y Renfe Regionals (Catalunya, España)

**Renfe (Spain)** lee el canal de larga distancia de Renfe, una nueva posición
más o menos cada 15 segundos. La etiqueta es el número de tren; el servicio
(AVE, Avlo, Alvia, etc.) está en el recuadro al señalar. AVE azul marino, Avlo
turquesa, cualquier otro servicio morado Renfe, cada uno relleno al salir de
Madrid (en un viaje que no llega a Madrid, su ciudad terminal más grande) e
intercambiado al ir hacia ella. Renfe no publica trazados de rutas, así que
las líneas se construyen a partir de OpenStreetMap y se incluyen con la
integración. Renfe no publica ninguna regla para un tren con retraso, así que
un tren va con retraso según la longitud de su viaje: desde 10 minutos hasta
400 km (250 millas), 15 hasta 560 km (350 millas), 20 hasta 725 km (450
millas), 25 hasta 885 km (550 millas), 30 más allá; con mucho retraso al
doble.

**Renfe Regionals (Catalunya)** dibuja las líneas regionales R11 a R17 de
Rodalies de Catalunya. La etiqueta es el número de tren, en el color propio de
la línea, relleno al salir de Barcelona e intercambiado al ir hacia ella.
Fuera de Barcelona una posición es la última estación por la que pasó un tren,
así que el tren se cronometra entre estaciones con el horario y su retraso.
Con retraso desde 10 minutos, con mucho retraso desde 20, según la longitud de
la línea más larga. Con los dos ferrocarriles de Renfe configurados, cada tren
se dibuja una sola vez.

### Los ferrocarriles suecos (Suecia)

De Trafikverket, con tu propia clave (una clave para los quince). La etiqueta
es el número de tren del billete; la marca, el número y las estaciones de
origen y destino están en el recuadro al señalar. Cada marca tiene sus propios
colores, intercambiados al ir hacia Stockholm C (en un viaje que no llega a
Stockholm C, su ciudad terminal más grande). Trafikverket da una velocidad en
cerca de la mitad de sus posiciones; los demás trenes avanzan a la velocidad
entre sus dos últimas posiciones. Suecia no publica trazados de rutas, así que
las líneas se construyen a partir de OpenStreetMap y se incluyen con la
integración. Con retraso desde 6 minutos (Trafikverket considera puntual un
tren hasta 5 minutos y 59 segundos), con mucho retraso desde 12.

### VIA Rail (Canadá)

De los propios datos de estado de los trenes de VIA Rail. Cada tren es un
disco con la hoja de arce y una banda en el color de su grupo de rutas
(Atlantic, Western, Ontario y Quebec, Prince Rupert, Churchill, Sudbury a
White River, Montréal scenic), con el número de tren en una etiqueta derecha.
Los números impares tienen un disco amarillo, los pares un disco del color de
la banda. Un tren sin nueva posición avanza hacia su próxima parada para
llegar a la hora que estima VIA. VIA no publica ninguna regla para un tren con
retraso, así que un tren va con retraso desde 10 minutos en el corredor de
Québec City a Windsor y desde 60 en los demás (los valores de Amtrak Status
Maps para VIA), con mucho retraso al doble.

### Amtrak (Estados Unidos)

Amtrak no publica datos abiertos en vivo. Amtraker retransmite el propio
seguimiento de trenes de Amtrak, con una nueva posición cada 3 a 5 minutos, y
la integración mueve cada tren por su línea a la velocidad que informa Amtrak.
Cada tren es una estrella con su número encima, en los colores de su ruta (las
rutas del Noreste, Cascades, Pacific Surfliner, Acela y más), o si no la
estrella de la bandera. El Maple Leaf (Nueva York a Toronto) cambia despacio
entre la estrella de Amtrak y el distintivo de VIA. Un tren parado en la
frontera en Lacolle, Rouses Point o Niagara Falls muestra "Customs" en lugar
de su retraso. Con retraso desde 16 minutos (Amtrak considera puntual un tren
dentro de 15 minutos), con mucho retraso desde 30. El mismo número de tren
puede circular en dos o tres días a la vez, así que cada recorrido es su
propio marcador.

### Brightline (Estados Unidos)

Del propio canal de Brightline, una nueva posición más o menos cada 60
segundos. La etiqueta es el número de viaje, en negro con contorno blanco,
sobre un disco del color del destino del tren, con un anillo negro. Una
posición de más de 5 minutos no se usa. El canal no tiene velocidad, así que
un tren avanza a la velocidad entre sus dos últimas posiciones. Brightline no
publica ninguna regla para un tren con retraso, así que un tren va con retraso
desde 10 minutos, con mucho retraso desde 20, según la longitud de su viaje.

---

## Todas las entidades que crea

Por cada ferrocarril:

| Entidad | Qué es |
|---|---|
| `sensor.<ferrocarril>_trains_in_service` | **Trains in service** (trenes en servicio): cuántos trenes tiene ahora el ferrocarril circulando en el mapa. Para Amtrak: `sensor.amtrak_trains_in_service` |
| `geo_location.<ferrocarril>_train_…` | uno por tren (`geo_location.amtrak_train_5_17`); aparece y desaparece con el tren. Cada uno lleva `source: live_track_intercity_rail`, y su estado es su distancia a tu casa en kilómetros |

El ID de entidad de un marcador viene del ferrocarril y del recorrido, nunca
de su etiqueta: `geo_location.amtrak_train_5_17` es el tren 5 de Amtrak que
salió el día 17 del mes, así que un tren conserva el mismo ID de entidad
durante todo su recorrido, y otro recorrido con el mismo número recibe el
suyo. El marcador se quita cuando el recorrido sale de los datos del
ferrocarril o termina. Los marcadores no tienen ID único, como ningún
marcador de mapa de Live Track, así que no se pueden renombrar, ocultar ni
asignar a un área en la interfaz. El sensor tiene un ID único y se puede
renombrar.

Los atributos que cambian en cada consulta, las posiciones y horas de los
marcadores, se guardan en el historial de Home Assistant, como para cualquier
entidad. El sensor no tiene atributos, así que guardarlo cuesta poco, y es el
registro de cuántos trenes circularon en un día. Para dejar los marcadores
fuera del historial, añade esto a `configuration.yaml` y reinicia:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_train_*
```

Si tu `configuration.yaml` ya tiene una sección `recorder:`, añade solo el
patrón `geo_location.*_train_*`, bajo `exclude:` y `entity_globs:`. El patrón
solo coincide con los marcadores de trenes de este módulo. Una tarjeta de mapa
configurada para dibujar el historial ya no tiene entonces rastro que dibujar.

---

## Qué envía y descarga

**Sobre tu ubicación.** Nada. La posición de tu casa se usa solo dentro de tu
Home Assistant, para dar la distancia de cada tren. Tu clave, donde un
ferrocarril la necesita, se envía solo al proveedor de ese ferrocarril. Nada
más sobre ti se envía a ninguna parte. Cada servicio ve tu dirección de
Internet, como cualquier sitio web.

**Cuánto.** Cada fuente en vivo se lee en cada consulta, por defecto con el
propio intervalo del ferrocarril (**Poll interval**, de 15 a 600 segundos), o
con menos frecuencia donde la tabla lo indica. Donde varios módulos de Live
Track o ferrocarriles leen la misma fuente, un cliente compartido la lee una
vez para todos. Medido el 19 de noviembre de 2026, de 02:44 a 02:49 UTC:

| Ferrocarril | Datos en vivo, una lectura | Horario y líneas |
|---|---|---|
| Journey Beyond (Australia) | nada: no se descarga nada | nada: su horario y sus líneas se incluyen con la integración |
| NSW TrainLink (Australia) | 124 KB de dos canales, como mucho una vez cada 55 segundos | 40 MB, cuando cambia, comprobado a diario |
| Queensland Rail Travel (Australia) | la lista, 5,5 KB, cada 5 minutos; las horas de cada tren en circulación, de 6 a 8 KB, cada 5 minutos | nada: sus líneas se incluyen con la integración |
| V/Line (Australia) | 14 KB de dos canales | 58 MB (la parte de V/Line del archivo de 311 MB de Transport Victoria, leída sola), cuando cambia, comprobado a diario |
| WA Trains (Australia) | nada: no existe canal en vivo | 28 MB, cuando cambia, comprobado a diario |
| VR (Finlandia) | 1,4 KB comprimidos para las posiciones; los trenes del día, 0,5 MB comprimidos la primera vez, después solo los cambios, una vez por minuto | 3,1 MB, cada día |
| Irish Rail (Irlanda) | 0,2 KB, como mucho una vez cada 55 segundos | 6,6 MB, cuando cambia, comprobado a diario; la lista de estaciones, 46 KB, una vez por semana |
| NS, Arriva, Keolis (Países Bajos) | 1,5 KB, como mucho una vez cada 9 segundos; retrasos de OVapi, 5,3 MB, cada 5 minutos y solo cuando cambian | el horario de OVapi, 267 MB, como mucho una vez por semana y solo cuando cambia; el mapa de vías de NS, 1,3 MB, cada día |
| Vy, Go-Ahead Norge, SJ Nord (Noruega) | Vy 510 KB de dos canales, Go-Ahead Norge 7 KB, SJ Nord 0,7 KB una vez por minuto | Vy 67 MB, Go-Ahead Norge 20 MB, SJ Nord 26 MB, cuando cambian, comprobado a diario |
| Renfe (Spain) | 2,1 KB de dos canales | 0,7 MB, cada día; sus líneas se incluyen con la integración |
| Renfe Regionals (Catalunya, España) | 0,2 KB de dos canales que llevan todas las redes locales de Renfe | 16 MB, cada día |
| Los ferrocarriles suecos (Suecia) | 474 KB la primera vez, después de 5 a 9 KB de cambios | nada; la lista de estaciones, 0,15 MB, cada día; las líneas se incluyen con la integración |
| VIA Rail (Canadá) | 353 KB, enviados comprimidos en 33 KB | 1,0 MB, una vez por semana |
| Amtrak (Estados Unidos) | 1,2 MB, enviados comprimidos en 113 KB | 18,6 MB, una vez por semana |
| Brightline (Estados Unidos) | 1,3 KB de dos canales | 29 KB, una vez por semana |

⚠ Cuando se midió esto era de día en Australia, de tarde en Norteamérica y de
noche en Europa. Un canal en vivo es más pequeño de noche: de día los canales
europeos son más grandes de lo que muestra la tabla.

**Tras un error.** Los trenes siguen moviéndose con los últimos datos buenos
durante hasta 10 minutos; después se marcan como no disponibles hasta que la
fuente responde. Un horario que no se puede descargar se vuelve a intentar más
tarde, y la copia que tienes sigue en uso. Si un proveedor rechaza tu clave
durante diez minutos, Home Assistant te pide una nueva.

**En disco.** Los horarios y los trazados de rutas se guardan en la carpeta
`.storage` de Home Assistant con nombres que empiezan por `saw_`, compartidos
con los demás módulos de Live Track que leen el mismo ferrocarril. Si quitas
Live Track Intercity Rail y ningún otro módulo de Live Track los usa, puedes
borrarlos a mano.

---

## Ayúdanos a hacerlo crecer

Live Track Intercity Rail sigue creciendo. Añadimos ferrocarriles y países a
medida que los encontramos, y queremos saber qué te gustaría a continuación.

### Sugerir algo

¿Falta tu país o tu ferrocarril? ¿Hay algo mal, o difícil de entender?
Cuéntanoslo de la forma que te resulte más fácil:

* [**Rellena un formulario corto**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=es.yml)
  en español. Necesitas una cuenta gratuita de GitHub.
* **Escribe un correo** a
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  No hace falta cuenta.

En cualquier caso, ayuda que nos digas:

* qué te gustaría ver, y en qué parte del mundo;
* un enlace a donde se publican los datos, si conoces uno (una página de
  datos abiertos, un canal público, la web de un servicio): no es necesario,
  pero ayuda;
* el idioma de tu Home Assistant, si el problema es la redacción o una
  traducción.

Escribe en inglés o en tu propio idioma, lo que te resulte más fácil.

### Añadirlo tú mismo, con nuestra ayuda

Si quieres añadir algo tú mismo, te ayudaremos a hacerlo, desde la primera
pregunta hasta la versión terminada. No necesitas ser desarrollador para
empezar:

* **Una traducción.** Los textos del diálogo de configuración son una lista
  corta de frases en un archivo de texto. Te mostraremos qué archivo y qué
  líneas.
* **Un nuevo ferrocarril.** Dinos dónde se publican los datos. Podemos
  escribir el código juntos, o revisar el tuyo.
* **Probarlo donde vives.** Instálalo, mira tu parte del mapa y dinos qué está
  bien y qué no.
* **Una corrección de este README.** Si un paso no coincidía con lo que
  viste, dinos lo que viste.

[**Cuéntanos qué tienes en mente**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=es.yml)
o escribe a
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
y te responderemos con los siguientes pasos.

---

## Idiomas

Este README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), **Español**, [Italiano](README.it.md),
[Dansk](README.da.md), [Suomi](README.fi.md), [Svenska](README.sv.md),
[Norsk bokmål](README.nb.md), [Gaeilge](README.ga.md). Cada README traducido
está completo. Ninguno ha sido leído todavía por un hablante nativo. Si uno de
estos idiomas es el tuyo, dinos si su README se lee bien: ver
[Ayúdanos a hacerlo crecer](#ayúdanos-a-hacerlo-crecer).

El diálogo de configuración y las opciones están por ahora solo en inglés, sea
cual sea el idioma de tu Home Assistant. Si hablas otro idioma, puedes
traducirlos tú mismo: es una lista corta de frases en un solo archivo, y [te
ayudaremos a hacerlo](#añadirlo-tú-mismo-con-nuestra-ayuda).

¿Has encontrado un error en una traducción, o necesitas otro idioma? Dínoslo
en <https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues>,
o [tradúcelo con nuestra ayuda](#añadirlo-tú-mismo-con-nuestra-ayuda).

---

## Créditos y licencias

Cada fuente en vivo se lee en tiempo de ejecución, por tu Home Assistant;
nada de un canal en vivo está en este repositorio. Cada tren cita su fuente en
su atributo `attribution`. Las condiciones de cada fuente te obligan a ti,
como persona que recibe sus datos.

* **Amtraker** (amtraker.com), que retransmite el seguimiento de trenes de
  Amtrak (Estados Unidos): datos bajo la
  [Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/),
  atribución obligatoria. El propio horario de **Amtrak** para los trazados de
  rutas.
* **Brightline** (Estados Unidos): sus canales GTFS y GTFS-Realtime;
  Brightline no publica condiciones.
* **VIA Rail** (Canadá): sus datos de estado de los trenes, para los que VIA
  no publica condiciones; su horario bajo la Open Government Licence - Canada
  2.0 ([developer resources](https://www.viarail.ca/en/developer-resources)).
* **Fintraffic / digitraffic.fi** (Finlandia): datos bajo CC BY 4.0.
* **Transport for NSW** (Australia): datos bajo CC BY 4.0
  ([licencia de datos](https://opendata.transport.nsw.gov.au/datalicence)).
* **Transport Victoria** (Australia): datos bajo CC BY 4.0
  ([datos abiertos](https://discover.data.vic.gov.au/dataset/gtfs-realtime)).
* **Queensland Rail Travel** (Australia): las horas que muestra su página
  Service Updates, leídas por tu Home Assistant; ver la
  [página de copyright de Queensland Rail](https://www.queenslandrailtravel.com.au/copyright).
  Nada de Queensland Rail Travel se incluye con la integración.
* **Journey Beyond** (Australia): sus horarios publicados, transcritos en
  `data/journey_beyond_timetable.json`; Journey Beyond no publica condiciones
  para ellos.
* **Public Transport Authority of Western Australia**: datos de horarios
  disponibles gratuitamente en www.transperth.wa.gov.au
  ([spatial data access](https://www.transperth.wa.gov.au/About/Spatial-Data-Access);
  no es CC BY).
* **Renfe** (España): datos bajo CC BY 4.0 ([data.renfe.com](https://data.renfe.com/)).
* **Entur** (Noruega): contiene datos bajo la licencia noruega de datos
  públicos abiertos ([NLOD 2.0](https://data.norge.no/nlod/en/2.0))
  distribuidos por Entur.
* **Trafikverket** (Suecia): datos bajo [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
* **Irish Rail** (Irlanda): datos en vivo; Irish Rail no publica condiciones.
  Horario de la [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)
  (Irlanda), CC BY 4.0, proporcionado tal cual.
* **NS** (Países Bajos): datos de vehículos y mapa de vías, con tu propia
  clave, bajo las condiciones del [portal de API de NS](https://apiportal.ns.nl/).
  Horario y retrasos de [OVapi](https://gtfs.ovapi.nl/), CC0.
* **Archivos incluidos en `data/`**: trazados de rutas para Journey Beyond,
  Queensland Rail Travel, Renfe (Spain) y Suecia, construidos a partir de
  [OpenStreetMap](https://www.openstreetmap.org/copyright), © colaboradores de
  OpenStreetMap, bajo la
  [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/);
  los municipios de las estaciones terminales de los viajes de Renfe
  (OpenStreetMap, ODbL 1.0) y sus poblaciones (propiedad P1082 de Wikidata,
  CC0, o si no OpenStreetMap); poblaciones de las ciudades terminales suecas de
  Statistics Sweden (SCB) y Trafikverket, ambas CC0 1.0; poblaciones de las
  ciudades terminales noruegas de Statistics Norway, tabla 04859, CC BY 4.0.
* **La tarjeta de mapa** es [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, una copia de [ha-map-card](https://github.com/nathan-gs/ha-map-card) de
  nathan-gs, MIT, incluida en `frontend/`. Sus teselas de mapa y sus créditos
  están en su README.

Ninguna de estas organizaciones ha hecho ni respaldado esta integración.

**Código**: MIT, en [LICENSE](LICENSE). Los archivos de `data/` conservan las
licencias de sus fuentes, indicadas arriba.

**Para desarrolladores:** cada ferrocarril es un módulo en
`custom_components/live_track_intercity_rail/operators/`, que lee un
adaptador de fuente en `sources/`; los trazados de rutas incluidos se
reconstruyen con los scripts de `tools/` (`journey_beyond.py`,
`qrt_lines.py`, `renfe_spain_lines.py`, `sweden_lines.py`). Las pruebas se
ejecutan con `python -m unittest discover -s tests`.

---

## Palabras clave

trenes Home Assistant · seguimiento de trenes Home Assistant · mapa de trenes
en vivo · trenes interurbanos · trenes de larga distancia · trenes en tiempo
real · GTFS-Realtime · Amtrak · Amtraker · Brightline · VIA Rail · trains en
temps réel · VR · kaukojunat · NSW TrainLink · XPT · V/Line · The Ghan ·
Indian Pacific · Spirit of Queensland · Transwa · Renfe · AVE · Avlo · Alvia ·
Rodalies · Vy · SJ Nord · tog i sanntid · SJ · Snälltåget · Öresundståg · tåg
i realtid · Irish Rail · Enterprise · traenacha beo · NS Intercity · Arriva ·
treinen live · Zugverkehr · treni in tempo reale · togtrafik · 火车实时地图 ·
geo_location · tarjeta de mapa · Lovelace · HACS · Marketplace · Live Track ·
LiveTrack · StrausbergAutomationWorks

---

**Reconocimiento.** StrausbergAutomationWorks reconoce a los pueblos indígenas
de todas las tierras y aguas de este mapa, en todo el mundo, y presenta sus
respetos a sus Mayores del pasado y del presente.
