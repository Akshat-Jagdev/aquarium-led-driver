#!/usr/bin/env python3
"""Panelize 4 V0 boards into one: 2x2 chain, 2mm open gaps, mouse-bite tabs."""
import re, uuid
G=2.0; H=20.0

def top_items(txt):
    out=[]; depth=0; in_s=False; esc=False; starts=[]; i=0; n=len(txt)
    while i<n:
        c=txt[i]
        if in_s:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c=='"': in_s=False
        elif c=='"': in_s=True
        elif c=='(':
            depth+=1
            if depth==2: starts.append(i)
        elif c==')':
            if depth==2: out.append((starts.pop(),i))
            depth-=1
        i+=1
    res=[]
    for s,e in out:
        m=re.match(r'\(([\w-]+)',txt[s:e+1])
        res.append((m.group(1) if m else '?', s, e+1))
    return res

def bal_span(s, kw):
    i=s.find('('+kw)
    if i<0: return None
    d=0; j=i
    while j<len(s):
        if s[j]=='(':d+=1
        elif s[j]==')':
            d-=1
            if d==0: return (i,j+1)
        j+=1
    return None

def off_pair(m,kw,dx,dy):
    g=m.groups()
    return f"({kw} {float(g[-2])+dx:.4f} {float(g[-1])+dy:.4f}"

def transform(block, kw, dx, dy, netmap):
    s=block
    if kw=='zone':
        s=re.sub(r'\(xy (-?[\d.]+) (-?[\d.]+)',lambda m:off_pair(m,'xy',dx,dy),s)
    elif kw in ('footprint','via','gr_text','gr_text_with_offset'):
        s=re.sub(r'\((at|start|end) (-?[\d.]+) (-?[\d.]+)',
                 lambda m:off_pair(m,m.group(1),dx,dy),s,count=1)
    else:
        s=re.sub(r'\((at|start|end|mid|center) (-?[\d.]+) (-?[\d.]+)',
                 lambda m:off_pair(m,m.group(1),dx,dy),s)
    return re.sub(r'"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"',
                   lambda m: f'"{uuid.uuid4()}"', s)

def npth(ref,x,y):
    return (f'(footprint "aquarium:NPTH_MouseBite"\n\t\t(layer "F.Cu")\n\t\t(uuid "{uuid.uuid4()}")\n'
      f'\t\t(at {x:.3f} {y:.3f})\n\t\t(attr board_only exclude_from_pos_files exclude_from_bom)\n'
      f'\t\t(property "Reference" "{ref}" (at 0 0 0) (layer "F.SilkS") (hide yes) (uuid "{uuid.uuid4()}") '
      f'(effects (font (size 0.8 0.8) (thickness 0.1))))\n'
      f'\t\t(property "Value" "NPTH_0.3" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "{uuid.uuid4()}") '
      f'(effects (font (size 0.8 0.8) (thickness 0.1))))\n'
      f'\t\t(pad "" np_thru_hole circle (at 0 0) (size 0.6 0.6) (drill 0.3) (layers "*.Mask"))\n\t)')

def union_outline(rects):
    xs=sorted({v for r in rects for v in (r[0],r[2])})
    ys=sorted({v for r in rects for v in (r[1],r[3])})
    nx,ny=len(xs),len(ys)
    def ins(i,j):
        cx,cy=(xs[i]+xs[i+1])/2,(ys[j]+ys[j+1])/2
        return any(r[0]<cx<r[2] and r[1]<cy<r[3] for r in rects)
    grid=[[ins(i,j) for j in range(ny-1)] for i in range(nx-1)]
    segs={}
    for i in range(nx-1):
        for j in range(ny-1):
            if not grid[i][j]: continue
            a,b,c,d=xs[i],xs[i+1],ys[j],ys[j+1]
            if j==0 or not grid[i][j-1]: segs[('H',c,a,b)]=+1
            if j==ny-2 or not grid[i][j+1]: segs[('H',d,a,b)]=-1
            if i==0 or not grid[i-1][j]: segs[('V',a,c,d)]=-1
            if i==nx-2 or not grid[i+1][j]: segs[('V',b,c,d)]=+1
    dirs=dict(segs)
    def ends(k):
        t,v,a,b=k; d=dirs[k]
        if t=='H': return ((a,v),(b,v)) if d>0 else ((b,v),(a,v))
        return ((v,a),(v,b)) if d>0 else ((v,b),(v,a))
    bystart={ends(k)[0]:k for k in segs}
    loops=[]
    while segs:
        k0=next(iter(segs)); loops.append([]); L=loops[-1]
        k=k0
        while True:
            L.append(k); del segs[k]
            p=ends(k)[1]
            if p==ends(k0)[0]: break
            k=bystart.get(p)
            if k is None or k not in segs: break
    best=max(loops,key=lambda lp:max(x for x,_ in (ends(kk)[0] for kk in lp)))
    pts=[ends(best[0])[0]]+[ends(kk)[1] for kk in best]
    if pts[0]==pts[-1]: pts=pts[:-1]
    return pts

def tab(x1,y1,x2,y2):
    tab.n=getattr(tab,'n',0)+1
    tab.rects.append((x1,y1,x2,y2))
    if x2-x1 < y2-y1:
        yc=(y1+y2)/2; pts=[(x1+1.7,yc),(x1+2.3,yc)]
    else:
        xc=(x1+x2)/2; pts=[(xc,y1+1.7),(xc,y1+2.3)]
    return [npth(f'MB{tab.n:03d}',px,py) for px,py in pts]

boards={}
for n in (1,2,3,4):
    txt=open(f'aquarium_v0_board{n}.kicad_pcb').read()
    boards[n]=(txt,top_items(txt))
bbox={}
for n,(txt,items) in boards.items():
    xs=[];ys=[]
    for kw,s,e in items:
        b=txt[s:e]
        if kw.startswith('gr_') and 'Edge.Cuts' in b:
            for m in re.finditer(r'\((?:start|end|center|mid) (-?[\d.]+) (-?[\d.]+)',b):
                xs.append(float(m.group(1)));ys.append(float(m.group(2)))
    bbox[n]=(min(xs),min(ys),max(xs),max(ys))
W={n:bbox[n][2]-bbox[n][0] for n in bbox}
pl={4:(5.0,5.0), 1:(5.0+W[4]+G,5.0), 2:(5.0,5.0+H+G), 3:(5.0+W[2]+G,5.0+H+G)}
ITEMS=('segment','via','footprint','zone','gr_text','gr_line','gr_rect','gr_arc','gr_circle')
pre_end=min(s for kw,s,e in boards[1][1] if kw in ITEMS)
out=[boards[1][0][:pre_end]]
for n in (4,1,2,3):
    txt,items=boards[n]; dx=pl[n][0]-bbox[n][0]; dy=pl[n][1]-bbox[n][1]
    for kw,s,e in items:
        if kw not in ('segment','via','footprint','zone','gr_text','gr_line','gr_rect','gr_arc','gr_circle'): continue
        b=txt[s:e]
        if kw.startswith('gr_') and 'Edge.Cuts' in b: continue
        out.append(transform(b,kw,dx,dy,None))
xg=5.0+W[4]; xg2=5.0+W[2]; yg=5.0+H
tab.rects=[]
tabs=[]
for yc in (9.0,15.0,21.0): tabs+=tab(xg-1,yc-2,xg+G+1,yc+2)
for yc in (31.0,37.0,43.0): tabs+=tab(xg2-1,yc-2,xg2+G+1,yc+2)
for xc in (45.0,135.0,200.0,240.0): tabs+=tab(xc-2,yg-1,xc+2,yg+G+1)
tab.rects+= [tuple(round(v,3) for v in (pl[n][0],pl[n][1],pl[n][0]+W[n],pl[n][1]+H)) for n in (1,2,3,4)]
pts=union_outline(tab.rects)
pts_txt=' '.join(f'(xy {x:.3f} {y:.3f})' for x,y in pts)
poly=(f'(gr_poly\n\t\t(pts\n\t\t\t{pts_txt}\n\t\t)\n'
      f'\t\t(stroke (width 0.05) (type solid)) (fill none) (layer "Edge.Cuts") (uuid "{uuid.uuid4()}"))')
print("outline pts:",len(pts))
out+=tabs; out.append(poly); out.append(')\n')
open('aquarium_v0_panel.kicad_pcb','w').write('\n'.join(out))
print(f"panel: {5+W[4]+G+W[1]-5:.1f} x {5+H+G+H-5:.1f} mm, NPTH={getattr(tab,'n',0)}")
