"""Source adapters: one module per kind of source a railroad can name.

  amtraker        Amtraker /v3/trains (Amtrak today; measured per provider)
  brightline_rt   Brightline's own GTFS-Realtime (SSOT 8.2)
  via_rail        VIA Rail's own train-status JSON (SSOT 8.3)
  digitraffic_rail Fintraffic Digitraffic rail, Finland (SSOT 8.4)
  tfnsw           Transport for NSW's nswtrains (SSOT 8.6)
  vline           Transport Victoria's V/Line feeds (SSOT 8.5)
  renfe           Renfe's GTFS-Realtime, Catalonia's regional lines (SSOT 8.7)
  renfe_ld        Renfe's long-distance GTFS-Realtime, AV, LD and MD (SSOT 8.7); its lines in renfe_ld_lines
  entur           Entur, Norway: one railroad's codespace through the shared client (SSOT 8.8)
  entur_et        Entur's SIRI ET, a railroad with no positions (SJ Nord, SSOT 8.8)
  trafikverket    Trafikverket, Sweden: one brand through the shared client (SSOT 8.9); its lines in sweden_lines
  irish_rail      Irish Rail, Ireland: the NTA timetable, the realtime API as updates, shared client (SSOT 8.10)
  ns              NS, the Netherlands: NS's positions, SpoorKaart's track, OVapi's timetable and delays (SSOT 8.11)
"""
