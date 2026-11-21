import math, sys, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OW,OH=1080,1920; K=1.5; FPS=30; DUR=14.6; AOFF=0.5
FONT="/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
BG=Image.open("bg_back.png"); BGB=Image.open("bg_back_blur.png"); FG=Image.open("bg_fore.png")
WW,WH=BG.size
import json, functools
LIB="../lib"; META=json.load(open(LIB+"/meta.json"))
@functools.lru_cache(maxsize=48)
def libframe(name,i):
    return Image.open(f"{LIB}/{name}/{i+1:03d}.webp").convert("RGBA")
EMO=ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",109)
ENV=np.load("env.npy")
def env(t):
    i=int((t-AOFF)*30); return float(ENV[i]) if 0<=i<len(ENV) else 0.0
def ease(x): x=max(0.0,min(1.0,x)); return 1-(1-x)**3
def eio(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)
def lerp(a,b,x): return a+(b-a)*x
def bounce(x):
    if x<=0: return 0.0
    if x>=0.6: return 1.0
    return ease(x/0.35)*(1+0.18*math.sin(x*16)*(1-x/0.6))
# ---- words (voice-relative), shifted by AOFF
segs=[(0.05,1.77,"¿Sabías que bostezar es contagioso?"),(2.39,4.71,"Si ves a alguien bostezar, tu cerebro lo copia"),
(4.83,5.97,"casi sin que te des cuenta."),(6.66,8.99,"Los científicos aún no saben exactamente por qué…"),
(9.46,10.80,"pero sí saben algo curioso:"),(11.15,13.24,"¡te pasa más con las personas que quieres!")]
KEY={"BOSTEZAR","CONTAGIOSO","CEREBRO","COPIA","CIENTÍFICOS","POR","QUÉ","CURIOSO","QUIERES"}
chunks=[]
for a,b,txt in segs:
    ws=txt.split(); wt=[len(w)+2 for w in ws]; tot=sum(wt); t=a+AOFF; timed=[]
    for w,x in zip(ws,wt):
        d=(b-a)*x/tot; timed.append((w,t,t+d)); t+=d
    cur=[]
    for it in timed:
        cur.append(it)
        if len(cur)==3 or sum(len(x[0]) for x in cur)>=13 or it[0][-1] in ",.?:…!":
            chunks.append(cur); cur=[]
    if cur: chunks.append(cur)
for i,c in enumerate(chunks):
    nxt=chunks[i+1][0][1] if i+1<len(chunks) else c[-1][2]+0.8
    c.append(min(nxt,c[-1][2]+0.35))
def wtime(word):
    for c in chunks:
        for w in c[:-1]:
            if w[0].strip("¿?¡!,.…").lower()==word: return w[1]
# ---- shots: (t0,t1,[(t,cx,cy,zoom,rot)])  world coords; char feet at (720,2230), height ~1650
SHOTS=[(0.0,2.75,[(0,720,1350,1.0,0),(2.75,710,1150,1.35,-2)]),
 (2.75,5.25,[(2.75,720,900,2.0,-3),(5.25,730,880,2.25,2)]),
 (5.25,7.0,[(5.25,700,1450,1.5,4),(7.0,720,1250,1.7,-2)]),
 (7.0,9.6,[(7.0,720,1080,1.75,3),(9.6,715,1020,2.0,-2)]),
 (9.6,11.5,[(9.6,720,1000,1.9,-4),(11.5,725,960,2.15,2)]),
 (11.5,14.6,[(11.5,720,1000,2.1,3),(13.0,720,1300,1.2,-1),(14.6,720,1330,1.1,0)])]
SHAKE={7.0}
def camera(t):
    for t0,t1,kf in SHOTS:
        if t0<=t<t1 or t>=SHOTS[-1][1]:
            c=list(kf[-1][1:])
            for (a,*pa),(b,*pb) in zip(kf,kf[1:]):
                if a<=t<=b: x=eio((t-a)/(b-a)); c=[lerp(p,q,x) for p,q in zip(pa,pb)]; break
            k=t-t0; c[2]*=1+0.10*max(0,1-k/0.25)
            c[0]+=math.sin(t*2.1)*4+math.sin(t*4.7)*2; c[1]+=math.cos(t*1.7)*4
            if t0 in SHAKE and k<0.4: c[0]+=math.sin(k*70)*18*(1-k/0.4); c[1]+=math.cos(k*60)*12*(1-k/0.4)
            return c,t0
def layer_crop(img,cx,cy,z,par):
    cx=WW/2+(cx-WW/2)*par; cy=WH/2+(cy-WH/2)*par
    vw=WW/ z; vh=vw*OH/OW
    box=(cx-vw/2,cy-vh/2,cx+vw/2,cy+vh/2)
    return img.transform((OW,OH),Image.EXTENT,box,Image.BILINEAR)
def to_screen(x,y,cx,cy,z):
    s=OW/(WW/z); return ((x-cx)*s+OW/2,(y-cy)*s+OH/2),s
# ---- character pose timeline
def clip(t,t0,name,a,b,mode="pp",fps=24):
    n=b-a; i=int((t-t0)*fps)
    if mode=="once": i=min(i,n)
    else:
        p=2*n; i=i%p; i=i if i<=n else p-i
    return name,a+i
TL=[(0.0,1.2,"giro",0,76,"once"),(1.2,2.75,"senalar",30,66,"once"),(2.75,5.25,"senalar",78,114,"pp"),
    (5.25,7.0,"sorpresa",48,90,"once"),(7.0,9.6,"pensar",30,72,"pp"),(9.6,11.5,"pensar",76,100,"once"),
    (11.5,13.6,"reir",48,96,"once"),(13.6,99,"reir",96,112,"pp")]
def char_sprite(t):
    for t0,t1,nm,a,b,m in TL:
        if t0<=t<t1:
            if nm=="giro": n=b-a; i=min(n,int((t-t0)/(t1-t0)*n)); return (nm,a+i),(None)
            return clip(t,t0,nm,a,b,m),(t0 if t0>0 else None)
F={}
def font(px):
    px=int(px)
    if px not in F: F[px]=ImageFont.truetype(FONT,px)
    return F[px]
def draw_heart(d,x,y,r,col=(235,60,80),out=(60,10,20),ow=6):
    pts=[]
    for k in range(60):
        a=k/60*2*math.pi; hx=16*math.sin(a)**3; hy=-(13*math.cos(a)-5*math.cos(2*a)-2*math.cos(3*a)-math.cos(4*a))
        pts.append((x+hx*r/17,y+hy*r/17))
    d.polygon(pts,fill=col,outline=out,width=ow)
    d.ellipse((x-r*0.55,y-r*0.55,x-r*0.25,y-r*0.3),fill=(255,170,180))
def sticker(img,txt,cx,cy,col,t,t0,t1,size=64,rot=-4):
    if not(t0<=t<t1): return
    cx*=K; cy*=K; size*=K
    s=bounce(t-t0)*(1-ease((t-(t1-0.15))/0.15) if t>t1-0.15 else 1)
    if s<=0.02: return
    f=font(size); d0=ImageDraw.Draw(img)
    bb=d0.textbbox((0,0),txt,font=f,stroke_width=int(7*K))
    w,h=bb[2]-bb[0]+40,bb[3]-bb[1]+40
    im=Image.new("RGBA",(w,h),(0,0,0,0)); dd=ImageDraw.Draw(im)
    dd.text((20-bb[0]+6,20-bb[1]+9),txt,font=f,fill=(0,0,0,120),stroke_width=int(7*K),stroke_fill=(0,0,0,120))
    dd.text((20-bb[0],20-bb[1]),txt,font=f,fill=col,stroke_width=int(7*K),stroke_fill=(40,15,10))
    fit=min(1,(OW*0.92)/w)
    im=im.resize((max(1,int(w*s*fit)),max(1,int(h*s*fit))),Image.BICUBIC).rotate(rot+math.sin(t*3)*2,expand=True,resample=Image.BICUBIC)
    img.paste(im,(int(cx-im.width/2),int(cy-im.height/2)),im)
def subtitles(img,t):
    for c in chunks:
        words,end=c[:-1],c[-1]
        if not(words[0][1]<=t<end): continue
        k=t-words[0][1]; s=0.85+0.15*bounce(k) if k<0.6 else 1.0
        f=font(62*K); d=ImageDraw.Draw(img)
        toks=[w[0].upper() for w in words]
        widths=[d.textbbox((0,0),w,font=f,stroke_width=int(8*K))[2] for w in toks]
        gap=int(18*K); total=sum(widths)+gap*(len(toks)-1)
        im=Image.new("RGBA",(int(total+60),int(150*K)),(0,0,0,0)); dd=ImageDraw.Draw(im); x=30
        for (w,a,b),tok,wd in zip(words,toks,widths):
            active=a<=t<b or (t>=b and (w,a,b)==words[-1]); said=t>=a
            col=(255,214,40) if active else ((255,255,255) if said else (255,255,255,160))
            if active and tok.strip("¿?¡!,.…") in KEY: col=(90,230,140)
            yoff=-15*max(0,1-(t-a)/0.15) if said and t-a<0.15 else 0
            dd.text((x+6,45+yoff+9),tok,font=f,fill=(0,0,0,150),stroke_width=int(8*K),stroke_fill=(0,0,0,150))
            dd.text((x,45+yoff),tok,font=f,fill=col,stroke_width=int(8*K),stroke_fill=(15,10,20)); x+=wd+gap
        fit=min(1,(OW*0.92)/im.width)*s
        im=im.resize((max(1,int(im.width*fit)),max(1,int(im.height*fit))),Image.BICUBIC)
        img.paste(im,(int(OW/2-im.width/2),int(OH*0.74-im.height/2)),im)
def frame(t):
    (cx,cy,z,rot),t0=camera(t)
    blur=z>2.0
    img=layer_crop(BGB if blur else BG,cx,cy,z,0.85).convert("RGBA")
    if 1.4<z<=2.0:
        img=Image.blend(img,layer_crop(BGB,cx,cy,z,0.85).convert("RGBA"),(z-1.4)/0.6)
    # character
    (nm,fi),ps=char_sprite(t)
    spr=libframe(nm,fi); m=META[nm]
    sc=1600/m["h"]
    talk=env(t)
    breath=1+0.008*math.sin(t*2.4)+0.01*talk
    pop=1.0
    if ps is not None and t-ps<0.3: pop=0.95+0.05*bounce(t-ps)
    sway=math.sin(t*1.6)*1.2+(math.sin(t*9)*0.8*talk)
    feet=(720,2230)
    (sx,sy),s=to_screen(*feet,cx,cy,z)
    w=int(spr.width*sc*s*pop); h=int(spr.height*sc*s*pop*breath); foot=(spr.height-m['feet'])*sc*s*pop*breath
    # shadow
    sh=Image.new("RGBA",(OW,OH),(0,0,0,0)); sd=ImageDraw.Draw(sh)
    sd.ellipse((sx-w*0.32,sy-30*s,sx+w*0.32,sy+30*s),fill=(60,30,20,110))
    img=Image.alpha_composite(img,sh.filter(ImageFilter.GaussianBlur(max(1,12*s))))
    if w>2 and h>2:
        im=spr.resize((w,h),Image.LANCZOS).rotate(sway,expand=True,resample=Image.BICUBIC,center=(w/2,h))
        bob=-abs(math.sin(t*7))*14*s*talk
        img.paste(im,(int(sx-im.width/2),int(sy-im.height+foot+bob)),im)
    # hearts / graphics in world
    d=ImageDraw.Draw(img)
    def emoji(ch,wx,wy,size,t0,t1,wob=6,screen=False):
        if not(t0<=t<t1): return
        if screen: ex,ey,s2=wx*K,wy*K,K
        else: (ex,ey),s2=to_screen(wx,wy,cx,cy,z)
        s=bounce(t-t0)*(1-ease((t-(t1-0.15))/0.15) if t>t1-0.15 else 1)
        if s<=0.02: return
        e=Image.new("RGBA",(136,136),(0,0,0,0)); ImageDraw.Draw(e).text((4,4),ch,font=EMO,embedded_color=True)
        px=max(2,int(size*s2*s)); e=e.resize((px,px),Image.BICUBIC).rotate(math.sin(t*4)*wob,expand=True,resample=Image.BICUBIC)
        img.alpha_composite(e,(int(ex-e.width/2),int(ey-e.height/2+math.sin(t*3)*6*s2)))
    emoji("🥱",600,430,150,0.3,2.75,screen=True)
    emoji("🧠",600,420,170,3.4,5.25,screen=True)
    emoji("🤔",600,440,160,7.3,9.6,screen=True)
    emoji("💡",600,400,150,10.0,11.5,screen=True)
    if t>11.9:
        for k in range(7):
            u=((t-11.9)*0.35+k/7)%1; wx=(330+k*40 if k%2 else 1110-k*30)+math.sin(u*8+k)*40; wy=1700-u*1300
            emoji("❤️",wx,wy,90+20*(k%3),11.9+k*0.08,14.6,10)
    emoji("😂",600,420,150,11.6,13.4,screen=True)
    # foreground plant (parallax)
    fg=layer_crop(FG,cx,cy,z,1.12)
    if blur: fg=fg.filter(ImageFilter.GaussianBlur(6))
    img=Image.alpha_composite(img,fg)
    # roll
    if abs(rot)>0.05:
        img=img.rotate(rot,resample=Image.BICUBIC,expand=False)
        zf=1+abs(math.sin(math.radians(rot)))*1.25; w2,h2=int(OW/zf),int(OH/zf)
        img=img.crop(((OW-w2)//2,(OH-h2)//2,(OW-w2)//2+w2,(OH-h2)//2+h2)).resize((OW,OH),Image.BICUBIC)
    # flash on cut
    k=t-t0
    if t0>0 and k<0.08: img=Image.blend(img,Image.new("RGBA",(OW,OH),(255,255,255,255)),0.5*(1-k/0.08))
    # overlays
    sticker(img,"¿BOSTEZO CONTAGIOSO?",360,170,(255,214,40),t,(wtime("contagioso") or 1.2),2.75,58,-4)
    sticker(img,"TU CEREBRO LO COPIA",360,170,(90,230,140),t,(wtime("cerebro") or 3.8),5.25,60,3)
    sticker(img,"¡SIN DARTE CUENTA!",360,170,(255,214,40),t,5.4,7.0,62,-3)
    emoji("😲",600,420,150,5.4,7.0,screen=True)
    sticker(img,"¿POR QUÉ?",360,175,(255,90,90),t,(wtime("por") or 8.4),9.6,84,4)
    sticker(img,"DATO CURIOSO",360,170,(255,214,40),t,(wtime("curioso") or 10.6),11.5,70,-4)
    sticker(img,"CON QUIEN QUIERES",360,170,(255,120,160),t,(wtime("quieres") or 13.0),14.6,62,3)
    subtitles(img,t)
    # vignette
    return img.convert("RGB")
VIG=None
if __name__=="__main__":
    out=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3])
    for i in range(a,min(b,int(FPS*DUR))): frame(i/FPS).save(f"{out}/f{i:04d}.png")
