#!/usr/bin/env python3
"""Printable perfboard placement map - ColorBoost V0 prototype (830-pt solderable BB)."""
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PROTO_MAP.html")

# ref, name, rail, ctrl, rset, L, Vstring, c0 (first column of 6-col block, top bank)
CH = [("U1","WHITE 1","+24V","CTRL_W","0.40 Ω","68 µH","≈17.6 V",1),
      ("U2","WHITE 2","+24V","CTRL_W","0.40 Ω","68 µH","≈17.6 V",7),
      ("U3","WHITE 3","+24V","CTRL_W","0.40 Ω","68 µH","≈17.6 V",13),
      ("U4","WHITE 4","+24V","CTRL_W","0.40 Ω","68 µH","≈17.6 V",19),
      ("U5","RED","+12V","CTRL_R","0.82 Ω","68 µH","≈8.0 V",25),
      ("U6","BLUE","+12V","CTRL_B","0.33 Ω","68 µH","≈6.4 V",31),
      ("U7","DEEP-RED","+12V","CTRL_DR","0.82 Ω","100 µH","≈4.4 V",37)]

def tmpl(c0, ref, rail, ctrl, rset, L):
    r = [f"{c0}","f{c0+1}"] # placeholder
    rows = []
    def hole(col,row): return f"({c0+col},{row})"
    items = [
      ("Rail jumper",  f"{rail} rail → {hole(0,'a')}", "22AWG"),
      ("C 22µF/50V 1210", f"{hole(0,'a')} – {hole(1,'a')}", "spans 2 cols"),
      ("C 100nF",      f"{hole(0,'b')} – {hole(1,'b')}", "spans 2 cols"),
      (f"SS3100 (SMA)", f"cathode(band) {hole(0,'d')} – anode {hole(2,'d')}", "extend 1 leg w/ wire"),
      (f"{ref} AL8860 dead-bug", f"glue body over cols {c0+1}…{c0+4}; legs → p5 {hole(0,'e')} · p2 {hole(1,'e')} · p1 {hole(2,'e')} · p4 {hole(3,'e')} · p3 {hole(5,'e')}", "30AWG legs"),
      (f"RSET {rset} 2512", f"pigtail top {hole(0,'c')} – pigtail bottom {hole(3,'c')}", "floats, 2 wire pigtails"),
      (f"L {L}", f"leg1 {hole(2,'c')} – leg2 {hole(4,'b')}", "leg wires + hot glue"),
      ("LED string +",  f"{hole(3,'d')} (anode, = SET net)", "offboard"),
      ("LED string −",  f"{hole(4,'c')} (cathode)", "offboard"),
      (f"{ctrl} wire in", f"from logic section → {hole(5,'c')}", "30AWG"),
    ]
    return items

def svg_board():
    # 63 cols x (rails 2 + a..e + center + f..j + rails 2). scale 11px/col
    W = 63*11 + 90
    parts = [f'<svg viewBox="0 0 {W} 250" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{W}px">']
    parts.append('<rect x="0" y="0" width="%d" height="250" fill="#fafafa" stroke="#999"/>' % W)
    def bank(y0, label):
        parts.append(f'<text x="8" y="{y0+14}" font-size="10" font-weight="bold">{label}</text>')
        for c in range(63):
            for r in range(5):
                parts.append(f'<circle cx="{90+c*11+5}" cy="{y0+10+r*9}" r="2.2" fill="#ccc"/>')
    def rails(y0, label, col="#c0392b"):
        parts.append(f'<text x="8" y="{y0+9}" font-size="9" font-weight="bold">{label}</text>')
        for c in range(63):
            parts.append(f'<circle cx="{90+c*11+5}" cy="{y0+5}" r="2.2" fill="{col}"/>')
    rails(8,  "+24V", "#c0392b"); rails(22, "GND", "#333")
    bank(38, "a–e")
    bank(128, "f–j")
    rails(192, "GND", "#333"); rails(206, "+12V", "#e67e22")
    blocks = [("CH1 W",0,6,"#3498db"),("CH2 W",7,12,"#3498db"),("CH3 W",13,18,"#3498db"),
              ("CH4 W",19,24,"#3498db"),("CH5 R",25,30,"#e74c3c"),("CH6 B",31,36,"#2980b9"),
              ("CH7 DR",37,42,"#8e44ad"),("U10 LM2596",43,50,"#27ae60")]
    for name,c1,c2,col in blocks:
        x = 90+c1*11; w = (c2-c1)*11
        parts.append(f'<rect x="{x}" y="36" width="{w}" height="52" fill="{col}" opacity="0.25" stroke="{col}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x+w/2}" y="65" font-size="8.5" text-anchor="middle" font-weight="bold" fill="{col}">{name}</text>')
        parts.append(f'<text x="{x+w/2}" y="78" font-size="7" text-anchor="middle" fill="{col}">cols {c1+1}–{c2}</text>')
    bb = [("PWR J1 F1 J7 C1 C2",0,8,"#f39c12"),("5V/3V3 LDOs + C3 C4",9,12,"#16a085"),
          ("J6 ESP32 header",12,18,"#7f8c8d"),("PWM/CTRL R1–R8",18,26,"#2c3e50"),
          ("TP loops",27,34,"#d35400")]
    for name,c1,c2,col in bb:
        x = 90+c1*11; w = (c2-c1)*11
        parts.append(f'<rect x="{x}" y="126" width="{w}" height="52" fill="{col}" opacity="0.2" stroke="{col}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x+w/2}" y="150" font-size="7.5" text-anchor="middle" font-weight="bold" fill="{col}">{name}</text>')
        parts.append(f'<text x="{x+w/2}" y="162" font-size="7" text-anchor="middle" fill="{col}">cols {c1+1}–{c2}</text>')
    for c in (5,10,15,20,25,30,35,40,45,50,55,60):
        parts.append(f'<text x="{90+c*11+5}" y="248" font-size="7" text-anchor="middle" fill="#666">{c+1}</text>')
    parts.append('</svg>')
    return "".join(parts)

def table(headers, rows, cls=""):
    h = "".join(f"<th>{x}</th>" for x in headers)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'

ch_rows = []
for ref,name,rail,ctrl,rset,L,vs,c0 in CH:
    ch_rows.append([f"<b>{ref}</b> {name}", f"{c0}–{c0+5}", rail, ctrl, rset, L,
                    f"A=({c0+3},d) · K=({c0+4},c)", vs,
                    "100 mV / RSET → " + ("250 mA" if rail=="+24V" else {"CTRL_R":"122 mA","CTRL_B":"303 mA","CTRL_DR":"122 mA"}[ctrl])])

CH1 = CH[0]
card = table(["Item","Where","Note"], tmpl(1, *CH1[0:1], *CH1[2:6]) if False else tmpl(1, CH1[0], CH1[2], CH1[3], CH1[4], CH1[5]))

power_rows = [
 ["col 1 (f–j)","VIN_RAW — DC jack 24V+ wire into (1,f)"],
 ["col 2 (f–j)","SW_A — F1 2A fuse body/clip from (1,h) to (2,h)"],
 ["col 3 (f–j)","GND — jack − wire into (3,f); jumper to BOT-inner GND rail"],
 ["col 4 (f–j)","+24V — jumper (4,f) → TOP-outer rail; rocker switch (J7) pigtails (2,i)→(4,i)"],
 ["C1 100nF","spans (4,f)–(3,f)"],
 ["C2 220µF/50V","spans (4,g)–(3,g), + leg at col 4"],
]
logic_rows = [
 ["col 10","+5V — U8 module OUT+ (see ⚠ IRM note) → (10,f); C3 1µF spans (10,f)–(11,f)"],
 ["col 11","GND — jumper to BOT-inner rail"],
 ["col 12","+3V3 — U9 AMS1117: pin3 IN→(10,g), pin2 OUT→(12,g), pin1 GND→(11,g); C4 1µF spans (12,f)–(11,f)"],
 ["cols 13–18","J6 ESP32-C3 6 wires: 13=PWM_W 14=PWM_R 15=PWM_B 16=PWM_DR 17=GND(jumper) 18=+3V3(jumper from col 12)"],
 ["cols 19,21,23,25","CTRL_W, CTRL_R, CTRL_B, CTRL_DR"],
 ["cols 20,22,24,26","GND (jumper together to rail)"],
 ["R1–R4 1k","PWM col → matching CTRL col: 13→19, 14→21, 15→23, 16→25 (pigtail span)"],
 ["R5–R8 100k","CTRL col → next GND col: 19→20, 21→22, 23→24, 25→26 (adjacent span)"],
 ["cols 28–33","TP wire loops: 28=+24V 29=GND 30=+12V 31=+5V 32=+3V3 33=CTRL_W"],
]
u10_rows = [
 ["col 43 (a–e)","+24V in — jumper from TOP-outer rail; module IN+ wire → (43,a)"],
 ["col 44 (a–e)","GND — jumper from TOP-inner rail; module IN− → (44,a)"],
 ["col 45 (a–e)","+12V OUT+ → (45,a); jumper (45,b) down to BOT-outer +12V rail"],
 ["col 46 (a–e)","GND OUT− → (46,a); jumper to TOP-inner GND rail"],
 ["C12V 22µF 1210","spans (45,a)–(46,a) (supersedes schematic 10µF)"],
 ["Cross-bank wires","+12V rail → (25,a), (31,a), (37,a) · CTRL_W col 19 → (6,c),(12,c),(18,c),(24,c) · CTRL_R 21 → (30,c) · CTRL_B 23 → (36,c) · CTRL_DR 25 → (42,c)"],
]


def exact_rows():
    rows = []
    for i,(ref,name,rail,ctrl,rset,L,vs,c0) in enumerate(CH):
        c=c0
        rows.append([f"<b>{ref}</b>",f"AL8860WT-7 SOT-23-6, dead-bug, glue cols {c0}-{c0+5}",
                     f"p5>({c},e) · p2>({c+1},e) · p1>({c+2},e) · p4>({c+3},e) · p3>({c+5},e) · p6 NC"])
        rows.append([f"D{i+1}","SS3100 SMA",f"cathode(band)>({c},d) · anode>({c+2},d)"])
        rows.append([f"R{10+i}","RSET "+rset+" 2512",f"top pigtail>({c},c) · bottom pigtail>({c+3},c)"])
        rows.append([f"L{i+1}","L "+L,f"leg1>({c+2},c) · leg2>({c+4},b)"])
        rows.append([f"C{10+i}","22uF/50V 1210",f"({c},a)-({c+1},a)"])
        rows.append([f"C{20+i}","100nF",f"({c},b)-({c+1},b)"])
        rows.append([f"LED string {name}","~"+vs,f"+ wire>({c+3},d) · - wire>({c+4},c)"])
    for r in [
      ["J1","DC barrel jack 2.1mm","+24V wire>(1,f) · GND wire>(3,f)"],
      ["F1","2A slow 5x20mm + 2 clips","clip leads (1,h)-(2,h)"],
      ["SW/J7","rocker switch","pigtails (2,i)-(4,i)"],
      ["C1","100nF","(4,f)-(3,f)"],
      ["C2","220uF/50V radial","+ (4,g) · - (3,g)"],
      ["U10","LM2596 module (preset 12.0V)","IN+>(43,a) IN->(44,a) OUT+>(45,a) OUT->(46,a)"],
      ["C12V","22uF/50V 1210","(45,a)-(46,a)"],
      ["U9","AMS1117-3.3 SOT223","p3 IN>(10,g) · p2 OUT>(12,g) · p1 GND>(11,g)"],
      ["C3","1uF","(10,f)-(11,f)"], ["C4","1uF","(12,f)-(11,f)"],
      ["J6","ESP32-C3 SuperMini (USB powered)","PWM_W>(13,f) PWM_R>(14,f) PWM_B>(15,f) PWM_DR>(16,f) GND>(17,f)"],
      ["R1","1k","(13,g)-(19,g)"], ["R2","1k","(14,g)-(21,g)"],
      ["R3","1k","(15,g)-(23,g)"], ["R4","1k","(16,g)-(25,g)"],
      ["R5","100k","(19,h)-(20,h)"], ["R6","100k","(21,h)-(22,h)"],
      ["R7","100k","(23,h)-(24,h)"], ["R8","100k","(25,h)-(26,h)"],
      ["TP1-TP6","bare wire loops 5mm","28=+24V 29=GND 30=+12V 31=+5V 32=+3V3 33=CTRL_W"],
    ]: rows.append(r)
    return rows

def svg_channel():
    X=[70,180,290,400,510,620]; names=["+24V/RAIL","GND","SW","A=SET","K=LED-","CTRL"]
    p=['<svg viewBox="0 0 720 320" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:720px">']
    p.append('<rect width="720" height="320" fill="#fff" stroke="#999"/>')
    p.append('<line x1="40" y1="30" x2="100" y2="30" stroke="#c0392b" stroke-width="3"/>')
    p.append('<text x="70" y="22" font-size="11" fill="#c0392b" text-anchor="middle">+24V rail</text>')
    p.append('<line x1="150" y1="295" x2="210" y2="295" stroke="#333" stroke-width="3"/>')
    p.append('<text x="180" y="312" font-size="11" fill="#333" text-anchor="middle">GND rail</text>')
    for i,x in enumerate(X):
        p.append(f'<line x1="{x}" y1="40" x2="{x}" y2="280" stroke="#2c3e50" stroke-width="2.5"/>')
        p.append(f'<text x="{x}" y="52" font-size="10" text-anchor="middle" font-weight="bold">col {i+1}</text>')
        p.append(f'<text x="{x}" y="64" font-size="8.5" text-anchor="middle" fill="#666">{names[i]}</text>')
    for y,v in ((90,"C10 22uF (1,a)-(2,a)"),(115,"C20 100n (1,b)-(2,b)")):
        p.append(f'<line x1="{X[0]}" y1="{y}" x2="{X[1]}" y2="{y}" stroke="#8e44ad" stroke-width="2"/>')
        p.append(f'<line x1="{X[0]}" y1="{y-5}" x2="{X[0]}" y2="{y+5}" stroke="#8e44ad" stroke-width="3"/>')
        p.append(f'<line x1="{X[1]}" y1="{y-5}" x2="{X[1]}" y2="{y+5}" stroke="#8e44ad" stroke-width="3"/>')
        p.append(f'<text x="{(X[0]+X[1])//2}" y="{y-8}" font-size="9" text-anchor="middle" fill="#8e44ad">{v}</text>')
    return p
    p.append('<rect x="195" y="135" width="200" height="58" rx="6" fill="#d6eaf8" stroke="#2471a5" stroke-width="2"/>')
    p.append('<text x="295" y="160" font-size="11" text-anchor="middle" font-weight="bold">U1 AL8860</text>')
    p.append('<text x="295" y="173" font-size="8" text-anchor="middle" fill="#555">dead-bug · legs 30AWG</text>')
    p.append('<text x="295" y="127" font-size="8" text-anchor="middle" fill="#2471a5">p5>(1,e) · p2>(2,e) · p1>(3,e) · p4>(4,e)</text>')
    p.append('<line x1="70" y1="185" x2="195" y2="185" stroke="#2471a5" stroke-width="2"/>')
    p.append('<line x1="180" y1="178" x2="205" y2="178" stroke="#2471a5" stroke-width="2"/>')
    p.append('<line x1="290" y1="178" x2="395" y2="178" stroke="#2471a5" stroke-width="2"/>')
    p.append('<line x1="395" y1="185" x2="620" y2="185" stroke="#2471a5" stroke-width="1.5" stroke-dasharray="4 3"/>')
    p.append('<text x="520" y="178" font-size="8" fill="#2471a5">p3>(6,e) CTRL</text>')
    p.append('<path d="M 290 250 L 70 250" stroke="#c0392b" stroke-width="2" fill="none"/>')
    p.append('<polygon points="110,250 102,244 102,256" fill="#c0392b"/>')
    p.append('<text x="180" y="240" font-size="9" text-anchor="middle" fill="#c0392b">D1 SS3100 (3,d)>(1,d)</text>')
    p.append('<line x1="70" y1="215" x2="400" y2="215" stroke="#16a085" stroke-width="2"/>')
    p.append('<rect x="215" y="207" width="30" height="16" fill="#16a085" opacity="0.3" stroke="#16a085"/>')
    p.append('<text x="235" y="203" font-size="9" text-anchor="middle" fill="#16a085">R10 0.40R (1,c)-(4,c)</text>')
    p.append('<path d="M 290 262 q 10 -14 20 0 q 10 -14 20 0 q 10 -14 20 0 q 10 -14 20 0 L 430 262" stroke="#e67e22" stroke-width="2" fill="none"/>')
    p.append('<text x="360" y="278" font-size="9" text-anchor="middle" fill="#e67e22">L1 68uH (3,c)-(5,b)</text>')
    p.append('<circle cx="400" cy="120" r="4" fill="#f1c40f"/>')
    p.append('<text x="360" y="112" font-size="9" fill="#b7950b">LED+ (4,d)</text>')
    p.append('<circle cx="510" cy="160" r="4" fill="#7f8c8d"/>')
    p.append('<text x="510" y="152" font-size="9" fill="#7f8c8d">LED- (5,c)</text>')
    p.append('</svg>')
    return "".join(p)

def svg_system():
    p=['<svg viewBox="0 0 720 430" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:720px">']
    p.append('<rect width="720" height="430" fill="#fff" stroke="#999"/>')
    def box(x,y,w,h,fill,title,sub=""):
        p.append('<rect x="{}" y="{}" width="{}" height="{}" rx="6" fill="{}" opacity="0.25" stroke="{}" stroke-width="1.5"/>'.format(x,y,w,h,fill,fill))
        p.append('<text x="{}" y="{}" font-size="10" font-weight="bold" fill="{}" text-anchor="middle">{}</text>'.format(x+w/2,y+16,fill,title))
        if sub: p.append('<text x="{}" y="{}" font-size="8" fill="{}" text-anchor="middle">{}</text>'.format(x+w/2,y+28,fill,sub))
    box(20,20,120,40,"#f39c12","24V PSU","LRS-35-24")
    box(170,20,120,40,"#f39c12","J1·F1·J7","fuse + switch")
    box(320,20,120,40,"#c0392b","+24V rail","top-outer")
    box(20,110,120,40,"#3498db","CH1-CH4 white","cols 1-24 · 250mA ea")
    box(170,110,120,40,"#27ae60","U10 LM2596","preset 12.0V")
    box(320,110,120,40,"#e67e22","+12V rail","bot-outer")
    box(20,200,120,40,"#e74c3c","CH5 red","122mA")
    box(170,200,120,40,"#2980b9","CH6 blue","303mA")
    box(320,200,120,40,"#8e44ad","CH7 deep-red","122mA")
    box(500,110,140,40,"#16a085","LED strings","A/K per channel")
    box(500,20,140,40,"#7f8c8d","ESP32-C3","USB powered · J6")
    box(500,200,140,60,"#2c3e50","R1-R4 1k series","R5-R8 100k pulldowns")
    box(20,300,620,40,"#333","GND star point at (3,f-j) power section - every channel GND + U10 + U9 wired back individually")
    for x1,y1,x2,y2,c in [(140,40,170,40,"#f39c12"),(290,40,320,40,"#f39c12"),(380,60,380,110,"#c0392b"),
        (80,90,80,110,"#3498db"),(230,90,230,110,"#c0392b"),(290,130,320,130,"#27ae60"),(380,150,380,200,"#e67e22"),
        (80,150,80,200,"#e74c3c"),(230,150,230,200,"#2980b9"),(380,240,380,260,"#8e44ad"),
        (570,60,570,110,"#7f8c8d"),(500,130,440,130,"#16a085")]:
        p.append('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="{}" stroke-width="2"/>'.format(x1,y1,x2,y2,c))
    p.append('<text x="420" y="55" font-size="8" fill="#c0392b">0.95A - run 22AWG bus</text>')
    p.append('</svg>')
    return "".join(p)

HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<title>ColorBoost V0 — perfboard placement map</title>
<style>
 @page {{ size: A4; margin: 12mm }}
 body {{ font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 11px; margin: 20px auto; max-width: 900px }}
 h1 {{ font-size: 19px; margin: 0 0 2px }} h2 {{ font-size: 14px; margin: 14px 0 4px; border-bottom: 2px solid #333 }}
 table {{ border-collapse: collapse; width: 100%; margin: 4px 0 8px }}
 th,td {{ border: 1px solid #999; padding: 2.5px 5px; text-align: left; vertical-align: top }}
 th {{ background:#eee }} .warn {{ background:#fde8e8; border:1px solid #c0392b; padding:6px 8px; margin:6px 0 }}
 .note {{ background:#fef9e7; border:1px solid #b7950b; padding:6px 8px; margin:6px 0 }}
 .mono {{ font-family: ui-monospace, Menlo, monospace }}
</style></head><body>
<h1>ColorBoost V0 — perfboard prototype placement map</h1>
<div style="color:#666">830-point solderable breadboard (2×63 cols × 5 rows + 4 rails) · generated from aquarium_v0.kicad_sch netlist · 2026-09-28</div>

<div class="note"><b>Before soldering:</b> ① with a multimeter, confirm each 5-hole column is one node and check whether your rails are continuous or split in halves (many solderable BBs split them — if split, bridge with wire). ② Columns are counted <b>from the left, 1–63</b>; rows a–e top bank (a nearest top rail), f–j bottom bank. ③ Tin everything first; AL8860 legs = 30AWG wire. ④ The J8–J13 board joints and colour-series chains from the PCB design do NOT apply here — one perfboard replaces all four boards, so each channel drives one LED string directly.</div>

<h2>Board overview</h2>
{svg_board()}

<h2>Channel blocks — top bank (a–e), 6 columns each</h2>
{table(["Ch","Cols","Rail","CTRL","RSET","L","LED string holes","V_string","I_LED"], ch_rows)}

<h2>Wiring card — every channel follows this template (example: CH1, cols 1–6)</h2>
{card}
<p class="mono" style="font-size:10px">Net check per channel: RAIL col ↔ rail · (c+1)=GND · (c+2)=SW=U_p1+L_leg1+D_anode · (c+3)=SET=U_p4+RSET-bottom+LED+ · (c+4)=LED−=L_leg2 · (c+5)=CTRL=U_p3</p>

<h2>Wiring diagram — one channel (CH1; identical shape for all 7, shift column numbers)</h2>
{svg_channel()}

<h2>System interconnect</h2>
{svg_system()}

<h2>Exact component list — every part and its holes</h2>
{table(["Ref","Part","Exact placement"], exact_rows())}

<h2>Power input — bottom bank cols 1–8</h2>
{table(["Where","What"], power_rows)}

<h2>LM2596 module (U10) + cross-bank wires — top bank cols 43–50</h2>
{table(["Where","What"], u10_rows)}

<h2>Logic / control — bottom bank cols 10–26</h2>
{table(["Where","What"], logic_rows)}

<h2>Bring-up sequence &amp; test points</h2>
{table(["Step","Action","Expect"], [
 ["0","LM2596 module ALONE on bench: feed 24V, set pot","12.00 V at OUT, before any wiring in"],
 ["1","Wire power section only (cols 1–8, rails, C1/C2). No ICs soldered yet","+24V rail = 24V, GND continuity OK, fuse holds"],
 ["2","Solder CH1 (U1 white) only. White LED string ≈17.6V at (4,d)–(5,c). Power via switch","V across RSET (1,c)–(4,c) ≈ 100 mV → I=250 mA; SW node square wave; SS3100 warm not hot"],
 ["3","If current off-sim, swap RSET (try 0.47/0.50Ω)","settles the open RSET decision → final PCB BOM"],
 ["4","Add CH2–CH4 whites one at a time","each ≈100 mV across its RSET; total 24V current ≈0.95 A"],
 ["5","Wire U10 + C12V; verify +12V rail unloaded","12.0 V"],
 ["6","Add CH5/CH6/CH7 (12V channels) one at a time","R:122 mA · B:303 mA · DR:122 mA (100 mV/RSET)"],
 ["7","Logic section + ESP32 PWM","CTRL 3V3 → full current; 0V → off"],
])}

<div class="warn"><b>⚠ U8 IRM-02-5 flag:</b> BOM lists Mean Well IRM-02-5 (24V→5V) but that module's input range is 70–305 VAC mains — it will NOT start from +24V DC. For the prototype power the ESP32 from USB. Re-check before the PCB order (swap to a 24→5V DC-DC, e.g. LM2596-5.0 mini module).</div>

<h2>Refs → perfboard cross-reference</h2>
{table(["Refs","Value / part","Perfboard placement"], [
 ["U1–U4","AL8860WT-7 SOT-23-6","top bank, dead-bug, blocks cols 1–24"],
 ["U5,U6,U7","AL8860WT-7 SOT-23-6","top bank, dead-bug, cols 25–42"],
 ["R10–R13","0.40Ω 2512 WSL","pigtailed at (c,3rd-row)–(c+3,3rd-row) per white block"],
 ["R14,R16","0.82Ω 2512","CH5/CH7 same position"],
 ["R15","0.33Ω 2512","CH6 same position"],
 ["D1–D7","SS3100 SMA","(c,d)–(c+2,d) per block; banded end = cathode → rail col"],
 ["L1–L6","68µH Würth 744778368","(c+2,c)–(c+4,b), leg wires + hot glue"],
 ["L7","100µH","CH7"],
 ["C10–C16","22µF/50V 1210","(c,a)–(c+1,a)"],
 ["C20–C26","100nF","(c,b)–(c+1,b)"],
 ["F1","2A slow 5×20mm + clips","(1,h)–(2,h)"],
 ["J7","rocker switch","(2,i)–(4,i)"],
 ["C1/C2","100n / 220µF-50V","(4,f)-(3,f) / (4,g)-(3,g)"],
 ["C3/C4","1µF","logic cols 10–12"],
 ["U9","AMS1117-3.3 SOT223","legs → (10,g),(11,g),(12,g)"],
 ["J6","ESP32-C3 SuperMini","6 wires to cols 13–18"],
 ["U10","LM2596 module","top bank cols 43–46"],
 ["C12V","22µF 1210","(45,a)–(46,a)"],
 ["J2–J5, J8–J13","omitted","single perfboard replaces the 4-board split"],
])}
<p style="color:#666">Print: Cmd+P → A4, enable background graphics. Source: proto/make_proto_map.py — regenerate after any netlist change.</p>
</body></html>"""
open(OUT, "w").write(HTML)
print("wrote", OUT, len(HTML), "bytes")
