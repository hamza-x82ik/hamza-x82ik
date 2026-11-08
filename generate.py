"""Builds dark_mode.svg and light_mode.svg from profile.json + stats.json + portrait.json.
Run:  python generate.py            (GitHub Action runs this daily after update_stats.py)"""
import html, re, json, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
E=lambda s: html.escape(s, quote=False)
W,H=1045,632; FS=16; CW=9.6; LH=20
THEMES={
 "dark": dict(bg="#161b22",fg="#c9d1d9",key="#ffa657",val="#a5d6ff",cc="#616e7f",red="#ff7b72",grn="#3fb950",blu="#79c0ff",cmt="#7ee787"),
 "light":dict(bg="#f6f8fa",fg="#24292f",key="#953800",val="#0a3069",cc="#c2cfde",red="#cf222e",grn="#1a7f37",blu="#0969da",cmt="#1a7f37")}
THEME=sys.argv[1] if len(sys.argv)>1 else "dark"
C=THEMES[THEME]
CFG=json.load(open("profile.json")); ST=json.load(open("stats.json"))
USER=CFG["github_user"]
o=[]; uid=[0]
def nid(): uid[0]+=1; return f"i{uid[0]}"
def vis(on,off=None):
    s=f'<set attributeName="visibility" to="visible" begin="{on:.2f}s"/>'
    if off is not None: s+=f'<set attributeName="visibility" to="hidden" begin="{off:.2f}s"/>'
    return s
def text(x,y,inner,on,off=None,fill=C["fg"],extra=""):
    o.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" visibility="hidden"{extra}>{inner}{vis(on,off)}</text>')
def cursor(x,y,on,off=None,ch="_"):
    o.append(f'<text x="{x:.1f}" y="{y}" fill="{C["fg"]}" class="cur" visibility="hidden">{ch}{vis(on,off)}</text>')
def typed(x,y,s,t0,dt,fill,off=None,cw=CW,fs=None,cur="_",lh=22,extra=""):
    """reveal s one char at a time (hard steps, no fades), cursor follows; returns end time"""
    n=len(s); i=nid(); t1=t0+n*dt
    vals=";".join(f"{k*cw:.2f}" for k in range(n+1))+f";{(n+1)*cw:.2f}"
    kt=";".join(f"{k/(n+1):.4f}" for k in range(n+2))
    fsz=fs or FS
    o.append(f'<clipPath id="{i}"><rect x="{x-1:.1f}" y="{y-fsz:.1f}" height="{lh}" width="0"><animate attributeName="width" begin="{t0:.2f}s" dur="{(n+1)*dt:.3f}s" values="{vals}" keyTimes="{kt}" calcMode="discrete" fill="freeze"/></rect></clipPath>')
    fa=f' font-size="{fs}"' if fs else ""
    text(x,y,E(s),t0,off,fill,f' clip-path="url(#{i})"{fa}{extra}')
    xs=";".join(f"{x+k*cw:.2f}" for k in range(n+1)); kt2=";".join(f"{k/(n+1):.4f}" for k in range(n+1))
    o.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{C["fg"]}"{fa} visibility="hidden">{cur}<animate attributeName="x" begin="{t0:.2f}s" dur="{(n+1)*dt:.3f}s" values="{xs}" keyTimes="{kt2}" calcMode="discrete" fill="freeze"/>{vis(t0,t1+dt)}</text>')
    return t1
def prompt(y,on,off):
    text(15,y,f'<tspan fill="{C["red"]}">hamza</tspan>@<tspan fill="{C["red"]}">nutech</tspan> ~&gt; ',on,off)
    return 15+len("hamza@nutech ~> ")*CW
def command(y,cmd,t0,dt,off):
    x=prompt(y,t0-0.8,off); cursor(x,y,t0-0.8,t0)
    t1=typed(x,y,cmd,t0,dt,C["red"])           # red while incomplete (zsh highlighting)
    first,_,rest=cmd.partition(" ")
    o.append(f'<rect x="{x-1:.1f}" y="{y-16}" width="{len(cmd)*CW+12:.1f}" height="22" fill="{C["bg"]}" visibility="hidden">{vis(t1+0.05,off)}</rect>')
    o.append(f'<text x="{x:.1f}" y="{y}" fill="{C["fg"]}" visibility="hidden"><tspan fill="{C["grn"]}">{E(first)}</tspan>{(" "+E(rest)) if rest else ""}{vis(t1+0.05,off)}</text>')
    return t1
def close_open(start,end):
    for k in range(len(o)):
        m=re.findall(r'to="visible" begin="([\d.]+)s"/>',o[k])
        if m and 'to="hidden"' not in o[k] and float(m[0])>=start-0.001:
            o[k]=o[k].replace(f'to="visible" begin="{m[0]}s"/>',f'to="visible" begin="{m[0]}s"/><set attributeName="visibility" to="hidden" begin="{end:.2f}s"/>',1)
y=lambda r: 30+r*LH

# ===== 1. BIOS (slower, like x0rzavi) =====
T0=1.4
text(15,y(0),"x82ik_OS Modular BIOS v1.0.26",T0)
text(15,y(1),f'Copyright (C) 2026, <tspan fill="{C["red"]}">Muhammad Hamza Ali</tspan> Labs Inc.',T0+0.35)
text(15,y(3),"GitHub Profile ReadMe Terminal, Rev 2026",T0+0.7,None,C["blu"])
text(15,y(5),"Arduino(tm) ATmega328P - 16MHz",T0+1.05)
text(15,y(28),f'Press <tspan fill="{C["blu"]}">DEL</tspan> to enter SETUP, <tspan fill="{C["blu"]}">ESC</tspan> to cancel Memory Test',T0+1.05)
t=T0+1.5
for v in range(0,2049,128):
    text(15,y(6),f"Memory Test: {v}",t,t+0.14); t+=0.14
text(15,y(6),"Memory Test: 2KB OK",t)
END1=t+1.8; close_open(0.1,END1)

# ===== 2+3. Initiating boot + scramble/glitch logo (same screen, like x0rzavi) =====
import random; sys.path.insert(0,".")
from pixfont import F as PF, RANDOM
random.seed(82)
S2=END1+0.3
text(15,y(0),"Initiating Boot Sequence ",S2)
for k in range(5): text(15+(25+k)*CW,y(0),".",S2+0.5+k*0.45)
P=9; ADV=6*P+5; LY=H/2-40
FR=0.085                                   # ~12 fps, same as the GIF
frames=[]                                  # (start, string)
def rnd(): return random.choice(RANDOM)
def decode(word,t,lead=4,per=2):
    k=0
    while True:
        locked=max(0,(k-lead)//per+1) if k>=lead else 0
        frames.append((t,"".join(word[i] if i<locked or word[i]==" " else rnd() for i in range(len(word)))))
        t+=FR; k+=1
        if locked>=len(word): return t
def hold(word,t,dur,glitch_at=()):
    end=t+dur
    for g in sorted(glitch_at):
        frames.append((t,word)); t=g
        w=list(word)
        for i in random.sample(range(len(word)),k=random.choice([1,1,2])): w[i]=rnd()
        frames.append((t,"".join(w))); t+=FR
    frames.append((t,word)); return end
t=S2+0.5+5*0.45+0.5
LOGO0=t
t=decode("Arix",t)
t=hold("Arix",t,1.1,[t+0.55])
for n in range(3,-1,-1):                   # backspace A-r-i-x
    frames.append((t,"Arix"[:n])); t+=0.2
t+=0.3
t=decode("x82ik",t)
t=hold("x82ik",t,2.0,[t+0.35,t+0.75,t+1.2])
END2=t
frames.append((END2,""))
# position-wise intervals -> <use> elements (each glyph defined once)
LX=(W-5*ADV)/2
used=set()
for pos in range(5):
    cur=None; start=None
    for (ft,st) in frames+[(END2+9,"")]:
        ch=st[pos] if pos<len(st) else ""
        if ch!=cur:
            if cur and cur.strip():
                used.add(cur)
                o.append(f'<use href="#g_{ord(cur)}" xlink:href="#g_{ord(cur)}" x="{LX+pos*ADV:.0f}" y="{LY:.0f}" visibility="hidden">{vis(start,ft)}</use>')
            cur=ch; start=ft
GLYPHS="".join(f'<g id="g_{ord(c)}" fill="{C["val"]}">'+"".join(f'<rect x="{cc*P}" y="{r*P}" width="{P+4}" height="{P}"/>' for r,row in enumerate(PF[c]) for cc,bit in enumerate(row) if bit=="1")+'</g>' for c in sorted(used))
close_open(S2,END2+0.6)
END3=END2+0.6

# ===== 4. login =====
S4=END3+0.3
text(15,y(0),"x82ik OS v1.0.26 (tty1)",S4,None,C["key"])
text(15,y(2),"login: ",S4+0.6)
t=typed(15+7*CW,y(2),"hamza",S4+1.1,0.15,C["fg"])
text(15,y(3),"password: ",t+0.4)
t=typed(15+10*CW,y(3),"********",t+0.8,0.12,C["fg"])
text(15,y(5),"Last login: Sun Nov  8 10:21:07 PKT 2026 on tty1",t+0.6)
t=command(y(6),"clear",t+1.1,0.15,None)
END4=t+0.6; close_open(S4,END4)

# ===== 5. fetch -> Andrew card, portrait TYPED row by row (moiz style) =====
S5=END4+0.3
t=command(y(0),f"fetch.sh -u {USER}",S5+0.9,0.09,None)
OUT=t+0.4
RX=455; WID=60
def kv(keys,v):
    k=".".join(keys); dots=WID-2-len(k)-1-2-len(v)
    ks=f'</tspan>.<tspan fill="{C["key"]}">'.join(E(x) for x in keys)
    return f'<tspan fill="{C["cc"]}">. </tspan><tspan fill="{C["key"]}">{ks}</tspan>:<tspan fill="{C["cc"]}"> {"."*dots} </tspan><tspan fill="{C["val"]}">{E(v)}</tspan>'
def hdr(s): return f'{E(s)} -{"—"*(WID-len(s)-4)}-—-'
dot=f'<tspan fill="{C["cc"]}">. </tspan>'
fmt=lambda n: f"{n:,}"
def stats_lines():
    k=lambda t: f'<tspan fill="{C["key"]}">{t}</tspan>'
    v=lambda t: f'<tspan fill="{C["val"]}">{t}</tspan>'
    d=lambda n: f'<tspan fill="{C["cc"]}"> {"."*max(1,n)} </tspan>'
    r,cn,sr=fmt(ST["repos"]),fmt(ST["contributed"]),fmt(ST["stars"])
    l1=f'{dot}{k("Repos")}:{d(4)}{v(r)} {{{k("Contributed")}: {v(cn)}}} | {k("Stars")}:{d(12)}{v(sr)}'
    cm,fo=fmt(ST["commits"]),fmt(ST["followers"])
    l2=f'{dot}{k("Commits")}:{d(18)}{v(cm)} | {k("Followers")}:{d(8)}{v(fo)}'
    tot=fmt(ST["loc_add"]-ST["loc_del"]); ad,de=fmt(ST["loc_add"]),fmt(ST["loc_del"])
    l3=f'{dot}{k("Lines of Code on GitHub")}:<tspan fill="{C["cc"]}">. </tspan>{v(tot)} ( <tspan fill="{C["grn"]}">{ad}++</tspan>,  <tspan fill="{C["red"]}">{de}--</tspan> )'
    return [l1,l2,l3]
info=[hdr(CFG["header"])]
for L in CFG["lines"]:
    if L[0]=="kv": info.append(kv(L[1],L[2]))
    elif L[0]=="dot": info.append(dot)
    elif L[0]=="gap": info.append(None)
    elif L[0]=="hdr": info.append(hdr(L[1]))
    elif L[0]=="stats": info+=stats_lines()
yy=66
for line in info:
    if line is not None:
        plain=html.unescape(re.sub(r"<[^>]+>","",line))
        ex=f' textLength="{len(plain)*CW:.1f}" lengthAdjust="spacingAndGlyphs"' if len(plain)>3 else ""
        text(RX,yy,line,OUT,None,C["fg"],ex)
    yy+=LH
# portrait: COLOURED, each row typed left->right with block cursor (moiz style)
PD=json.load(open("portrait.json"))
pcw,plh,pfs=PD["cw"],PD["lh"],6.5; px,py=12,60
t=OUT; STEPCH=4; ROWDUR=0.06
for i,(l,lums) in enumerate(zip(PD["chars"],PD["lum"])):
    st=len(l)-len(l.lstrip()); seg=l.rstrip()[st:]
    if not seg: continue
    x0=px+st*pcw; yrow=py+i*plh
    # group runs of same colour into tspans
    runs=[]; 
    for k,ch in enumerate(seg):
        lv=lums[st+k] or 0
        g_=round(255*(0.70+0.30*lv)) if THEME=="dark" else round(255*(0.14+0.30*(1-lv)))
        col=f"#{g_:02x}{g_:02x}{g_:02x}"
        if runs and runs[-1][0]==col: runs[-1][1]+=ch
        else: runs.append([col,ch])
    inner="".join(f'<tspan fill="{c}">{E(txt)}</tspan>' for c,txt in runs)
    n=(len(seg)+STEPCH-1)//STEPCH; step=ROWDUR/n
    i_=nid()
    vals=";".join(f"{min(k*STEPCH,len(seg))*pcw:.1f}" for k in range(n+1))+f";{(len(seg)+1)*pcw:.1f}"
    kt=";".join(f"{k/(n+1):.4f}" for k in range(n+2))
    o.append(f'<clipPath id="{i_}"><rect x="{x0-0.5:.1f}" y="{yrow-6.5:.1f}" height="{plh+0.6:.1f}" width="0"><animate attributeName="width" begin="{t:.3f}s" dur="{(n+1)*step:.3f}s" values="{vals}" keyTimes="{kt}" calcMode="discrete" fill="freeze"/></rect></clipPath>')
    o.append(f'<text x="{x0:.1f}" y="{yrow:.1f}" font-size="{pfs}" clip-path="url(#{i_})" textLength="{len(seg)*pcw:.1f}" lengthAdjust="spacingAndGlyphs">{inner}</text>')
    xs=";".join(f"{x0+min(k*STEPCH,len(seg))*pcw:.1f}" for k in range(n+1)); kt2=";".join(f"{k/(n+1):.4f}" for k in range(n+1))
    o.append(f'<rect x="{x0:.1f}" y="{yrow-5.5:.1f}" width="{pcw:.1f}" height="6.5" fill="{C["fg"]}" visibility="hidden"><animate attributeName="x" begin="{t:.3f}s" dur="{(n+1)*step:.3f}s" values="{xs}" keyTimes="{kt2}" calcMode="discrete" fill="freeze"/>{vis(t,t+(n+1)*step)}</rect>')
    t+=(n+1)*step+0.012
PEND=t
CM=PEND+0.8
x=prompt(H-22,CM,None); cursor(x,H-22,CM,CM+0.8)
t=typed(x,H-22,CFG["closing_line"],CM+0.8,0.055,C["cmt"])
cursor(x+len(CFG["closing_line"])*CW,H-22,t+0.05)

svg=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" font-family="ConsolasFallback,Consolas,monospace" width="{W}px" height="{H}px" viewBox="0 0 {W} {H}" font-size="{FS}px">',
'''<style>
@font-face{src:local('Consolas'),local('Consolas Bold');font-family:'ConsolasFallback';font-display:swap;-webkit-size-adjust:109%;size-adjust:109%}
text,tspan{white-space:pre}
.cur{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}
</style>''',
f'<rect width="{W}px" height="{H}px" fill="{C["bg"]}" rx="15"/>',f'<defs><g fill="{C["val"]}">{GLYPHS}</g></defs>',
f'<text x="15" y="30" fill="{C["fg"]}" class="cur">_<set attributeName="visibility" to="hidden" begin="{T0:.2f}s"/></text>']
svg+=o; svg.append("</svg>")
open(f"{THEME}_mode.svg","w").write("\n".join(svg))
print(THEME, f"BIOS end {END1:.1f}s | logo {LOGO0:.1f}s | fetch output {OUT:.1f}s | portrait done {PEND:.1f}s | total {t:.1f}s")
