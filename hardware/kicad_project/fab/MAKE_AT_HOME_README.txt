AQUARIUM V0 — DIY PCB FABRICATION FILES (Sep 16, 2026)
======================================================

Board sizes (verify printed page with a ruler BEFORE etching — scale must be 1:1):
  Board 1: 150.5 x 20.0 mm   Board 2: 149.0 x 20.0 mm
  Board 3:  97.9 x 20.0 mm   Board 4: 175.1 x 20.0 mm
  2-layer (F.Cu top, B.Cu bottom), 1.6 mm FR4 assumed.

PRINTABLE (aquarium_v0_all_printable_pdfs.zip + print/ folder)
  boardN_F_Cu_1to1.pdf     — top copper, actual size
  boardN_B_Cu_1to1.pdf     — bottom copper, actual size
  boardN_assembly_silk.pdf — silkscreen + outline, component placement reference
  boardN_drill_map.pdf     — drill hole locations with symbols
  Print settings: "Actual size / 100%" — NEVER "fit to page".
  Toner-transfer/UV: mirror the layer that touches the copper
  (F.Cu printed from the BACK for toner transfer; B.Cu printed normally,
  or vice-versa depending on your method).

GERBERS (aquarium_v0_boardN_gerbers.zip, one per board)
  For any fab house (JLCPCB/PCBWay/local). Contains all layers +
  aquarium_v0_boardN.drl (Excellon drill). Also usable for CNC:
  the .drl drives the drill machine; .gm1 (Edge_Cuts) is the outline.

CRITICAL DIY WARNINGS
  1. NO PLATED THROUGH-HOLES at home: every via and PTH pad (J-headers,
     U10 header, barrel jack) must have a piece of wire pulled through
     and soldered BOTH sides, or components soldered on both sides.
  2. Clearances are 0.3 mm on power nets, 0.15 mm elsewhere — use fine
     toner/UV artwork; check tracks with a loupe before etching.
  3. The drill files assume real plated vias; if hand-wiring vias,
     use 0.6-0.8 mm wire in the 0.9 mm via holes.
