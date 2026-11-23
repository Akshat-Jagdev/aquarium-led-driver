#!/usr/bin/env python3
"""Transient sim: AL8860 hysteretic-buck LED channels, Aquarium V0 (Sep 16 2026).
Loop: rail -> RSET -> LED string -> L -> SW. ON: through internal FET (RDS).
OFF: freewheel SS3100 (VD) back to rail (RSET stays in loop -> high-side sense).
"""
REF=0.100; HYST=0.10        # SET reference [V], +/- hysteretic band (frac of Iset)
RDS=0.35; VD=0.50; RDCR=0.15; RDYN=2.0   # AL8860 RDS(on), SS3100 Vf, L DCR, string dyn R
DT=2e-9; TEND=300e-6; TSETTLE=50e-6
CH=[("White (U1-U4)",4,24.0,17.55,0.40,68e-6),
    ("Red   (U5)    ",1,12.0, 8.00,0.82,68e-6),
    ("Blue  (U6)    ",1,12.0, 6.40,0.33,68e-6),
    ("DeepR (U7)    ",1,12.0, 4.40,0.82,100e-6)]
def run(vrail,vf,rset,L):
    iset=REF/rset; ihi,ilo=iset*(1+HYST),iset*(1-HYST)
    i=ilo; on=True; t=0.0; ncyc=0; ton=t_off_start=0.0
    Ton=[]; Imax=-9; Imin=9; iacc=0.0; n=0; Ton_tot=0.0
    Ein=Eled=Edio=Erds=Erset=0.0
    while t<TEND:
        vstr=vf+i*RDYN
        if on:
            vL=vrail - vstr - i*(rset+RDCR+RDS)
        else:
            vL= -vstr - VD - i*(rset+RDCR)
        i+=vL/L*DT
        if i<0: i=0.0
        if t>=TSETTLE:
            if on: Ein+=vrail*i*DT; Erds+=i*i*RDS*DT; ton+=DT; Ton_tot+=DT
            else:  Edio+=i*VD*DT
            Eled+=vstr*i*DT; Erset+=i*i*rset*DT
            iacc+=i; n+=1; Imax=max(Imax,i); Imin=min(Imin,i)
            if on and i>=ihi:
                on=False; ncyc+=1; Ton.append(ton); ton=0.0
            elif (not on) and i<=ilo:
                on=True
        elif on and i>=ihi: on=False
        elif (not on) and i<=ilo: on=True
        t+=DT
    Tw=n*DT; fsw=ncyc/Tw; duty=Ton_tot/Tw
    Pin=Ein/Tw; Pled=Eled/Tw; eta=Pled/Pin if Pin else 0
    return dict(iavg=iacc/n, rip=Imax-Imin, fsw=fsw, duty=duty,
                ton_min=min(Ton) if Ton else 0, ton_avg=(Ton_tot/ncyc) if ncyc else 0,
                Pin=Pin, Pled=Pled, eta=eta, Pdio=Edio/Tw, Prds=Erds/Tw, Prset=Erset/Tw)
tot24=0.0; p12=0.0
print(f"{'channel':16s} {'I_led(mA)':>9s} {'rip(mA)':>7s} {'fsw(kHz)':>8s} {'duty':>6s} {'tON(ns)':>8s} {'Pin(W)':>7s} {'eta':>6s} {'Pdiode':>7s}")
for name,qty,vrail,vf,rset,L in CH:
    r=run(vrail,vf,rset,L)
    print(f"{name:16s} {r['iavg']*1e3:9.1f} {r['rip']*1e3:7.1f} {r['fsw']/1e3:8.1f} {r['duty']:6.3f} {r['ton_avg']*1e9:8.0f} {r['Pin']:7.2f} {r['eta']:6.3f} {r['Pdio']:7.3f}")
    if vrail>20: tot24+=r['Pin']*qty
    else:        p12+=r['Pin']*qty
print(f"\ntON_min after settle: see ton_min per channel (excluded from table for brevity)")
p24_buck=p12/0.92; i12=p12/12.0
print(f"12V rail load: {p12:.2f} W  -> I_out(LM2596) = {i12:.2f} A; LM2596 draws {p24_buck/24:.2f} A from 24V (eff 92%)")
print(f"24V rail total: white {tot24:.2f} W + 12V buck {p24_buck:.2f} W = {tot24+p24_buck:.2f} W -> I(24V) = {(tot24+p24_buck)/24:.2f} A")
print(f"LRS-35-24 headroom: {36-(tot24+p24_buck):.1f} W of 36 W")
