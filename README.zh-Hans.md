# Live Track Intercity Rail

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · **简体中文** · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk bokmål](README.nb.md) · [Gaeilge](README.ga.md) · [所有语言](#语言)

**为 Home Assistant 显示城际列车，全部在一张地图上。** Live Track Intercity Rail 把你选择的城际和长途铁路的每一列列车放到你的 Home Assistant 地图上：它在哪里、它的车次、按铁路自己的规则是否晚点，以及它的下一站。每条铁路单独添加，使用它自己发布的数据。

> **Live Track Intercity Rail 是 Live Track 的一个模块**。Live Track 是一组 Home Assistant 集成，把一切移动的东西，以及它们穿过的天气，画在同一张共享地图上：飞机、船只、列车和天气。可以单独安装，也可以和其他模块一起安装（[见下方列表](#live-track-的组成部分其他模块)）。

> **不断扩展，欢迎提出想法。** Live Track Intercity Rail 目前覆盖 3 大洲 9 个国家的 33 条铁路，我们还在添加更多铁路和国家。缺少你的铁路吗？[提出建议](#帮助它成长)，或者自己添加：我们会帮你完成。

**状态：0.1.0，首个版本。** 已通过链接添加到 Marketplace（[见下方](#安装步骤)）；它还不在 Marketplace 的目录中。

StrausbergAutomationWorks 的原创作品。与 Amtrak、Amtraker、Brightline、VIA Rail、Fintraffic、VR、Transport for NSW、NSW TrainLink、Transport Victoria、V/Line、Queensland Rail、Journey Beyond、Public Transport Authority of Western Australia、Transwa、Renfe、Rodalies de Catalunya、Entur、Vy、Go-Ahead Norge、SJ Nord、Trafikverket、SJ、VR Snabbtåg、Snälltåget、Öresundståg、Pågatågen、Mälartåg、Västtågen、Krösatågen、Östgötapendeln、Norrtåg、Tåg i Bergslagen、X-Tåget、Värmlandstrafik、Tågab、Inlandsbanan、Irish Rail、National Transport Authority（爱尔兰）、NS、Arriva、Keolis、OVapi 或任何其他铁路均无关联，也未获其认可。

---

## 目录

1. [全部功能](#全部功能)
2. [适用地区](#适用地区)
3. [Live Track 的组成部分：其他模块](#live-track-的组成部分其他模块)
4. [开始之前](#开始之前)
5. [安装步骤](#安装步骤)
6. [设置步骤](#设置步骤)
7. [解锁更多功能的免费密钥](#解锁更多功能的免费密钥)
8. [把地图放到仪表盘上](#把地图放到仪表盘上)
9. [在自动化中使用](#在自动化中使用)
10. [地图上的全部内容详解](#地图上的全部内容详解)
11. [它创建的全部实体](#它创建的全部实体)
12. [它发送和下载的内容](#它发送和下载的内容)
13. [帮助它成长](#帮助它成长)
14. [语言](#语言)
15. [致谢与许可](#致谢与许可)
16. [关键词](#关键词)

---

## 全部功能

### 在地图上，无需任何设置

你添加一条**铁路**：先选一个国家，再选该国的一条城际铁路。之后下面的所有内容都会为这条铁路显示。想要其他铁路，就为每一条再添加一次集成。

| 内容 | 适用范围 | 来源 |
|---|---|---|
| **运营中的列车**：每列车一个标记，以车次或线路作标签，使用铁路自己的配色，朝向列车行驶的方向 | 每条铁路 | 每条铁路自己发布的数据 |
| **晚点**：按铁路自己的规则，列车显示为晚点或严重晚点；铁路没有公布规则的，按列车行驶的距离判断 | 每条报告延误的铁路 | 每条铁路自己的数据源 |
| **下一站及其时间**：列车接下来停靠的车站，以及预计到达那里的时间 | 数据源或时刻表提供这些信息的每条铁路 | 每条铁路自己的数据源和时刻表 |
| **沿轨道行驶的列车**：两次报告之间，列车以最后的速度沿自己的线路前进，而不是走直线 | 线路已知的每条铁路 | 每条铁路的时刻表，或随集成提供的线路 |
| **按时刻表显示的列车**：铁路不公布位置的，每列车按其时间放在线路上，并标记为估计 | Journey Beyond、Queensland Rail Travel 和 WA Trains（澳大利亚），SJ Nord（挪威）；Irish Rail 结合其最新延误 | 每条铁路的时刻表或时间 |
| **部分列车的图画**：圣诞老人快车和夏日小屋（芬兰），Journey Beyond 列车的动物，Queensland Rail Travel 每条线路各一幅图画 | 芬兰、澳大利亚 | 为本集成绘制 |
| **停在边境**：停在美国与加拿大边境口岸的列车显示 "Customs"，代替其延误 | 往返加拿大的 Amtrak 列车 | Amtrak 的位置 |
| **每条铁路一个计数**：运营中的列车 | 每条铁路 | 同一份数据 |

### 用你自己的免费密钥或账户开启

| 免费密钥或账户 | 增加的内容 |
|---|---|
| **Transport for NSW Open Data** 密钥 | NSW TrainLink 的区域列车（澳大利亚新南威尔士州） |
| **Transport Victoria Open Data** 密钥 | V/Line 的长途列车（澳大利亚维多利亚州） |
| **NS API 门户**密钥 | NS Intercity，以及 Arriva 和 Keolis 的区域列车（荷兰）；一个密钥适用于全部三家 |
| **Trafikverket** 密钥 | 15 条瑞典铁路；一个密钥适用于全部十五条 |

每个密钥只需几分钟即可获得：[见下方的步骤](#解锁更多功能的免费密钥)。其余 13 条铁路不需要密钥。

---

## 适用地区

| 地区 | 你得到什么 | 来源 | 需要 |
|---|---|---|---|
| **澳大利亚**：全国 | Journey Beyond：The Ghan、The Ghan Expedition、Indian Pacific、Great Southern、The Overland，仅按时刻表显示（[原因](#journey-beyond澳大利亚)） | Journey Beyond | 无 |
| **澳大利亚**：新南威尔士州 | NSW TrainLink 的区域列车（XPT 和 Xplorer），也开往昆士兰州、维多利亚州和澳大利亚首都领地 | Transport for NSW | 一个免费密钥 |
| **澳大利亚**：昆士兰州 | Queensland Rail Travel：Spirit of Queensland、Spirit of the Outback、Tilt Train、Westlander、Inlander、Kuranda Scenic Railway、Gulflander，按其公布的时间显示（[原因](#queensland-rail-travel澳大利亚)） | Queensland Rail Travel | 无 |
| **澳大利亚**：维多利亚州 | V/Line 的长途列车（其通勤线路在 Live Track Commuter Rail 中），也开往新南威尔士州 | Transport Victoria | 一个免费密钥 |
| **澳大利亚**：西澳大利亚州 | WA Trains：Australind、Prospector、MerredinLink 和 AvonLink，仅按时刻表显示（[原因](#wa-trains西澳大利亚州澳大利亚)） | Public Transport Authority of Western Australia | 无 |
| **欧洲**：芬兰 | VR 的长途列车 | Fintraffic Digitraffic | 无 |
| **欧洲**：爱尔兰 | Irish Rail 的 InterCity 列车，以及从都柏林开往贝尔法斯特（英国）的 Enterprise | Irish Rail、National Transport Authority | 无 |
| **欧洲**：荷兰 | NS Intercity，以及 Arriva（Arriva、RRReis、Blauwnet）和 Keolis（Blauwnet、RRReis）的区域列车；NS 的 Sprinter 在 Live Track Commuter Rail 中 | NS、OVapi | 一个免费密钥 |
| **欧洲**：挪威 | Vy 的 F、RE、RX 和 R 线（F1 也开往瑞典），Go-Ahead Norge 的 F5 和 R50，SJ Nord 的 F6、F7 以及 R60 至 R75 | Entur | 无 |
| **欧洲**：西班牙 | Renfe 的 AVE、Avlo、Alvia、Avant、Euromed、Intercity、MD 和 Regional 列车，也开往法国和葡萄牙；Rodalies de Catalunya 的区域线路 R11 至 R17 | Renfe | 无 |
| **欧洲**：瑞典 | SJ、VR Snabbtåg、Snälltåget、Öresundståg、Pågatågen、Mälartåg、Västtågen、Krösatågen、Östgötapendeln、Norrtåg、Tåg i Bergslagen、X-Tåget、Värmlandstrafik、Tågab 和 Inlandsbanan，各自作为一条铁路；Öresundståg 也开往丹麦 | Trafikverket | 一个免费密钥 |
| **北美**：加拿大 | VIA Rail，所有线路 | VIA Rail | 无 |
| **北美**：美国 | Amtrak，所有线路，也开往加拿大 | Amtraker | 无 |
| **北美**：美国 | Brightline（佛罗里达州） | Brightline | 无 |

不在列表中？[告诉我们](#帮助它成长)。只要有人公开发布数据，我们就会考虑添加。

⚠ **列车的好坏取决于其铁路的数据。** 有的铁路每隔几秒报告一次列车，有的每隔几分钟，有的只在列车经过信号机时报告，有的根本不公布位置。每条铁路的局限见[地图上的全部内容详解](#地图上的全部内容详解)。

⚠ **这不是铁路的官方信息。** 出行前，请查看铁路自己的应用或网站。

---

## Live Track 的组成部分：其他模块

Live Track 是一组 Home Assistant 集成，每种移动的东西一个，全部画在同一张地图卡片上。每个都能单独工作；合在一起就成为一幅实时画面。它们共享地图卡片和一个 Python 库（[saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)），因此再安装一个模块不会向另一个模块已在读取的来源增加请求。

| 模块 | 在地图上显示什么 | 状态 |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | 通过 ADS-B 显示头顶的飞机，带航线和机型图标 | 已发布 |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | 通过 AIS 显示船只和船艇，在你附近或任何地方 | 已发布 |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | 北美、欧洲和澳大利亚的通勤列车 | 已发布 |
| **Live Track Intercity Rail** | 北美、欧洲和澳大利亚的城际和长途列车（本模块） | 已发布 |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | 来自公开列表的移民和联邦执法飞机及船只 | 已发布 |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | 天气、风暴和自然灾害 | 已发布 |
| Live Track Stations | 每个车站的发车信息板和"该出发了"提醒 | 计划中 |
| Live Track Satellites | 从头顶经过的卫星 | 计划中 |
| Live Track Freight Trains | 铁路公开发布的货运和工程列车 | 计划中 |
| Live Track Transit | 城市公交、有轨电车、渡轮和地铁 | 计划中 |
| Live Track Intercity Buses | 城际和区域长途客车 | 计划中 |
| Live Track Commuter Buses | 通勤巴士 | 计划中 |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | 每个模块都在上面绘制的共享地图卡片 | 已发布，随每个模块一起安装 |

一切都是免费和开源的。没有任何功能只留给赞助者。

---

## 开始之前

* **Home Assistant** 2026.11 或更高版本。
* 你的 Home Assistant 中安装了 **Marketplace**（HACS），可以用简单的方式安装和更新。没有它也可以手动复制文件。
* Home Assistant 需要**互联网连接**：每列车都来自其铁路自己发布的数据。
* **可选：Marketplace 中的 auto-entities**，用于把标记放到地图上（见[把地图放到仪表盘上](#把地图放到仪表盘上)）。
* 无需付费。33 条铁路中有 13 条不需要账户；其余 20 条需要你自己的免费密钥，四个密钥即可覆盖全部（[见上方](#用你自己的免费密钥或账户开启)）。
* 集成第一次加载时，Home Assistant 会自行安装所需的 Python 包（`saw-livetrack`、`gtfs-realtime-bindings` 和 `tzdata`）。

---

## 安装步骤

### 通过 Marketplace（推荐）

Live Track Intercity Rail 还不在 Marketplace 的目录中。通过它的链接添加：

1. 在 Home Assistant 中打开**设置 → Marketplace**（HACS）。
2. 选择**从链接添加**（或三点菜单 → **自定义存储库**）。
3. 输入 `StrausbergAutomationWorks/LiveTrackIntercityRail`。如果要求选择类型，选择**集成**。
4. 在列表中找到 **Live Track Intercity Rail**，选择**下载**或**安装**。
5. **重启 Home Assistant**：**设置 → 系统 → 修复**会提供重启，或使用**设置 → 系统 → 重新启动 Home Assistant**。

之后 Marketplace 会把每个新版本作为更新提供。

### 手动安装

1. 下载[最新版本](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/releases/latest)的源代码。
2. 把其中的 `custom_components/live_track_intercity_rail` 文件夹复制到你的 Home Assistant 配置文件夹下的 `custom_components` 文件夹中（如果没有 `custom_components`，就新建一个）。
3. 重启 Home Assistant。

手动更新时，用新版本的文件夹替换旧文件夹，然后重启。

---

## 设置步骤

1. 打开**设置 → 设备与服务**。
2. 选择**添加集成**（右下角），搜索 **Live Track Intercity Rail**。
3. **Region**（地区）：选择铁路所在的国家。只列出至少有一条铁路的国家。选择**提交**。
4. **Railroad**（铁路）：选择铁路。选择**提交**。
5. **API key**（API 密钥）：仅用于 NSW TrainLink、V/Line、三家荷兰铁路和十五条瑞典铁路。粘贴你的密钥（[如何获取](#解锁更多功能的免费密钥)），然后选择**提交**。其他铁路跳过这一步。

就这样。列车会在一两分钟内出现。线路来自时刻表的铁路，在时刻表下载完成后，列车就开始沿线路行驶，第一次可能需要几分钟。要关注另一条铁路，就再添加一次集成。同一条铁路添加两次会被拒绝。

### 更改显示内容：选项

在要更改的铁路上打开**设置 → 设备与服务 → Live Track Intercity Rail → 配置**（齿轮图标）。只有一个选项：

| 选项 | 作用 | 默认值 |
|---|---|---|
| **Poll interval**（轮询间隔） | 读取铁路数据源的频率，15 到 600 秒。比数据源自身的刷新更短的间隔不会显示更多内容 | 按铁路设定：Renfe (Spain) 和三家荷兰铁路为 15 秒；Brightline、NSW TrainLink、Irish Rail 和 SJ Nord 为 60 秒；其他为 30 秒 |

---

## 解锁更多功能的免费密钥

二十条铁路要求每位用户使用自己的密钥，来自四个提供方。这些密钥全部免费，每位安装 Live Track Intercity Rail 的用户都获取自己的密钥。设置对话框要求时粘贴密钥（[上方第 5 步](#设置步骤)）。只要求密钥：不需要密码，也不需要其他机密信息。密钥与集成一起保存在 Home Assistant 中，只发送给它自己的提供方，绝不会写入日志。如果提供方连续十分钟拒绝它，Home Assistant 会要求你提供新的密钥。

### Transport for NSW（NSW TrainLink，澳大利亚新南威尔士州）

1. 打开 <https://opendata.transport.nsw.gov.au/>，选择 **Register**，创建账户并登录。
2. 选择你的用户头像图标，然后选择 **API Tokens**。
3. 为密钥输入一个名称，选择 **CREATE API TOKEN**。立即复制密钥：网站只显示一次。
4. 添加 NSW TrainLink 时，把它粘贴到 **API key** 中。只粘贴密钥本身：Live Track Intercity Rail 会自行加上 `apikey` 一词。

### Transport Victoria（V/Line，澳大利亚维多利亚州）

1. 打开 <https://opendata.transport.vic.gov.au/>，选择 **Login**，然后选择 **Sign up**。
2. 填写你的信息，选择 **Create Account**。输入你收到的电子邮件中的验证码，选择 **Confirm**。
3. 门户要求你在手机上使用身份验证器应用：用它扫描二维码，输入应用中的验证码，选择 **Confirm**。然后用你的电子邮件、密码和应用的验证码登录。
4. 选择 **My Account** → **Profile** → **API tokens**。你的密钥已经在那里。添加 V/Line 时，把它粘贴到 **API key** 中。

### NS（NS、Arriva 和 Keolis，荷兰）

1. 打开 <https://apiportal.ns.nl/>，选择 **Inloggen**（登录），然后选择 **Externe bezoeker**（外部访客）。
2. 填写表单并提交。一封电子邮件会确认注册。API 最多可能需要 5 分钟才会出现在门户中。
3. 打开 **Virtual Train API**（NS 的列车位置）页面。在 **Related Products** 下打开其产品，为你的订阅命名，然后选择 **Subscribe**。
4. NS 批准订阅后，你的密钥会显示在你的个人资料页面上。添加 NS、Arriva 或 Keolis 时，把它粘贴到 **API key** 中。一个密钥适用于全部三家。

### Trafikverket（15 条瑞典铁路）

1. 打开 <https://data.trafikverket.se/oauth2/Account/register>。
2. 填写 **Email**、**Displayname**（显示名称）、**Password**（密码）和 **Confirm password**，勾选 **Accept license and Agreement**，然后选择 **Register**。
3. 打开 <https://data.trafikverket.se/get-started>，在 **Create a key** 下选择 **Create key**。用你创建的账户登录，然后创建密钥。
4. 添加瑞典铁路时，把它粘贴到 **API key** 中。一个密钥适用于全部十五条。

---

## 把地图放到仪表盘上

地图是 [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)，每个 Live Track 模块都在上面绘制的卡片。**它随 Live Track Intercity Rail 一起安装**：无需下载，无需复制，无需添加资源。

1. 打开一个仪表盘，选择铅笔图标（**编辑仪表盘**），然后选择**添加卡片**。
2. 滚动到最下方，选择**手动**。
3. 粘贴以下内容，然后选择**保存**：

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

标记需要 Marketplace 中的 [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)。如果安装了其他 Live Track 模块，为它们的每个来源再加一个 `- domain: geo_location` 过滤器（`live_track_commuter_rail`、`live_track_aircraft` 等）。

**在地图上：**

* 每列车是一个使用其铁路配色的标记，以车次或线路作标签。Amtrak 的列车是星形，VIA Rail 的带有枫叶，Irish Rail 的 InterCity 列车是三叶草，有些列车是图画（下面每条铁路都会说明是哪些）。
* 在大多数铁路上，配色随方向互换：离开主要城市时一种，驶向它时另一种。
* 箭头显示列车行驶的方向。停着的列车保持最后的方向。图画保持直立，没有箭头。
* **指向**一列车可查看其铁路、车次、线路和运行区间。**点击**它可查看全部详情，包括下一站和延误。

如果你的仪表盘资源在 YAML 中设置（`lovelace: resource_mode: yaml`），就无法替你注册任何内容：**修复**中的一条提示会给出需要添加到 `configuration.yaml` 的确切内容。它们看起来像这样，占位符处为集成自己的地址：

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_intercity_rail/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

每个 Live Track 模块都带有一份卡片副本，并在 Home Assistant 启动时注册它。它们共同在**设置 → 仪表盘 → 资源**中保持恰好一行：其中任一模块所带的最新卡片版本，绝不会是更旧的版本。你自己通过 Marketplace 安装的卡片不会被改动。删除本模块的最后一条铁路时，这一行会转交给另一个 Live Track 模块，如果没有其他模块就会被删除。如果集成的文件被删除而其铁路仍处于设置状态，并且没有安装其他 Live Track 模块，请自己在**设置 → 仪表盘 → 资源**中删除这一行。

**如果想改为手动安装卡片**，请按照[卡片的 README](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track) 中的步骤操作。你自己为 `/local/` 下的副本创建的行，只有当本模块的副本是更新的版本时，才会指向本模块的副本。

任何其他显示 `geo_location` 实体的地图卡片也会显示这些列车，作为普通标记。

---

## 在自动化中使用

一切都是普通的 Home Assistant 实体，因此自动化编辑器可以直接使用，无需代码。

**你的铁路数据停止时在手机上收到通知**（列车随后会离开地图）：

1. **设置 → 自动化与场景 → 创建自动化 → 创建新的自动化**。
2. **每当**：**添加触发条件** → **实体** → **状态已变化**。选择该铁路的 **Trains in service**（运营中的列车）实体，在**变为（可选）**下选择**不可用**。
3. **就执行**：**添加动作**，搜索你手机的通知动作（它带有你手机的名称），输入一条消息，例如：

   ```text
   地图上没有城际列车：铁路的数据已停止
   ```

4. **保存**。

**其他想法：** 当 Amtrak 列车距离你在美国的家 2 公里（1.2 英里）以内时打开一盏灯，依据标记的距离；在仪表盘上统计 VR 一天中在芬兰开行的列车；Queensland Rail Travel 当天第一列车出发时（澳大利亚）发送消息，依据 **Trains in service** 升到 0 以上。

---

## 地图上的全部内容详解

### 列车

每列车是一个标记。它的状态是与你家的距离，单位为公里。铁路报告该列车时，或其时刻表显示它正在运行时，标记出现；列车离开铁路的数据或其运行结束时，标记被删除。

* **两次报告之间**，列车沿自己的线路驶向下一站：使用铁路报告的速度，铁路不报告速度时，使用其最后两次报告之间的速度。它绝不会越过下一站，并在最后一次报告 30 分钟后停止移动。在已知线路上的列车画在线路上；铁路自己的报告保存在旁边。
* **如果铁路的数据中断**，其列车会依据最后一次有效报告继续移动，最长 10 分钟。之后它们变为不可用，离开地图，直到数据恢复。
* **晚点和严重晚点**：铁路公布了自己的晚点规则的，集成使用该规则。没有公布的，按列车行驶的距离判断晚点，使用 Amtrak Status Maps（asm.transitdocs.com）的阈值。下面每条铁路都会说明使用哪种。

每列车上有：`marker_label`、`train`、`line_name`、`observed_at`（其报告成立的时间）、`course_deg`（移动时）、`next_stop` 和 `arrival_estimated_at`（已知时）、`delay_min`、`late_threshold_min` 和 `very_late_threshold_min`、`speed_kmh`（铁路报告时）、`attribution`，以及两次报告之间的 `previous_latitude`、`previous_longitude`、`previous_observed_at` 和 `segment_duration_s`。沿线路移动的列车带有 `position_source: estimated`，铁路的报告在 `fix_latitude` 和 `fix_longitude` 中。

### Journey Beyond（澳大利亚）

⚠ **Journey Beyond 不公布位置。** 每列车都根据其公布的时刻表绘制，时刻表已转录到随集成提供的文件中（发车日期至 2027 年 12 月 29 日），因此不下载任何内容。每列车按其时间放在线路上，标记为估计，没有延误：晚点或取消的列车仍按正点绘制。每种服务都有自己的图画（骆驼和骑手、一只鸟、一只袋鼠、一只鸸鹋），去程使用其配色，返程互换，没有标签：指向它即可看到列车及其运行区间。

### NSW TrainLink（澳大利亚新南威尔士州）

来自 Transport for NSW 的 NSW TrainLink 数据源，使用你自己的密钥，大约每分钟一个新位置。标签是车次。离开悉尼时为 NSW 橙色带白色圆环，驶向悉尼时互换。数据源没有速度，因此列车以其最后两个位置之间的速度沿线路行驶。晚点 11 分钟起算晚点（NSW TrainLink 把 10 分钟以内视为正点），30 分钟起为严重晚点。

### Queensland Rail Travel（澳大利亚）

⚠ **Queensland Rail Travel 不公布位置。** 你的 Home Assistant 读取 Queensland Rail Travel 的 Service Updates 页面显示的时间：当天列车列表最多每 5 分钟一次，每列车的时间从出发前 30 分钟到到达后 15 分钟，最多每 5 分钟一次。每列车按这些时间放在线路上，标记为估计。每条线路都有自己的图画，离开布里斯班时使用其配色，驶向布里斯班时互换，车次显示在旁边的标签中。不显示晚点或严重晚点。

### V/Line（澳大利亚维多利亚州）

来自 Transport Victoria 的 V/Line 数据源，使用你自己的密钥：前往 Albury、Ararat、Bairnsdale、Echuca、Maryborough、Shepparton、Swan Hill 和 Warrnambool 的长途线路。标签是车次。离开墨尔本时为 V/Line 紫色带黄色圆环，驶向墨尔本时互换。数据源没有速度，因此列车以其最后两个位置之间的速度行驶；10 分钟没有新位置后，按时间推算到下一站。长线路晚点 11 分钟起、短线路 6 分钟起算晚点（V/Line 自己的列表），30 分钟起为严重晚点。

### WA Trains（西澳大利亚州，澳大利亚）

⚠ **不公布实时位置。** 每列车都根据 Public Transport Authority of Western Australia 的时刻表绘制：按计划时间沿线路放置，标记为估计，没有延误。时刻表每天检查一次。标签是线路名称的前三个字母：AUS（Australind，紫色）、PRO（Prospector，橙色）、MER（MerredinLink，绿色）和 AVO（AvonLink，绿色），两个方向相同。

### VR（芬兰）

来自 Fintraffic 的 Digitraffic，大约每 30 秒一个新位置。标签是列车类型和车次，按 VR 的写法（`IC 23`）。离开赫尔辛基时为 VR 绿色带深色圆环，驶向赫尔辛基时互换。数据没有方向，因此箭头沿线路方向。晚点 6 分钟起算晚点（VR 把晚点超过五分钟的列车视为晚点），12 分钟起为严重晚点。

* **圣诞老人快车**，从将临期第一个星期日到 1 月 6 日：北上时是雪人，返程时是驯鹿，没有车次。晚点 12 分钟起，图形每隔几秒转一次身。
* **夏日小屋**，从仲夏夜前夕到 7 月 31 日：VR 的每列长途列车都画成一座小屋，车次显示在旁边。

### Irish Rail（爱尔兰）

来自 Irish Rail 的实时服务和 National Transport Authority 的时刻表。⚠ Irish Rail 只在列车经过相隔几分钟的信号点时报告列车，因此每列车根据其时刻表和最新延误绘制，沿其线路移动。标签是不带字母的车次（A700 显示为 700）。InterCity 列车离开都柏林时是带橙色轮廓和车次的绿色三叶草，驶向都柏林时颜色互换。Enterprise 是一个银色圆盘，带红色外圈、品红色色带和品红色车次；驶向都柏林时圆盘为品红色。晚点 10 分钟起算晚点（National Transport Authority 的规则），20 分钟起为严重晚点。

### NS、Arriva 和 Keolis（荷兰）

来自 NS 的车辆数据，使用你自己的密钥，大约每 10 秒一个新位置。该数据源报告列车自己的速度和方向，两者都会被采用。下一站和延误来自 OVapi 的时刻表；轨道是 NS 自己的线路地图，每天下载一次。标签是车次。NS 的列车为黄色带 NS 蓝色圆环；Arriva 和 Keolis 的列车暂时使用地图卡片自己的样式。晚点 3 分钟起算晚点（NS 自己的定义），10 分钟起为严重晚点。

### Vy、Go-Ahead Norge 和 SJ Nord（挪威）

来自 Entur，每条铁路各自一个条目。标签是线路代码（F4、RE10、R50）。离开 Oslo S 时为线路自己的颜色带白色圆环（不到达 Oslo S 的行程，以其较大的终点城市为准），驶向它时互换。Entur 不公布速度和方向，因此列车以其最后两个位置之间的速度行驶，箭头沿线路方向。在奥斯陆的长隧道中，位置中断的列车会沿线路继续移动，直到位置恢复。⚠ **SJ Nord 不公布位置：** 它的每列车都按预计时间放在线路上。晚点 4 分钟起算晚点，F 线和开往哥德堡（瑞典）的线路为 6 分钟，这是 Bane NOR 和 Vy 的规则；加倍即为严重晚点。

### Renfe (Spain) 和 Renfe Regionals (Catalunya)（西班牙）

**Renfe (Spain)** 读取 Renfe 的长途数据源，大约每 15 秒一个新位置。标签是车次；服务类别（AVE、Avlo、Alvia 等）显示在悬停框中。AVE 为海军蓝，Avlo 为青绿色，其他所有服务为 Renfe 紫色，离开马德里时为实心（不到达马德里的行程，以其较大的终点城市为准），驶向马德里时互换。Renfe 不公布线路走向，因此线路由 OpenStreetMap 构建，并随集成提供。Renfe 没有公布晚点规则，因此按行程长度判断晚点：400 公里（250 英里）以内 10 分钟起，560 公里（350 英里）以内 15 分钟，725 公里（450 英里）以内 20 分钟，885 公里（550 英里）以内 25 分钟，更远 30 分钟；加倍即为严重晚点。

**Renfe Regionals (Catalunya)** 绘制 Rodalies de Catalunya 的区域线路 R11 至 R17。标签是车次，使用线路自己的颜色，离开巴塞罗那时为实心，驶向巴塞罗那时互换。在巴塞罗那以外，位置是列车最后经过的车站，因此列车在车站之间按时刻表和其延误推算时间。晚点 10 分钟起算晚点，20 分钟起为严重晚点，按最长线路的长度判断。两条 Renfe 铁路都设置时，每列车只绘制一次。

### 瑞典铁路（瑞典）

来自 Trafikverket，使用你自己的密钥（一个密钥适用于全部十五条）。标签是车票上的车次；品牌、车次和始发终点站显示在悬停框中。每个品牌都有自己的配色，驶向 Stockholm C 时互换（不到达 Stockholm C 的行程，以其较大的终点城市为准）。Trafikverket 在大约一半的位置中提供速度；其他列车以其最后两个位置之间的速度行驶。瑞典不公布线路走向，因此线路由 OpenStreetMap 构建，并随集成提供。晚点 6 分钟起算晚点（Trafikverket 把 5 分 59 秒以内视为正点），12 分钟起为严重晚点。

### VIA Rail（加拿大）

来自 VIA Rail 自己的列车状态数据。每列车是一个带枫叶的圆盘，色带颜色表示其线路组（Atlantic、Western、Ontario 和 Quebec、Prince Rupert、Churchill、Sudbury 至 White River、Montréal scenic），车次显示在直立的标签中。单数车次为黄色圆盘，双数车次为色带颜色的圆盘。没有新位置的列车会驶向下一站，以便按 VIA 自己的估计时间到达。VIA 没有公布晚点规则，因此在魁北克城至温莎走廊上晚点 10 分钟起、其他地方 60 分钟起算晚点（Amtrak Status Maps 对 VIA 的取值），加倍即为严重晚点。

### Amtrak（美国）

Amtrak 不公布开放的实时数据。Amtraker 转发 Amtrak 自己的列车追踪，每 3 到 5 分钟一个新位置，集成以 Amtrak 报告的速度让每列车沿线路移动。每列车是一颗星，车次横贯其上，使用其线路的配色（东北部线路、Cascades、Pacific Surfliner、Acela 等），否则为国旗星。Maple Leaf（纽约至多伦多）会在 Amtrak 的星形和 VIA 的徽标之间缓慢变换。停在 Lacolle、Rouses Point 或 Niagara Falls 边境的列车显示 "Customs"，代替其延误。晚点 16 分钟起算晚点（Amtrak 把 15 分钟以内视为正点），30 分钟起为严重晚点。同一车次可能同时在两三天的行程中运行，因此每次运行都有自己的标记。

### Brightline（美国）

来自 Brightline 自己的数据源，大约每 60 秒一个新位置。标签是行程编号，黑色带白色轮廓，位于目的地颜色的圆盘上，带黑色圆环。超过 5 分钟的位置不会使用。数据源没有速度，因此列车以其最后两个位置之间的速度行驶。Brightline 没有公布晚点规则，因此按行程长度判断：晚点 10 分钟起算晚点，20 分钟起为严重晚点。

---

## 它创建的全部实体

每条铁路：

| 实体 | 说明 |
|---|---|
| `sensor.<railroad>_trains_in_service` | **Trains in service**（运营中的列车）：该铁路此刻在地图上运行的列车数量。Amtrak 为：`sensor.amtrak_trains_in_service` |
| `geo_location.<railroad>_train_…` | 每列车一个（`geo_location.amtrak_train_5_17`）；随列车出现和消失。每个都带有 `source: live_track_intercity_rail`，其状态是与你家的距离，单位为公里 |

标记的实体 ID 来自铁路和该次运行，绝不来自其标签：`geo_location.amtrak_train_5_17` 是当月 17 日出发的 Amtrak 5 次列车，因此列车在整个运行过程中保持同一个实体 ID，同一车次的另一次运行会有自己的 ID。该次运行离开铁路的数据或结束时，标记被删除。和所有 Live Track 地图标记一样，这些标记没有唯一 ID，因此无法在界面中重命名、隐藏或分配区域。传感器有唯一 ID，可以重命名。

每次轮询都会变化的属性，即标记的位置和时间，会像任何实体一样记录在 Home Assistant 的历史中。传感器没有属性，因此保存成本很低，它记录了一天中有多少列车运行。要让标记不进入历史，把以下内容添加到 `configuration.yaml`，然后重启：

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.*_train_*
```

如果你的 `configuration.yaml` 已经有 `recorder:` 部分，只需把模式 `geo_location.*_train_*` 添加到其中的 `exclude:` 和 `entity_globs:` 下。该模式只匹配本模块的列车标记。设置为绘制历史的地图卡片届时将没有轨迹可绘制。

---

## 它发送和下载的内容

**关于你的位置。** 什么都不发送。你家的位置只在你的 Home Assistant 内部使用，用于计算每列车的距离。你的密钥（在铁路需要时）只发送给该铁路的提供方。关于你的其他任何信息都不会发送到任何地方。和任何网站一样，每个服务都能看到你的互联网地址。

**数据量。** 每个实时来源在每次轮询时读取，默认使用铁路自己的间隔（**Poll interval**，15 到 600 秒），表格中注明的则更少。多个 Live Track 模块或铁路读取同一来源时，一个共享客户端为它们全部只读取一次。测量时间为 2026 年 11 月 19 日 02:44 至 02:49 UTC：

| 铁路 | 实时数据，每次读取 | 时刻表和线路 |
|---|---|---|
| Journey Beyond（澳大利亚） | 无：不下载任何内容 | 无：其时刻表和线路随集成提供 |
| NSW TrainLink（澳大利亚） | 来自两个数据源的 124 KB，最多每 55 秒一次 | 40 MB，有变化时下载，每天检查 |
| Queensland Rail Travel（澳大利亚） | 列表 5.5 KB，每 5 分钟；每列运行中列车的时间 6 到 8 KB，每 5 分钟 | 无：其线路随集成提供 |
| V/Line（澳大利亚） | 来自两个数据源的 14 KB | 58 MB（Transport Victoria 311 MB 文件中 V/Line 的部分，单独读取），有变化时下载，每天检查 |
| WA Trains（澳大利亚） | 无：没有实时数据源 | 28 MB，有变化时下载，每天检查 |
| VR（芬兰） | 位置数据压缩后 1.4 KB；当天的列车，第一次压缩后 0.5 MB，之后只读取变化，每分钟一次 | 3.1 MB，每天 |
| Irish Rail（爱尔兰） | 0.2 KB，最多每 55 秒一次 | 6.6 MB，有变化时下载，每天检查；车站列表 46 KB，每周一次 |
| NS、Arriva、Keolis（荷兰） | 1.5 KB，最多每 9 秒一次；来自 OVapi 的延误 5.3 MB，每 5 分钟且仅在有变化时 | OVapi 的时刻表 267 MB，最多每周一次且仅在有变化时；NS 的轨道地图 1.3 MB，每天 |
| Vy、Go-Ahead Norge、SJ Nord（挪威） | Vy 来自两个数据源的 510 KB，Go-Ahead Norge 7 KB，SJ Nord 0.7 KB 每分钟一次 | Vy 67 MB，Go-Ahead Norge 20 MB，SJ Nord 26 MB，有变化时下载，每天检查 |
| Renfe (Spain) | 来自两个数据源的 2.1 KB | 0.7 MB，每天；其线路随集成提供 |
| Renfe Regionals (Catalunya)（西班牙） | 来自两个数据源的 0.2 KB，包含 Renfe 的所有地方网络 | 16 MB，每天 |
| 瑞典铁路（瑞典） | 第一次 474 KB，之后变化部分 5 到 9 KB | 无；车站列表 0.15 MB，每天；线路随集成提供 |
| VIA Rail（加拿大） | 353 KB，压缩后以 33 KB 发送 | 1.0 MB，每周一次 |
| Amtrak（美国） | 1.2 MB，压缩后以 113 KB 发送 | 18.6 MB，每周一次 |
| Brightline（美国） | 来自两个数据源的 1.3 KB | 29 KB，每周一次 |

⚠ 测量时澳大利亚是白天，北美是傍晚，欧洲是夜间。实时数据源在夜间最小：白天欧洲的数据源比表中显示的更大。

**出错之后。** 列车会依据最后的有效数据继续移动，最长 10 分钟；之后标记为不可用，直到来源恢复响应。下载失败的时刻表会稍后重试，你现有的副本继续使用。如果提供方连续十分钟拒绝你的密钥，Home Assistant 会要求提供新的密钥。

**磁盘上。** 时刻表和线路走向保存在 Home Assistant 的 `.storage` 文件夹中，名称以 `saw_` 开头，与读取同一铁路的其他 Live Track 模块共享。如果你删除 Live Track Intercity Rail，且没有其他 Live Track 模块使用它们，可以手动删除。

---

## 帮助它成长

Live Track Intercity Rail 仍在成长。我们发现新的铁路和国家就会添加，也想知道你接下来希望看到什么。

### 提出建议

缺少你的国家或铁路吗？有什么地方不对，或难以理解？用你觉得最方便的方式告诉我们：

* [**填写一份简短的表单**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=zh-Hans.yml)，使用中文。你需要一个免费的 GitHub 账户。
* **发送电子邮件**到 [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org)。无需账户。

无论哪种方式，告诉我们以下内容会有帮助：

* 你希望看到什么，以及在世界上的什么地方；
* 数据发布地点的链接，如果你知道的话（开放数据页面、公开数据源、服务网站）：不是必需的，但会有帮助；
* 你的 Home Assistant 语言，如果问题出在措辞或翻译上。

用英语或你自己的语言书写都可以，哪种方便用哪种。

### 在我们的帮助下自己添加

如果你想自己添加什么，我们会帮你完成，从第一个问题到最终发布。开始时你不需要是开发者：

* **翻译。** 设置对话框中的文字是一个文本文件里的一小串短语。我们会告诉你是哪个文件、哪几行。
* **新的铁路。** 告诉我们数据在哪里发布。我们可以一起写代码，或者帮你检查你写的代码。
* **在你所在的地方测试。** 安装它，查看地图上你所在的部分，告诉我们哪些正确、哪些不正确。
* **修正这份 README。** 如果某个步骤与你看到的不一致，告诉我们你看到了什么。

[**告诉我们你的想法**](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues/new?template=zh-Hans.yml)，或写信到 [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org)，我们会回复接下来的步骤。

---

## 语言

本 README：[English](README.md)、[Deutsch](README.de.md)、[Français](README.fr.md)、[Nederlands](README.nl.md)、**简体中文**、[Español](README.es.md)、[Italiano](README.it.md)、[Dansk](README.da.md)、[Suomi](README.fi.md)、[Svenska](README.sv.md)、[Norsk bokmål](README.nb.md)、[Gaeilge](README.ga.md)。每份翻译的 README 都是完整的。目前还没有一份经过母语人士阅读。如果其中某种语言是你的母语，请告诉我们它的 README 读起来是否通顺：见[帮助它成长](#帮助它成长)。

设置对话框和选项目前只有英文，无论你的 Home Assistant 使用什么语言。如果你会说其他语言，可以自己翻译它们：只是一个文件里的一小串短语，[我们会帮你完成](#在我们的帮助下自己添加)。

发现翻译中的错误，或需要其他语言？请在 <https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail/issues> 告诉我们，或[在我们的帮助下翻译](#在我们的帮助下自己添加)。

---

## 致谢与许可

每个实时来源都由你的 Home Assistant 在运行时读取；本仓库中不包含任何实时数据源的内容。每列车在其 `attribution` 属性中注明来源。作为接收数据的人，你须遵守每个来源的条款。

* **Amtraker**（amtraker.com），转发 Amtrak 的列车追踪（美国）：数据采用 [Open Data Commons Attribution License (ODC-By) v1.0](https://opendatacommons.org/licenses/by/1-0/)，须注明出处。线路走向使用 **Amtrak** 自己的时刻表。
* **Brightline**（美国）：其 GTFS 和 GTFS-Realtime 数据源；Brightline 未公布条款。
* **VIA Rail**（加拿大）：其列车状态数据，VIA 未公布相关条款；其时刻表采用 Open Government Licence - Canada 2.0（[developer resources](https://www.viarail.ca/en/developer-resources)）。
* **Fintraffic / digitraffic.fi**（芬兰）：数据采用 CC BY 4.0。
* **Transport for NSW**（澳大利亚）：数据采用 CC BY 4.0（[数据许可](https://opendata.transport.nsw.gov.au/datalicence)）。
* **Transport Victoria**（澳大利亚）：数据采用 CC BY 4.0（[开放数据](https://discover.data.vic.gov.au/dataset/gtfs-realtime)）。
* **Queensland Rail Travel**（澳大利亚）：其 Service Updates 页面显示的时间，由你的 Home Assistant 读取；见 [Queensland Rail 的版权页面](https://www.queenslandrailtravel.com.au/copyright)。集成中不包含 Queensland Rail Travel 的任何内容。
* **Journey Beyond**（澳大利亚）：其公布的时刻表，转录到 `data/journey_beyond_timetable.json` 中；Journey Beyond 未公布相关条款。
* **Public Transport Authority of Western Australia**：时刻表数据可从 www.transperth.wa.gov.au 免费获取（[spatial data access](https://www.transperth.wa.gov.au/About/Spatial-Data-Access)；不是 CC BY）。
* **Renfe**（西班牙）：数据采用 CC BY 4.0（[data.renfe.com](https://data.renfe.com/)）。
* **Entur**（挪威）：包含采用挪威开放政府数据许可（[NLOD 2.0](https://data.norge.no/nlod/en/2.0)）的数据，由 Entur 分发。
* **Trafikverket**（瑞典）：数据采用 [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)。
* **Irish Rail**（爱尔兰）：实时数据；Irish Rail 未公布条款。时刻表来自 [National Transport Authority](https://www.transportforireland.ie/transitData/PT_Data.html)（爱尔兰），CC BY 4.0，按原样提供。
* **NS**（荷兰）：车辆数据和轨道地图，使用你自己的密钥，遵守 [NS API 门户](https://apiportal.ns.nl/)的条款。时刻表和延误来自 [OVapi](https://gtfs.ovapi.nl/)，CC0。
* **`data/` 中随附的文件**：Journey Beyond、Queensland Rail Travel、Renfe (Spain) 和瑞典的线路走向，由 [OpenStreetMap](https://www.openstreetmap.org/copyright) 构建，© OpenStreetMap 贡献者，采用 [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/)；Renfe 行程终点站所在的市镇（OpenStreetMap，ODbL 1.0）及其人口（Wikidata 属性 P1082，CC0，否则为 OpenStreetMap）；瑞典终点城市人口来自瑞典统计局（SCB）和 Trafikverket，均为 CC0 1.0；挪威终点城市人口来自挪威统计局，表 04859，CC BY 4.0。
* **地图卡片**是 [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)，MIT，是 nathan-gs 的 [ha-map-card](https://github.com/nathan-gs/ha-map-card)（MIT）的副本，随附于 `frontend/` 中。其地图瓦片及其署名见其 README。

以上机构均未制作或认可本集成。

**代码**：MIT，见 [LICENSE](LICENSE)。`data/` 中的文件保留其来源的许可，如上所列。

**开发者须知：** 每条铁路是 `custom_components/live_track_intercity_rail/operators/` 中的一个模块，读取 `sources/` 中的一个来源适配器；随附的线路走向用 `tools/` 中的脚本重新构建（`journey_beyond.py`、`qrt_lines.py`、`renfe_spain_lines.py`、`sweden_lines.py`）。测试用 `python -m unittest discover -s tests` 运行。

---

## 关键词

Home Assistant 火车 · Home Assistant 列车追踪 · 火车实时地图 · 城际铁路 · 长途列车 · GTFS-Realtime · Amtrak · Amtraker · Brightline · VIA Rail · trains en temps réel · VR · kaukojunat · NSW TrainLink · XPT · V/Line · The Ghan · Indian Pacific · Spirit of Queensland · Transwa · Renfe · AVE · Avlo · Alvia · Rodalies · trenes en tiempo real · Vy · SJ Nord · tog i sanntid · SJ · Snälltåget · Öresundståg · tåg i realtid · Irish Rail · Enterprise · traenacha beo · NS Intercity · Arriva · treinen live · Zugverkehr · treni in tempo reale · togtrafik · geo_location · 地图卡片 · Lovelace · HACS · Marketplace · Live Track · LiveTrack · StrausbergAutomationWorks

---

**致敬。** StrausbergAutomationWorks 向这张地图上世界各地陆地和水域的原住民族致意，并向他们过去和现在的长老致敬。
