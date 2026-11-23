export const meta = {
  name: 'pcb-route-and-verify',
  description: 'Route aquarium_v0 driver PCB: 6 parallel DRC-gated route agents on disjoint net groups, merge, zones+GND pour, adversarial verify panel',
  phases: [
    { title: 'Route', detail: '6 agents route disjoint net groups in scratch copies, gated on DRC 0 violations' },
    { title: 'Merge', detail: 'combine overlays, resolve cross-group band conflicts, full-board DRC' },
    { title: 'Zones', detail: 'B.Cu GND pour, F.Cu thermal islands, GND + stitching vias, refill' },
    { title: 'Verify', detail: '5-lens adversarial panel: parity, connectivity, fab rules, layout quality, reproducibility' },
  ],
}

const PROJ = 'C:/Users/Akshat Jagdev/Desktop/aquarium_v0/hardware/kicad_project'
const BRIEF = PROJ + '/ROUTING_BRIEF.md'
const SCRATCH = 'C:/Users/Akshat Jagdev/AppData/Local/Temp/aquar_route_'

const ROUTE_SCHEMA = {
  type: 'object',
  properties: {
    routes: { type: 'array', items: { type: 'object', properties: {
      net: { type: 'string' }, layer: { type: 'string', enum: ['F.Cu', 'B.Cu'] },
      width: { type: 'number' },
      pts: { type: 'array', minItems: 2, items: { type: 'array', minItems: 2, maxItems: 2, items: { type: 'number' } } }
    }, required: ['net', 'layer', 'width', 'pts'] } },
    vias: { type: 'array', items: { type: 'object', properties: {
      net: { type: 'string' }, x: { type: 'number' }, y: { type: 'number' }
    }, required: ['net', 'x', 'y'] } },
    drc_violations_final: { type: 'number' },
    my_nets_unconnected_final: { type: 'number' },
    notes: { type: 'string' }
  },
  required: ['routes', 'vias', 'drc_violations_final', 'my_nets_unconnected_final', 'notes']
}

const GROUPS = [
  { id: 'g1_24v', nets: ['+24V'], hint:
    'You own the ENTIRE +24V net: the 1.0mm trunk at y=2.2 from J7.2(37,6) to x~575 (KEY FACT from the brief: every D cathode pad at (x0+18.6, 2.5) is directly crossed by the trunk — same-net overlap IS the connection, no drop needed for diodes), the input-cluster feeds (J7.2 up to trunk, C2.1(43,13), C1.2(52,14.22), U8.1(48,5)), and per-cell cap feeds per the working band plan (drop x0+21.0 to C100n pin2 + horizontal y9.05 to U pin5; right-side drop x0+29 down to y10.9, left, up into C22uF pin2 bottom, RSET pin2 from below through the same vertical). All F.Cu, 0.5mm drops, 1.0mm trunk. Other agents own SW, A/K, chains, logic — leave their bands (y 7.0, y 13.65, y 4.2, B.Cu corridor) alone; your drops crossing those bands at x0+21 / x0+29 are EXPECTED and the merge agent resolves the two documented conflicts (W3/W4). Verify with pad_pos.' },
  { id: 'g2_sw', nets: ['Net-(U1-SW)','Net-(U2-SW)','Net-(U3-SW)','Net-(U4-SW)','Net-(U5-SW)','Net-(U6-SW)','Net-(U7-SW)'], hint:
    'You own all 7 switching-node nets. High dI/dt — SHORT loops on F.Cu only, per cell: D anode (x0+18.6, 6.5) down to y~8.0, left to x0+17.36, down to U pin1 (y 9.05); L pad1 (x0+12.95, 10) horizontal at y 9.05 right to U pin1 pad (land ON the pad edges — same net). 0.5mm. Do NOT touch y bands 2.2 (trunk), 4.2, 7.0, 13.65 or B.Cu. Keep >=0.15mm from every foreign pad (U pin2 GND y 9.7-10.3 and pin3 CTRL y 10.65-11.25 sit right below your pad-1 approach — check clearance with DRC).' },
  { id: 'g3_white', nets: ['/W1_A','/W1_K','/W2_A','/W2_K','/W3_A','/W3_K','/W4_A','/W4_K'], hint:
    'You own the 4 white channel pairs (A=SET node: U pin4 + RSET pin1 + header pin1; K: L pad2 + header pin2). Band plan: _A at y=13.65 (1.0mm) — W1/W2 run LEFT to their header pin1 (109 / 233), W3/W4 run RIGHT (369 / 475); stub at x0+18.54 from RSET pin1 top edge (14.32) up to the band; also connect U pin4 (x0+19.64, 10.95) down to RSET pin1. _K: W1/W2 at y=7.0 (0.8mm) left-going from L pad2 top; W3/W4 RIGHT-going at y=4.2 (0.5-0.8mm, corridor between the D pads y-windows) from L pad2 up around; approach header pin2 pads from BELOW between pin1/pin3 pads (x Hx-2.54, vertical from your band up to y 5.5). KNOWN conflicts with +24V drops at x0+21/x0+29 (the +24V agent places those) — you do NOT have their segments, so route to your bands as if the drops exist at x0+21.0 (spans y 2.2-9.05) and x0+29 (spans y 2.2-18.55): where your band crosses one, add a clean jog AROUND it using the free x-gap between D anode pad right edge (x0+19.5) and the drop (x0+20.75) — only 0.95mm wide, fits a 0.5mm track at x0+20.15 — or drop to B.Cu with two vias for the crossing stretch; DOCUMENT in notes which you did so the merge agent can validate.' },
  { id: 'g4_logic', nets: ['/VIN_RAW','/SW_A','+5V','+3V3','/PWM_W','/PWM_R','/PWM_B','/PWM_DR'], hint:
    'You own the input/logic cluster (x 0-100). /VIN_RAW: J1.1(8,6) to F1.1(12,15) — route down-left of the fuse clips (F1 pads at 12,15 and 26.7,15, 2.3mm squares; F1 body spans x 1.75-22.25 y ~12-18, tracks may cross the BODY, just not foreign pads). /SW_A: F1.2(26.7,15) to J7.1(32,6). +24V from J7.2 is NOT yours (g1 owns). +5V: U8.3(53.08,5) to C3.2(66,14.55) and U9.3(55.35,17.3). +3V3: U9.2(55.35,15) to C4.2(70,14.55) and J6.6(90.7,5). PWM x4: J6 pins 1-4 (y 5) down to R1-R4 pin2 (y 11.18) — short 0.25mm runs, keep them parallel-ish between the J6 and resistor rows, watch J6.5 GND pad (88.16,5) and R rows. Avoid MH1 (20,4, keep 1mm) and the +24V trunk at y 2.2 (g1 owns; your nets can dip under/around it on B.Cu if a crossing is unavoidable — prefer routing below y 6). 0.25mm Default class.' },
  { id: 'g5_color_a_ctrl', nets: ['/R_A','/B_A','/DR_A','/CTRL_W','/CTRL_R','/CTRL_B','/CTRL_DR'], hint:
    'You own the colour-channel anode nets and the 4 CTRL nets. Plan: B.Cu corridor y 16.8-19.5 (GND pour will cover y<16.5 — keep corridor tracks >=16.7). /R_A: via near R14 pin1 (U5 x0=155, pad x 172.93-174.15 y 14.32-17.68 — stub on F.Cu from pad bottom y 17.68 down to corridor, via) then B.Cu left to x 103.92, via up, F.Cu vertical to J2 pin3 (103.92, 5.5) — the F.Cu vertical crosses NOTHING per analysis (clears W1 bands x-start 106.46/109 by >1mm, check with DRC). /B_A: same pattern from U6 x0=196 to J2 pin5 (98.84, 5.5). /DR_A: from U7 x0=398 to J4 pin5 (364.62, 5.5) — careful: the F.Cu vertical at 364.62 crosses W3_A band (y 13.65, x 348-369) and W3_K band (y 4.2): route the vertical on B.Cu up to y ~7 first, via to F.Cu at y 7 only if clear, or land the via directly next to the J4 pin5 pad and make the final approach a 1-2mm F.Cu stub. CTRL x4: from R1-R4 pin1 (88-98.5, y 12.82) + R5-R8 pin2 (y 16.68) — pull-down resistor bank — route each CTRL net on B.Cu corridor (0.25mm) rightward to its driver(s), via up near U pin3 (x0+17.36, y 10.95) with a short F.Cu stub to the pad. /CTRL_W feeds FOUR drivers (U1 3, U2 3, U3 3, U4 3) — one corridor lane with four via-up stubs. The lane must not overlap other nets in the same x-range: you share the corridor with chains + long K nets (another agent) — occupy DISTINCT lanes: use y=18.35 and y=18.75 for CTRL, y=17.15/17.55 for your A-nets, and note your lane choices in notes for the merge agent.' },
  { id: 'g6_color_k_chains', nets: ['/R_K','/B_K','/DR_K','/R_J23','/R_J34','/R_J45','/B_J23','/DR_J45'], hint:
    'You own the colour cathode returns and the 5 inter-header chains. B.Cu corridor y 16.8-19.5, lanes reusable in disjoint x-ranges. /R_K is the monster: L5 pad2 (158.05, 10; pad x 156.55-159.45 y 7.3-12.7) — stub down from pad bottom (y 12.7) at x 158.05 to corridor, via, B.Cu right ~309mm to x 467.38, via up, F.Cu stub into J5 pin4 (467.38, 5.5). /B_K: L6 pad2 (199.05) to J3 pin6 (220.3, 5.5). /DR_K: L7 pad2 (401.05) to J5 pin6 (462.3, 5.5). Chains (0.3-0.5mm): /R_J23 J2.4(101.38,5.5)-J3.3(227.92); /R_J34 J3.4(225.38)-J4.3(363.92); /R_J45 J4.4(361.38)-J5.3(469.92); /B_J23 J2.6(96.3)-J3.5(222.84); /DR_J45 J4.6(356.3)-J5.5(464.84). Each chain: F.Cu stub from header pad down to corridor (vertical at the pad x — analysis says x 101.38/96.3/225.38 are clear of W1/W2 bands; 361.38/356.3 CROSS W3 bands y 4.2 and y 13.65 — for those two, run the vertical on B.Cu and approach the J4 pad with a via placed 2mm below the pad at y ~7.7, then a short F.Cu stub up), B.Cu across, via + stub at the far end. Lane discipline: you share the corridor with the A/CTRL agent — claim y=17.0 (R_K 0.8mm), y=17.9, y=18.15, y=19.0, y=19.3, y=16.85 for your nets and note choices in notes; reuse lanes only in disjoint x-ranges. Long B.Cu runs pass UNDER everything (cells, trunk, bands) — zero F.Cu interaction except at your via/stub endpoints.' },
]

const commonPrompt = (g) => `You are a PCB routing agent. READ ${BRIEF} FIRST — it has all geometry, toolchain commands, the overlay JSON format, and ground rules. Your scratch directory: ${SCRATCH}${g.id} — create it by copying the project: cp -r "${PROJ}" "${SCRATCH}${g.id}" (quote paths, there are spaces). Work ONLY in the scratch copy; NEVER touch ${PROJ}.

YOUR NETS: ${g.nets.join(', ')}
ASSIGNMENT NOTES: ${g.hint}

Iterate with the DRC oracle until: 0 violations, and zero unconnected_items in drc.json mentioning any of YOUR nets (other nets' unconnected entries are OTHER agents' business — ignore them; GND is the zones agent's). Use gen_pcb.pad_pos/COMPS in your scratch to get exact pad coordinates; land tracks directly ON same-net pads (overlap = connection). Return your FINAL TESTED overlay verbatim (routes + vias, exactly the contents of your scratch ROUTES_EXTRA.json) plus final DRC counts and notes (include your lane/band choices and any deviation from the brief). If a net turns out to be genuinely unroutable within the rules, route everything else and say so in notes with the exact blocker.`

phase('Route')
log('fanning out 6 route agents on disjoint net groups...')
const routeResults = (await parallel(GROUPS.map(g => () =>
  agent(commonPrompt(g), { label: 'route:' + g.id, phase: 'Route', schema: ROUTE_SCHEMA })
))).filter(Boolean)
log(`route agents done: ${routeResults.length}/${GROUPS.length} returned overlays`)

const MERGE_SCHEMA = {
  type: 'object',
  properties: {
    drc_violations_final: { type: 'number' },
    unconnected_final: { type: 'number' },
    unconnected_nets_remaining: { type: 'array', items: { type: 'string' } },
    conflicts_resolved: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' }
  },
  required: ['drc_violations_final', 'unconnected_final', 'unconnected_nets_remaining', 'conflicts_resolved', 'notes']
}

phase('Merge')
log('merging overlays and resolving band conflicts on the real board...')
const merge = await agent(`You are the PCB merge agent. READ ${BRIEF} first. You work in the REAL project directory: ${PROJ}.

Six route agents produced overlays for disjoint net groups. Their results (routes + vias + notes) as JSON:
${JSON.stringify(routeResults)}

The GND net is deliberately absent (a zones agent handles it AFTER you — GND unconnected items are expected and fine).

Your job:
1. Merge all routes/vias into ONE ${'ROUTES_EXTRA.json'} in ${PROJ} (this file is a first-class source of truth; gen_pcb.py reads it via the overlay hook).
2. Run: python gen_pcb.py, then kicad-cli pcb drc --format json -o drc.json aquarium_v0.kicad_pcb.
3. Resolve cross-group conflicts. The brief's KNOWN-conflicts list and each agent's notes tell you where to look (W3/W4 band crossings with +24V drops at x0+21/x0+29; chain verticals at J4 x 361.38/356.3 crossing W3 bands; corridor lane collisions between the A/CTRL agent and the K/chains agent; any same-band different-net overlaps). Rules of engagement: the +24V trunk (y 2.2) and all SW-loop segments are SACRED (EM-critical) — reroute the other net around them, never the reverse. Prefer F.Cu jogs in documented free lanes; use B.Cu + vias when a jog would violate clearance; lane-reuse in disjoint x-ranges is allowed. Keep every net at its netclass width (brief has the table). You may freely re-route ANY non-sacred segment, including discarding an agent's path entirely and re-deriving it, as long as connectivity holds.
4. Iterate until DRC: 0 violations AND zero unconnected items for every net EXCEPT GND (GND pads will be connected by the zones agent's pour + vias).
5. The final ROUTES_EXTRA.json in ${PROJ} must be the exact one that produced the passing board.

Report final counts, remaining non-GND unconnected nets (should be none — list them if any), the conflicts you resolved and how, and notes (final lane map, deviations from the brief).`, { label: 'merge', schema: MERGE_SCHEMA })

const ZONES_SCHEMA = {
  type: 'object',
  properties: {
    zones_added: { type: 'number' },
    vias_added: { type: 'number' },
    drc_violations_final: { type: 'number' },
    unconnected_final: { type: 'number' },
    pour_fragmented: { type: 'boolean' },
    notes: { type: 'string' }
  },
  required: ['zones_added', 'vias_added', 'drc_violations_final', 'unconnected_final', 'pour_fragmented', 'notes']
}

phase('Zones')
log('adding GND pour, thermal islands, stitching vias...')
const zones = await agent(`You are the zones agent for the aquarium_v0 driver PCB. READ ${BRIEF} first. Work in the REAL project directory: ${PROJ}. The board is fully routed for all non-GND nets (ROUTES_EXTRA.json merged; DRC 0 violations; only GND pads unconnected). Merge report: ${JSON.stringify(merge)}

Your job — extend gen_pcb.py (it is THE generator; keep its deterministic style: L()/U()/fmt() helpers, data tables, self-asserts):
1. Add an emit_zones() that writes:
   a. ONE B.Cu GND zone covering the full board EXCEPT the bottom corridor: outline y 0.5..16.5 (x 0.5..579.5) — the corridor y 16.8-19.5 carries signal traffic and must stay OUTSIDE the pour (this is a documented deviation from an unbroken pour; note it). Net GND, priority 1, fill with thermal reliefs (thermal_gap 0.5, thermal_bridge_width 0.5), min thickness 0.2. Zones are authored as outline + (fill yes ...) with NO filled_polygon — the refill step computes fills.
   b. 7 F.Cu thermal islands (priority 2, net GND), one per driver cell: a small rectangle around each TSOT-23-5, roughly x0+15.5..x0+21.5 by y 7.6..12.4 — EXCLUDE the region by checking against actual routed tracks: the fill respects clearances automatically, so just make the island generous; same net GND so it bridges U pin2.
2. GND connectivity: for EVERY GND pad on F.Cu (logic cluster: J1.2, U8.2, U8.4, U9.1, C1.1, C2.2, C3.1, C4.1, J6.5, R5-R8 pin1; per cell: U pin2, C100n pin1, C22uF pin1) add a short F.Cu stub + a 0.5/0.3 via placed in FREE copper (>=0.4mm from any foreign track/pad, >=1mm from MH holes, not inside pad copper) so the pad reaches the B.Cu pour. Also J7 has no GND pad (switch loop) — skip.
3. Thermal stitching: 8-12 GND vias per driver cell scattered across the F.Cu island + nearby B.Cu pour area, in free space (check against ROUTES_EXTRA tracks; vias may sit inside the island zone since fill avoids them... no — vias ARE GND so fill connects TO them; place them where B.Cu below is pour, i.e. y < 16.5, and >=0.4mm from signal tracks).
4. Also add these vias/stubs INTO the generator (emit_zones or a new emit_gnd()) — NOT into ROUTES_EXTRA.json (that file belongs to the signal routing). Regenerate: python gen_pcb.py.
5. Refill + persist + final gate: "C:/Users/Akshat Jagdev/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe" pcb drc --refill-zones --save-board --format json -o drc.json aquarium_v0.kicad_pcb — iterate until 0 violations AND 0 unconnected items TOTAL (GND pads now connected via pour). If min_resolved_spokes complains about a tight thermal relief, add a via near that pad or move the stub.
6. Sanity: after the passing save, reload the board with the bundled python (pcbnew.LoadBoard) and check the B.Cu GND zone's filled polygons form one connected region (or at most a few large islands — count them; if the corridor carve or a via stub splits it into many fragments, report pour_fragmented=true and explain).

Report zones_added, vias_added, final DRC counts, pour fragmentation, and notes (what you changed in gen_pcb.py, deviations).`, { label: 'zones+gnd', schema: ZONES_SCHEMA })

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    lens: { type: 'string' },
    pass: { type: 'boolean' },
    findings: { type: 'array', items: { type: 'object', properties: {
      severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
      description: { type: 'string' },
      location: { type: 'string' }
    }, required: ['severity', 'description', 'location'] } }
  },
  required: ['lens', 'pass', 'findings']
}

phase('Verify')
log('adversarial verify panel: 5 lenses on the finished board...')
const LENSES = [
  { id: 'parity', prompt: `LENS: schematic parity + pad-net audit. In ${PROJ}: run kicad-cli pcb drc --schematic-parity --format json -o parity.json aquarium_v0.kicad_pcb (binary: C:/Users/Akshat Jagdev/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe). Then, with the bundled python (C:/Users/Akshat Jagdev/AppData/Local/Programs/KiCad/10.0/bin/python.exe) + pcbnew.LoadBoard, audit EVERY (ref, pin) pair in netlist.net against the board pad's net name — any mismatch is a finding (this catches overlay/injection bugs). Also confirm all 44 netlist nets exist on the board and every footprint 1-1 matches a netlist comp. Default to reporting a finding if uncertain. Do NOT modify anything.` },
  { id: 'connectivity', prompt: `LENS: connectivity + netclass widths. In ${PROJ}: parse drc.json (regenerate it if absent) — confirm 0 violations, 0 unconnected items. With bundled python + pcbnew: for every track, look up its net's netclass in aquarium_v0.kicad_pro (net_settings.classes + netclass_assignments) and verify width >= netclass track_width (+24V and Net-(Ux-SW) 0.5, _A nets 1.0, _K nets 0.8); every via drill >= 0.3 / dia >= 0.5. Also verify no net is routed ONLY on one layer with a dangling via pair (a via with no track on one side is fine ONLY if the other side connects into a zone fill). Do NOT modify anything.` },
  { id: 'fab', prompt: `LENS: JLCPCB manufacturability. In ${PROJ}: verify copper-edge clearance >= 0.3 everywhere (drc.json copper_edge_clearance entries would appear as violations — also spot-check the outermost tracks/pads near x 0/580 and y 0/20 with pcbnew), hole-to-hole >= 0.3 (MH holes vs nearby pads/vias), min annular ring, silk text height >= 0.8mm. ALSO adversarially review the ignore list in aquarium_v0.kicad_pro rule_severities (lib_footprint_mismatch, silk_over_copper, silk_overlap, silk_edge_clearance are ignored): for each, argue whether ignoring it could hide a REAL manufacturing or assembly problem on THIS board (e.g. silk over pads hiding pin-1 marks that an assembler needs — check where the J2-J5 pin-1 dots and + / - marks actually sit relative to pads). Report findings with severity. Do NOT modify anything.` },
  { id: 'quality', prompt: `LENS: analog/EM layout quality (this is a 7-channel buck LED driver). In ${PROJ} with bundled python + pcbnew, measure and judge: (1) SW loop area per channel — the D anode -> U pin1 -> L pad1 -> C22uF loop should be small; estimate from actual track paths (rough polygon area); (2) decoupling distance rules from the brief: C100n pin2 <= 2mm and C22uF pin2 <= 5mm from U pin5 pad edge per cell — MEASURE all 7 cells; (3) CTRL routing (B.Cu corridor) vs SW nodes (F.Cu) separation; (4) per-driver thermal vias 8-12 and F.Cu island exists (zone present with fills on F.Cu); (5) B.Cu GND pour connectivity: count disjoint filled islands of the GND zone — flag if fragmented; (6) the +24V trunk: single continuous path from J7.2 to every cell, no neckdowns below 0.5mm. Report each measurement and any failure as a finding. Do NOT modify anything.` },
  { id: 'repro', prompt: `LENS: reproducibility + code review. In a SCRATCH COPY (cp -r "${PROJ}" "C:/Users/Akshat Jagdev/AppData/Local/Temp/aquar_verify_repro" — never touch the real dir): delete aquarium_v0.kicad_pcb, run python gen_pcb.py, refill (kicad-cli pcb drc --refill-zones --save-board), and confirm the regenerated board passes DRC identically (0 violations / 0 unconnected) — this proves gen_pcb.py + ROUTES_EXTRA.json are a complete deterministic source. Then code-review gen_pcb.py (and ROUTES_EXTRA.json): correctness bugs, dead code, non-determinism (uuid randomness is expected/OK), fragile parsing, and whether the overlay zone/via additions follow the file's established style. Also confirm the .kicad_pro netclass_assignments cover every routed power net. Findings only for real defects. Do NOT modify the real project.` },
]
const verdicts = (await parallel(LENSES.map(l => () =>
  agent(`${l.prompt}\n\nREAD ${BRIEF} for context. You are an adversarial verifier — your job is to REFUTE the claim that this board is done. Report pass=false if any critical/major finding survives your own double-check. Include exact locations (mm coords or file:line) for every finding.`, { label: 'verify:' + l.id, phase: 'Verify', schema: VERDICT_SCHEMA })
))).filter(Boolean)

return {
  route_groups: routeResults.map(r => ({ notes: r.notes, drc: r.drc_violations_final, unconnected: r.my_nets_unconnected_final, routes: r.routes.length, vias: r.vias.length })),
  merge, zones, verdicts
}