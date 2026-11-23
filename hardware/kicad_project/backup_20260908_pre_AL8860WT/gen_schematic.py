#!/usr/bin/env python3
"""
Generate the ColorBoost V0 driver-strip schematic (KiCad 8 .kicad_sch).

Self-contained: every symbol is embedded in the schematic's lib_symbols
section (custom 'aquarium' library + power symbols), so the file opens in
any KiCad 8/9 install with no external libraries.

Sources:
  docs/03_schematic_text.md          - audited circuit topology
  docs/05_kicad_spec.md              - schematic requirements
  hardware/mechanical/pcb_layout_notes.md  - J1..J7 pinouts

Run:  python gen_schematic.py
Out:  aquarium_v0.kicad_sch, aquarium_v0.kicad_pro (this folder)
"""
import json
import os
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
SCH_PATH = os.path.join(HERE, "aquarium_v0.kicad_sch")
PRO_PATH = os.path.join(HERE, "aquarium_v0.kicad_pro")

ROOT_UUID = str(uuid.uuid4())


def U():
    return str(uuid.uuid4())


out = []


def L(indent, text):
    out.append("\t" * indent + text)


# ---------------------------------------------------------------- helpers

def prop(name, value, x, y, hide=False):
    h = " (hide yes)" if hide else ""
    return ('(property "%s" "%s" (at %s %s 0) '
            '(effects (font (size 1.27 1.27))%s))' % (name, value, x, y, h))


def pin_def(x, y, ang, name, num, ptype="passive", length=25):
    return (f'(pin {ptype} line (at {x} {y} {ang}) (length {length}) '
            f'(name "{name}" (effects (font (size 1.27 1.27)))) '
            f'(number "{num}" (effects (font (size 1.27 1.27))))')


def gfx_rect(x1, y1, x2, y2, fill="none"):
    return (f'(rectangle (start {x1} {y1}) (end {x2} {y2}) '
            f'(stroke (width 0.254) (type default)) (fill (type {fill})))')


def gfx_poly(pts, fill="none", width=0.254):
    p = " ".join(f"(xy {x} {y})" for x, y in pts)
    return (f'(polyline (pts {p}) '
            f'(stroke (width {width}) (type default)) (fill (type {fill})))')


# ---------------------------------------------------------- lib symbols

def lib_header(name, power=False, pin_hide=False, pin_off=0.508):
    flags = []
    if power:
        flags.append("(power)")
    if pin_hide:
        flags.append("(pin_names hide)")
    else:
        flags.append(f"(pin_names (offset {pin_off}))")
    L(1, f'(symbol "{name}" ' + " ".join(flags) +
      " (exclude_from_sim no) (in_bom yes) (on_board yes)")


def lib_footer():
    L(1, ")")


def lib_2pin(name, ref_prefix, body_gfx, pin_type="passive"):
    """Vertical two-terminal symbol.

    KiCad maps symbol-local (sx, sy) to sheet (X+sx, Y-sy) at rot 0, i.e.
    symbol +y renders UP. pin1 conn at (0,0), pin2 conn at (0,100)."""
    lib_header(name)
    L(2, prop("Reference", ref_prefix, 0, 100, hide=True))
    L(2, prop("Value", name.split(":")[1], 0, 100, hide=True))
    L(2, prop("Footprint", "", 0, 0, hide=True))
    L(2, prop("Datasheet", "~", 0, 0, hide=True))
    L(2, f'(symbol "{name.split(":")[1]}_0_1"')
    for g in body_gfx:
        L(3, g)
    L(2, ")")
    L(2, f'(symbol "{name.split(":")[1]}_1_1"')
    L(3, pin_def(0, 0, 90, "~", "1", pin_type, length=40))
    L(3, pin_def(0, 100, 270, "~", "2", pin_type, length=40))
    L(2, ")")
    lib_footer()


def lib_conn(name, n):
    """N-pin single-row connector, pins on the left, 100 mil pitch."""
    short = name.split(":")[1]
    body = [gfx_rect(25, 50, 150, 100 * (n - 1) + 50, fill="background")]
    lib_header(name)
    L(2, prop("Reference", "J", 0, 100, hide=True))
    L(2, prop("Value", short, 0, 100, hide=True))
    L(2, prop("Footprint", "", 0, 0, hide=True))
    L(2, prop("Datasheet", "~", 0, 0, hide=True))
    L(2, f'(symbol "{short}_0_1"')
    for g in body:
        L(3, g)
    L(2, ")")
    L(2, f'(symbol "{short}_1_1"')
    for k in range(1, n + 1):
        L(3, pin_def(0, 100 * (k - 1), 0, str(k), str(k)))
    L(2, ")")
    lib_footer()


def lib_ic(name, ref_prefix, box, pins, pin_show=True):
    """box = (x1,y1,x2,y2); pins = list of (x,y,ang,name,num,type)."""
    short = name.split(":")[1]
    lib_header(name, pin_hide=not pin_show)
    L(2, prop("Reference", ref_prefix, 0, 100, hide=True))
    L(2, prop("Value", short, 0, 100, hide=True))
    L(2, prop("Footprint", "", 0, 0, hide=True))
    L(2, prop("Datasheet", "~", 0, 0, hide=True))
    L(2, f'(symbol "{short}_0_1"')
    L(3, gfx_rect(*box, fill="background"))
    L(2, ")")
    L(2, f'(symbol "{short}_1_1"')
    for (x, y, a, nm, num, pt) in pins:
        L(3, pin_def(x, y, a, nm, num, pt, length=100))
    L(2, ")")
    lib_footer()


def lib_power_rail(netname, ptype):
    """+24V/+5V/+3V3/PWR_FLAG: pin conn at (0,0), graphics extend UP
    (symbol +y renders up on sheet)."""
    lib_header(f"power:{netname}", power=True, pin_hide=True)
    L(2, prop("Reference", "#PWR", 0, 0, hide=True))
    L(2, prop("Value", netname, 0, 0, hide=True))
    L(2, prop("Footprint", "", 0, 0, hide=True))
    L(2, prop("Datasheet", "", 0, 0, hide=True))
    L(2, f'(symbol "{netname}_0_1"')
    L(3, pin_def(0, 0, 90, netname, "1", ptype))
    L(3, gfx_poly([(0, 25), (0, 75)]))
    L(3, gfx_poly([(-40, 75), (40, 75)]))
    L(2, ")")
    lib_footer()


def lib_power_gnd():
    """GND: pin conn at (0,0), graphics extend DOWN (symbol -y renders
    down on sheet)."""
    lib_header("power:GND", power=True, pin_hide=True)
    L(2, prop("Reference", "#PWR", 0, 0, hide=True))
    L(2, prop("Value", "GND", 0, 0, hide=True))
    L(2, prop("Footprint", "", 0, 0, hide=True))
    L(2, prop("Datasheet", "", 0, 0, hide=True))
    L(2, '(symbol "GND_0_1"')
    L(3, pin_def(0, 0, 270, "GND", "1", "power_in"))
    L(3, gfx_poly([(-50, -25), (50, -25)]))
    L(3, gfx_poly([(-35, -35), (35, -35)]))
    L(3, gfx_poly([(-20, -45), (20, -45)]))
    L(2, ")")
    lib_footer()


# -------------------------------------------------------- sheet objects

def wire(x1, y1, x2, y2):
    L(1, f'(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) '
      f'(stroke (width 0) (type default)) (uuid "{U()}"))')


def label(name, x, y, ang=0):
    just = "right" if ang == 180 else "left"
    L(1, f'(label "{name}" (at {x} {y} {ang}) '
      f'(effects (font (size 1.27 1.27)) (justify {just})) (uuid "{U()}"))')


def no_connect(x, y):
    L(1, f'(no_connect (at {x} {y}) (uuid "{U()}"))')


def note(text, x, y):
    L(1, f'(text "{text}" (at {x} {y} 0) '
      f'(effects (font (size 1.27 1.27)) (justify left top)) (uuid "{U()}"))')


def inst(lib_id, x, y, rot, ref, value, fp, pin_nums,
         ref_pos, val_pos):
    L(1, "(symbol")
    L(2, f'(lib_id "{lib_id}")')
    L(2, f'(at {x} {y} {rot})')
    L(2, "(unit 1)")
    L(2, "(exclude_from_sim no)")
    L(2, "(in_bom yes)")
    L(2, "(on_board yes)")
    L(2, "(dnp no)")
    L(2, f'(uuid "{U()}")')
    L(2, prop("Reference", ref, *ref_pos))
    L(2, prop("Value", value, *val_pos))
    L(2, prop("Footprint", fp, x, y, hide=True))
    L(2, prop("Datasheet", "~", x, y, hide=True))
    for p in pin_nums:
        L(2, f'(pin "{p}" (uuid "{U()}"))')
    L(1, ")")


def comp2(lib_id, x, y, ref, value, fp):
    """Vertical 2-pin part: pin1 Bottom at (x,y), pin2 top at (x,y-100)."""
    inst(lib_id, x, y, 0, ref, value, fp, ["1", "2"],
         (x - 150, y - 50), (x - 150, y + 50))


def conn(lib_id, x, y, ref, value, fp, n):
    """Connector: pin k at (x, y-100*(k-1)), body to the right."""
    inst(lib_id, x, y, 0, ref, value, fp, [str(k) for k in range(1, n + 1)],
         (x + 200, y - 100 * (n - 1) // 2), (x + 200, y - 100 * (n - 1) // 2 + 100))


_pwr_n = [0]


def pwr(net, x, y):
    """Power symbol stacked directly on a pin at (x,y)."""
    _pwr_n[0] += 1
    is_gnd = (net == "GND")
    L(1, "(symbol")
    L(2, f'(lib_id "power:{net}")')
    L(2, f'(at {x} {y} 0)')
    L(2, "(unit 1)")
    L(2, "(exclude_from_sim no)")
    L(2, "(in_bom yes)")
    L(2, "(on_board yes)")
    L(2, "(dnp no)")
    L(2, f'(uuid "{U()}")')
    L(2, prop("Reference", f"#PWR{_pwr_n[0]:04d}", x, y, hide=True))
    L(2, prop("Value", net, x, y + 100 if is_gnd else y - 100))
    L(2, prop("Footprint", "", x, y, hide=True))
    L(2, prop("Datasheet", "", x, y, hide=True))
    L(2, f'(pin "1" (uuid "{U()}"))')
    L(1, ")")


# ------------------------------------------------------------ footprints

R0603 = "Resistor_SMD:R_0603_1608Metric"
R2512 = "Resistor_SMD:R_2512_6332Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C1210 = "Capacitor_SMD:C_1210_3225Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
CETHT = "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm"
L12 = "Inductor_SMD:L_12x12mm_H8mm"
DSMA = "Diode_SMD:D_SMA"
SOT236 = "Package_TO_SOT_SMD:SOT-23-6"
SOT223 = "Package_TO_SOT_SMD:SOT-223-3"
PH2 = "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"
PH6 = "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical"
CUSTOM = ""  # custom footprint to be drawn before layout

# ---------------------------------------------------------------- build

L(0, "(kicad_sch")
L(1, "(version 20231120)")
L(1, '(generator "eeschema")')
L(1, '(generator_version "8.0")')
L(1, f'(uuid "{ROOT_UUID}")')
L(1, '(paper "A3")')
L(1, "(title_block")
L(2, '(title "ColorBoost V0 - LED Driver Strip (7x AL8860)")')
L(2, '(date "2026-09-08")')
L(2, '(rev "V0.1")')
L(2, '(company "aquarium_v0")')
L(2, '(comment 1 "Sources: docs/03_schematic_text.md, docs/05_kicad_spec.md, '
  'hardware/mechanical/pcb_layout_notes.md")')
L(1, ")")

# ---- lib_symbols ----
L(1, "(lib_symbols")

# resistor (also used for 0-ohm style parts)
lib_2pin("aquarium:R", "R", [gfx_rect(-30, 40, 30, 60)])
# capacitor (ceramic, unpolarised)
lib_2pin("aquarium:C", "C", [gfx_poly([(-30, 40), (30, 40)]),
                             gfx_poly([(-30, 60), (30, 60)])])
# electrolytic (polarised: curved bottom plate + + marker)
lib_2pin("aquarium:CP", "C", [gfx_poly([(-30, 40), (30, 40)]),
                              gfx_poly([(-30, 60), (30, 60), (0, 40),
                                        (-30, 60)])])
# inductor
lib_2pin("aquarium:L", "L", [gfx_rect(-30, 40, 30, 60)])
# schottky diode: anode pin1 (bottom), cathode pin2 (top)
lib_2pin("aquarium:D_Schottky", "D",
         [gfx_poly([(-30, 30), (30, 30), (0, 70), (-30, 30)], fill="outline"),
          gfx_poly([(-30, 70), (30, 70)])])
# fuse
lib_2pin("aquarium:Fuse", "F",
         [gfx_rect(-30, 35, 30, 65), gfx_poly([(0, 25), (0, 75)])])

lib_conn("aquarium:Conn_01x02", 2)
lib_conn("aquarium:Conn_01x06", 6)

# AL8860 (SOT-23-6): 1=LX 2=GND 3=NC 4=CS 5=CTRL 6=VIN
lib_ic("aquarium:AL8860", "U", (-300, -200, 300, 400), [
    (-400, 300, 0,   "VIN",   "6", "power_in"),
    (-400, 100, 0,   "GND",   "2", "power_in"),
    (-400, -100, 0,  "CTRL",  "5", "passive"),
    (400,  300, 180, "LX",    "1", "passive"),
    (400,  100, 180, "NC",    "3", "passive"),
    (400,  -100, 180, "CS",   "4", "passive"),
])

# AMS1117-3.3 (SOT-223): 1=GND 2=VOUT 3=VIN
lib_ic("aquarium:AMS1117", "U", (-300, 200, 300, 800), [
    (-400, 300, 0,   "VI",  "3", "power_in"),
    (400,  300, 180, "VO",  "2", "power_out"),
    (0,    100, 90,  "GND", "1", "power_in"),
])

# IRM-02-5 module: 1=+VIN 2=-VIN 3=+VOUT 4=-VOUT  (VERIFY vs datasheet)
lib_ic("aquarium:IRM-02-5", "U", (-300, 200, 300, 700), [
    (-400, 300, 0,   "+VIN", "1", "power_in"),
    (-400, 500, 0,   "-VIN", "2", "power_in"),
    (400,  300, 180, "+VOUT", "3", "power_out"),
    (400,  500, 180, "-VOUT", "4", "power_in"),
])

lib_power_gnd()
lib_power_rail("+24V", "power_in")
lib_power_rail("+5V", "power_in")
lib_power_rail("+3V3", "power_in")
lib_power_rail("PWR_FLAG", "power_out")
L(1, ")")

# ---- notes / section headers ----
note("POWER INPUT: J1 (panel jack leads) -> F1 2A slow-blow -> J7 (panel switch loop) -> +24V bus",
     1000, 1900)
note("LOGIC POWER: IRM-02-5 24V->5V, AMS1117 5V->3V3. VERIFY IRM-02-5 PINOUT VS DATASHEET.",
     1000, 3700)
note("ESP32-C3 SuperMini plugs onto J6. GPIO0-3 -> 1k -> CTRL_x; 100k pull-downs keep LEDs off during boot.",
     1000, 6300)
note("LED DRIVER CHANNELS (7x AL8860). D cathode to +24V (flyback), L -> header -> LED string, CS pin senses at RSET top.",
     4200, 1700)
note("MCPCB HEADERS: J2-J5 -> LED boards. Red chain J2>J3>J4>J5, blue J2>J3, deep-red J4>J5 (series joins on this PCB).",
     4200, 6700)
note("AL8860 VARIANT: audited design uses AL8860W6-7 SOT-23-6. LCSC_TRUTH_BOM lists AL8860WT-7 SOP-8 (C125330) - RECONCILE BEFORE PCB ORDER.",
     1000, 11500)

# ============================================================ POWER INPUT
# J1: DC 24V in
conn("aquarium:Conn_01x02", 1500, 2500, "J1", "DC 24V IN", PH2, 2)
wire(1500, 2500, 1500, 2600)
label("VIN_RAW", 1500, 2600)
pwr("GND", 1500, 2400)
pwr("PWR_FLAG", 1500, 2400)

# F1: fuse
comp2("aquarium:Fuse", 2200, 2500, "F1", "2A slow-blow", CUSTOM)
wire(2200, 2500, 2200, 2600)
label("VIN_RAW", 2200, 2600)
wire(2200, 2400, 2200, 2300)
label("SW_A", 2200, 2300)

# J7: panel switch loop
conn("aquarium:Conn_01x02", 2900, 2500, "J7", "SW LOOP", PH2, 2)
wire(2900, 2500, 2900, 2600)
label("SW_A", 2900, 2600)
pwr("+24V", 2900, 2400)
pwr("PWR_FLAG", 2900, 2400)

# input caps
comp2("aquarium:C", 3600, 2500, "C1", "100nF", C0603)
pwr("+24V", 3600, 2400)
pwr("GND", 3600, 2500)
comp2("aquarium:CP", 3900, 2500, "C2", "220uF/50V", CETHT)
pwr("+24V", 3900, 2400)
pwr("GND", 3900, 2500)

# ============================================================ LOGIC POWER
# U8: IRM-02-5
inst("aquarium:IRM-02-5", 2200, 4500, 0, "U8", "IRM-02-5", CUSTOM,
     ["1", "2", "3", "4"], (2200, 4750), (2200, 4850))
wire(1800, 4200, 1700, 4200)
pwr("+24V", 1700, 4200)
wire(1800, 4000, 1700, 4000)
pwr("GND", 1700, 4000)
wire(2600, 4200, 2700, 4200)
pwr("+5V", 2700, 4200)
wire(2600, 4000, 2700, 4000)
pwr("GND", 2700, 4000)

# C3: 1uF on +5V
comp2("aquarium:C", 3100, 4200, "C3", "1uF", C0805)
pwr("+5V", 3100, 4100)
pwr("GND", 3100, 4200)

# U9: AMS1117-3.3
inst("aquarium:AMS1117", 3900, 4500, 0, "U9", "AMS1117-3.3", SOT223,
     ["1", "2", "3"], (3900, 3400), (3900, 3500))
wire(3500, 4200, 3400, 4200)
pwr("+5V", 3400, 4200)
wire(4300, 4200, 4400, 4200)
pwr("+3V3", 4400, 4200)
pwr("GND", 3900, 4400)

# C4: 1uF on +3V3
comp2("aquarium:C", 4800, 4200, "C4", "1uF", C0805)
pwr("+3V3", 4800, 4100)
pwr("GND", 4800, 4200)

# ======================================================== ESP32 INTERFACE
# J6: ESP32-C3 SuperMini header
conn("aquarium:Conn_01x06", 1500, 7500, "J6", "ESP32-C3", PH6, 6)
wire(1500, 7500, 1400, 7500)
label("PWM_W", 1400, 7500, 180)
wire(1500, 7400, 1400, 7400)
label("PWM_R", 1400, 7400, 180)
wire(1500, 7300, 1400, 7300)
label("PWM_B", 1400, 7300, 180)
wire(1500, 7200, 1400, 7200)
label("PWM_DR", 1400, 7200, 180)
pwr("GND", 1500, 7100)
pwr("+3V3", 1500, 7000)

# R1-R4: 1k series (GPIO -> CTRL). Row pitch 400 (not 300): at 300 the
# pwm label of row i (ry-200) lands on the same point as the ctrl label
# of row i+1 ((ry-300)+100), merging the two nets.
for i, (ry, pwm, ctrl) in enumerate([
        (7500, "PWM_W", "CTRL_W"),
        (7100, "PWM_R", "CTRL_R"),
        (6700, "PWM_B", "CTRL_B"),
        (6300, "PWM_DR", "CTRL_DR")]):
    comp2("aquarium:R", 2500, ry, f"R{i+1}", "1k", R0603)
    wire(2500, ry - 100, 2500, ry - 200)
    label(pwm, 2500, ry - 200)
    wire(2500, ry, 2500, ry + 100)
    label(ctrl, 2500, ry + 100)

# R5-R8: 100k pull-downs (CTRL -> GND), same 400 pitch as R1-R4
for i, (ry, ctrl) in enumerate([
        (7500, "CTRL_W"),
        (7100, "CTRL_R"),
        (6700, "CTRL_B"),
        (6300, "CTRL_DR")]):
    comp2("aquarium:R", 3100, ry, f"R{i+5}", "100k", R0603)
    wire(3100, ry - 100, 3100, ry - 200)
    label(ctrl, 3100, ry - 200)
    pwr("GND", 3100, ry)

# ===================================================== DRIVER CHANNELS x7
CHANNELS = [
    # (uref, lref, dref, c22, chf, rset, rset_val, net, ctrl)
    ("U1", "L1", "D1", "C10", "C20", "R10", "0.40R", "W1", "CTRL_W"),
    ("U2", "L2", "D2", "C11", "C21", "R11", "0.40R", "W2", "CTRL_W"),
    ("U3", "L3", "D3", "C12", "C22", "R12", "0.40R", "W3", "CTRL_W"),
    ("U4", "L4", "D4", "C13", "C23", "R13", "0.40R", "W4", "CTRL_W"),
    ("U5", "L5", "D5", "C14", "C24", "R14", "0.82R", "R", "CTRL_R"),
    ("U6", "L6", "D6", "C15", "C25", "R15", "0.33R", "B", "CTRL_B"),
    ("U7", "L7", "D7", "C16", "C26", "R16", "0.82R", "DR", "CTRL_DR"),
]

for i, (uref, lref, dref, c22, chf, rset, rset_val, net, ctrl) in enumerate(CHANNELS):
    cx = 4500 + 1500 * i
    base = 3000  # IC origin y

    # AL8860
    inst("aquarium:AL8860", cx, base, 0, uref, "AL8860W6-7", SOT236,
         ["1", "2", "3", "4", "5", "6"], (cx, 3250), (cx, 3350))

    # VIN pin (cx-400, 2700): power stack; GND pin (cx-400, 2900)
    pwr("+24V", cx - 400, 2700)
    pwr("GND", cx - 400, 2900)

    # CTRL pin (cx-400, 3100)
    wire(cx - 400, 3100, cx - 500, 3100)
    label(ctrl, cx - 500, 3100, 180)

    # NC pin
    no_connect(cx + 400, 2900)

    # LX pin (cx+400,2700) -> D anode tap -> L pin2 (cx+700,2700).
    # Two segments: KiCad only connects pins at wire endpoints, so the
    # D anode (cx+550,2700) must be an endpoint, not a mid-wire tap.
    wire(cx + 400, 2700, cx + 550, 2700)
    wire(cx + 550, 2700, cx + 700, 2700)
    comp2("aquarium:D_Schottky", cx + 550, 2700, dref, "SS3100", DSMA)
    pwr("+24V", cx + 550, 2600)          # D cathode
    comp2("aquarium:L", cx + 700, 2800, lref, "68uH", L12)
    wire(cx + 700, 2800, cx + 700, 2900)
    label(f"{net}_A", cx + 700, 2900)

    # CS pin (cx+400,3100) -> RSET top; label = string cathode return
    wire(cx + 400, 3100, cx + 900, 3100)
    label(f"{net}_K", cx + 650, 3100)
    comp2("aquarium:R", cx + 900, 3200, rset, rset_val, R2512)
    pwr("GND", cx + 900, 3200)

    # input caps (left of IC)
    comp2("aquarium:C", cx - 800, 2200, chf, "100nF", C0603)
    pwr("+24V", cx - 800, 2100)
    pwr("GND", cx - 800, 2200)
    comp2("aquarium:C", cx - 800, 2600, c22, "22uF", C1210)
    pwr("+24V", cx - 800, 2500)
    pwr("GND", cx - 800, 2600)

# ======================================================== MCPCB HEADERS
HEADERS = [
    ("J2", "MCPCB1 (L1, blue)", 4500,
     ["W1_A", "W1_K", "R_A", "R_J23", "B_A", "B_J23"]),
    ("J3", "MCPCB2 (L2, blue)", 6500,
     ["W2_A", "W2_K", "R_J23", "R_J34", "B_J23", "B_K"]),
    ("J4", "MCPCB3 (R1, deep-red)", 8500,
     ["W3_A", "W3_K", "R_J34", "R_J45", "DR_A", "DR_J45"]),
    ("J5", "MCPCB4 (R2, deep-red)", 10500,
     ["W4_A", "W4_K", "R_J45", "R_K", "DR_J45", "DR_K"]),
]

for ref, val, hx, nets in HEADERS:
    conn("aquarium:Conn_01x06", hx, 7500, ref, val, PH6, 6)
    for k, netname in enumerate(nets):
        py = 7500 - 100 * k
        wire(hx, py, hx - 100, py)
        label(netname, hx - 100, py, 180)

L(1, "(sheet_instances")
L(2, '(path "/" (page "1"))')
L(1, ")")
L(0, ")")

with open(SCH_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

# ---------------------------------------------------------------- .kicad_pro
pro = {
    "boards": [],
    "cvpcb": {"equivalence_files": []},
    "libraries": {"pinned_symbol_libs": [], "pinned_footprint_libs": []},
    "meta": {"filename": "aquarium_v0.kicad_pro", "version": 1},
    "net_settings": {
        "classes": [
            {"name": "Default", "bus_width": 12, "clearance": 0.2,
             "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
             "diff_pair_width": 0.2, "track_width": 0.25,
             "via_diameter": 0.8, "via_drill": 0.4, "wire_width": 6},
            {"name": "Power_24V", "bus_width": 12, "clearance": 0.3,
             "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
             "diff_pair_width": 0.2, "track_width": 0.5,
             "via_diameter": 0.8, "via_drill": 0.4, "wire_width": 6},
            {"name": "LED_Anode", "bus_width": 12, "clearance": 0.3,
             "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
             "diff_pair_width": 0.2, "track_width": 1.0,
             "via_diameter": 0.8, "via_drill": 0.4, "wire_width": 6},
            {"name": "LED_Cathode", "bus_width": 12, "clearance": 0.3,
             "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
             "diff_pair_width": 0.2, "track_width": 0.8,
             "via_diameter": 0.8, "via_drill": 0.4, "wire_width": 6},
        ],
        "meta": {"version": 3},
        "netclass_assignments": None,
        "netclass_patterns": [],
    },
    "pcbnew": {"last_paths": {}, "page_layout_descr_file": ""},
    "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
    "sheets": [[ROOT_UUID, ""]],
    "text_variables": {},
}
with open(PRO_PATH, "w", encoding="utf-8") as f:
    json.dump(pro, f, indent=2)

print(f"wrote {SCH_PATH}")
print(f"wrote {PRO_PATH}")
print(f"objects: {len(out)} lines")