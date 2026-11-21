import math, sys, json, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OW,OH=1080,1920; K=1.5; FPS=30; DUR=49.5; AOFF=1.5
FONT="/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
BG=Image.open("bg_back.png"); BGB=Image.open("bg_back_blur.png"); FG=Image.open("bg_fore.png")
WW,WH=BG.size
META=json.load(open("../lib2/meta.json"))
@functools.lru_cache(maxsize=10)
def libframe(name,i): return Image.open(f"../{META[name]['dir']}/{name}/{i+1:03d}.webp").convert("RGBA")
E2H=560; HEMY=2230-1.05*E2H
EMOF=ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",109)
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
# ---------- words
WORDS=[(w,a+AOFF,b+AOFF) for w,a,b in json.load(open("words.json"))]
WORDS[-1]=(WORDS[-1][0],WORDS[-1][1],max(WORDS[-1][2],45.8))
def W(i): return WORDS[i][1]
KEY={"ALARMA?","CASUALIDAD.","CEREBRO","RELOJ","NÚCLEO","SUPRAQUIASMÁTICO,","INCREÍBLE.","EXPERIMENTO,","HORMONAS","HORA","ANTES.","MISMA","SOLO.","OJO,","CONFUNDES,","CANSADO.","DÍAS.","COMENTARIOS."}
chunks=[]; cur=[]
for it in WORDS:
    cur.append(it)
    if len(cur)==3 or sum(len(x[0]) for x in cur)>=13 or it[0][-1] in ",.?:…!":
        chunks.append(cur); cur=[]
if cur: chunks.append(cur)
for i,c in enumerate(chunks):
    nxt=chunks[i+1][0][1] if i+1<len(chunks) else c[-1][2]+1.5
    c.append(min(nxt,c[-1][2]+0.4))
# ---------- reaction timeline
TL=[(0.0,1.6,"giro",0,76,"once"),(1.6,5.5,"senalar",0,26,"pp"),(5.5,7.0,"senalar",30,66,"once"),
    (7.0,9.2,"reir",10,35,"pp"),(9.2,11.9,"pensar",30,72,"pp"),(11.9,15.3,"sorpresa",0,24,"pp"),
    (15.3,17.4,"sorpresa",48,90,"once"),(17.4,21.4,"senalar",78,114,"pp"),(21.4,24.4,"senalar",0,26,"pp"),
    (24.4,26.4,"sorpresa",48,90,"once"),(26.4,29.4,"reir",48,96,"once"),(29.4,32.8,"pensar",76,100,"once"),
    (32.8,34.9,"reir",10,35,"pp"),(34.9,37.5,"sorpresa",96,114,"pp"),(37.5,40.3,"sorpresa",124,142,"once"),
    (40.3,43.4,"senalar",30,66,"once"),(43.4,46.6,"reir",48,96,"once"),(46.6,99,"reir",96,112,"pp")]
def char_sprite(t):
    for t0,t1,nm,a,b,m in TL:
        if t0<=t<t1:
            if nm=="giro": n=b-a; return (nm,a+min(n,int((t-t0)/(t1-t0)*n))),None
            n=b-a; i=int((t-t0)*24)
            if m=="once": i=min(i,n)
            else: p=2*n; i=i%p; i=i if i<=n else p-i
            return (nm,a+i),t0
# ---------- shots
FR={"W":((720,1350,1.05),(715,1300,1.2)),"M":((720,1380,1.5),(720,1340,1.7)),"C":((720,1280,2.0),(725,1250,2.25)),
    "L":((700,1470,1.4),(730,1400,1.6)),"P":((720,1270,1.9),(720,1330,1.15))}
PLAN=[(0,"W",0),(1.6,"M",-2),(5.5,"C",3),(7.0,"M",-3),(9.2,"C",2),(11.9,"W",-2),(15.3,"C",4),(17.4,"M",-2),
      (21.4,"L",3),(24.4,"C",-3),(26.4,"M",2),(29.4,"C",-2),(32.8,"W",3),(34.9,"C",-4),(37.5,"M",2),(40.3,"L",-3),(43.4,"P",0)]
SHAKE={5.5,15.3,24.4,34.9}
def camera(t):
    for i,(t0,f,r) in enumerate(PLAN):
        t1=PLAN[i+1][0] if i+1<len(PLAN) else DUR
        if t0<=t<t1 or (i==len(PLAN)-1 and t>=t0):
            (a,b)=FR[f]; x=eio((t-t0)/(t1-t0))
            c=[lerp(a[0],b[0],x),lerp(a[1],b[1],x),lerp(a[2],b[2],x),lerp(r,-r*0.5,x)]
            k=t-t0; c[2]*=1+0.10*max(0,1-k/0.25)
            c[0]+=math.sin(t*2.1)*4+math.sin(t*4.7)*2; c[1]+=math.cos(t*1.7)*4
            if t0 in SHAKE and k<0.4: c[0]+=math.sin(k*70)*18*(1-k/0.4); c[1]+=math.cos(k*60)*12*(1-k/0.4)
            return c,t0
def layer_crop(img,cx,cy,z,par):
    cx=WW/2+(cx-WW/2)*par; cy=WH/2+(cy-WH/2)*par
    vw=WW/z; vh=vw*OH/OW
    return img.transform((OW,OH),Image.EXTENT,(cx-vw/2,cy-vh/2,cx+vw/2,cy+vh/2),Image.BILINEAR)
def to_screen(x,y,cx,cy,z):
    s=OW/(WW/z); return ((x-cx)*s+OW/2,(y-cy)*s+OH/2),s
F={}
def font(px):
    px=int(px)
    if px not in F: F[px]=ImageFont.truetype(FONT,px)
    return F[px]
# ---------- overlays plan
STICK=[("¡NO ES CASUALIDAD!",(255,214,40),W(15),7.0,-4),
       ("NÚCLEO\nSUPRAQUIASMÁTICO",(90,230,140),W(27),11.9,3),
       ("¡1 HORA ANTES!",(255,90,90),W(67),26.4,-4),
       ("MISMA HORA,\nTODOS LOS DÍAS",(255,214,40),W(121),43.4,3)]
R=(600,420); L=(125,430); R2=(600,640); L2=(125,660)
EMO=[("⏰",(560,560),230,0.0,1.6,14),("😴",R,150,W(5),4.0,6),("⏰",L,150,W(14),5.5,10),
     ("🧠",R,160,W(19),9.2,6),("⏱️",L,140,W(22),9.2,8),("😴",R,140,W(32),W(35),6),("☀️",L,150,W(35),15.3,6),
     ("🤯",R,160,W(40),17.4,6),("🧪",L,150,W(43),21.4,6),("👥",R,150,W(48),21.4,6),("⚡",R,150,W(64),24.4,10),
     ("😂",R,150,W(72),29.4,6),("🔁",L,150,W(86),32.8,8),("✅",R,150,W(100),34.9,6),("⚠️",R,160,W(102),37.5,8),
     ("😵",L,150,W(110),W(116),6),("🥱",R,150,W(116),40.3,6),("✅",L2,140,W(121),43.4,6),("💬",R,160,W(130),DUR,6),("👇",L,140,W(130)+0.4,DUR,6)]
def sticker(img,txt,col,t,t0,t1,rot,cx=360,cy=190,size=60):
    if not(t0<=t<t1): return
    cx*=K; cy*=K; size*=K
    s=bounce(t-t0)*(1-ease((t-(t1-0.15))/0.15) if t>t1-0.15 else 1)
    if s<=0.02: return
    f=font(size); d0=ImageDraw.Draw(img); sw=int(7*K)
    bb=d0.textbbox((0,0),txt,font=f,stroke_width=sw,align='center')
    w,h=int(bb[2]-bb[0]+40),int(bb[3]-bb[1]+40)
    im=Image.new("RGBA",(w,h),(0,0,0,0)); dd=ImageDraw.Draw(im)
    dd.text((20-bb[0]+6,20-bb[1]+9),txt,font=f,fill=(0,0,0,120),stroke_width=sw,stroke_fill=(0,0,0,120),align='center')
    dd.text((20-bb[0],20-bb[1]),txt,font=f,fill=col,stroke_width=sw,stroke_fill=(40,15,10),align='center')
    fit=min(1,(OW*0.92)/w)
    im=im.resize((max(1,int(w*s*fit)),max(1,int(h*s*fit))),Image.BICUBIC).rotate(rot+math.sin(t*3)*2,expand=True,resample=Image.BICUBIC)
    img.paste(im,(int(cx-im.width/2),int(cy-im.height/2)),im)
@functools.lru_cache(maxsize=64)
def emoji_img(ch):
    e=Image.new("RGBA",(160,160),(0,0,0,0)); ImageDraw.Draw(e).text((8,8),ch,font=EMOF,embedded_color=True)
    return e.crop(e.getbbox())
def emoji(img,t,ch,pos,size,t0,t1,wob):
    if not(t0<=t<t1): return
    s=bounce(t-t0)*(1-ease((t-(t1-0.15))/0.15) if t>t1-0.15 else 1)
    if s<=0.02: return
    e=emoji_img(ch); px=max(2,int(size*K*s))
    e=e.resize((px,int(px*e.height/e.width)),Image.LANCZOS)
    ang=math.sin(t*4)*wob + (math.sin(t*40)*12 if ch=="⏰" and t<1.6 else 0)
    e=e.rotate(ang,expand=True,resample=Image.BICUBIC)
    img.alpha_composite(e,(int(pos[0]*K-e.width/2),int(pos[1]*K-e.height/2+math.sin(t*3+pos[0])*8)))
def subtitles(img,t):
    for c in chunks:
        words,end=c[:-1],c[-1]
        if not(words[0][1]<=t<end): continue
        k=t-words[0][1]; s=0.85+0.15*bounce(k) if k<0.6 else 1.0
        f=font(62*K); d=ImageDraw.Draw(img); sw=int(8*K)
        toks=[w[0].upper() for w in words]
        widths=[d.textbbox((0,0),w,font=f,stroke_width=sw)[2] for w in toks]
        gap=int(18*K); total=sum(widths)+gap*(len(toks)-1)
        im=Image.new("RGBA",(int(total+60),int(150*K)),(0,0,0,0)); dd=ImageDraw.Draw(im); x=30
        for (w,a,b),tok,wd in zip(words,toks,widths):
            active=a<=t<b or (t>=b and (w,a,b)==words[-1]); said=t>=a
            col=(255,214,40) if active else ((255,255,255) if said else (255,255,255,160))
            if active and tok in KEY: col=(90,230,140)
            yoff=-15*max(0,1-(t-a)/0.15) if said and t-a<0.15 else 0
            dd.text((x+6,45+yoff+9),tok,font=f,fill=(0,0,0,150),stroke_width=sw,stroke_fill=(0,0,0,150))
            dd.text((x,45+yoff),tok,font=f,fill=col,stroke_width=sw,stroke_fill=(15,10,20)); x+=wd+gap
        fit=min(1,(OW*0.92)/im.width)*s
        im=im.resize((max(1,int(im.width*fit)),max(1,int(im.height*fit))),Image.BICUBIC)
        img.paste(im,(int(OW/2-im.width/2),int(OH*0.74-im.height/2)),im)
def frame(t):
    (cx,cy,z,rot),t0=camera(t)
    (nm,fi),ps=char_sprite(t); m=META[nm]; spr=libframe(nm,fi)
    ws=E2H/m["e2h"]; bot=HEMY-m["hem"]*ws+spr.height*ws
    if bot<2190:
        lim=bot-30; z=max(z,WW*(OH/OW)/lim*1.02); vh=(WW/z)*OH/OW
        if cy+vh/2>lim: cy=lim-vh/2
        cy=max(cy,vh/2)
    blur=z>2.0
    img=layer_crop(BGB if blur else BG,cx,cy,z,0.85).convert("RGBA")
    if 1.4<z<=2.0: img=Image.blend(img,layer_crop(BGB,cx,cy,z,0.85).convert("RGBA"),(z-1.4)/0.6)
    talk=env(t)
    breath=1+0.008*math.sin(t*2.4)+0.01*talk
    pop=0.95+0.05*bounce(t-ps) if ps and t-ps<0.3 else 1.0
    sway=math.sin(t*1.6)*1.2+math.sin(t*9)*0.8*talk
    wsc=ws*pop
    top_w=HEMY-m["hem"]*wsc*breath; left_w=720-m["cx"]*wsc
    (sx,sy),s=to_screen(left_w,top_w,cx,cy,z)
    w=int(spr.width*wsc*s); h=int(spr.height*wsc*s*breath)
    if bot>=2190:
        (fx,fy),_=to_screen(720,2230,cx,cy,z)
        sh=Image.new("RGBA",(OW,OH),(0,0,0,0)); ImageDraw.Draw(sh).ellipse((fx-w*0.32,fy-30*s,fx+w*0.32,fy+30*s),fill=(60,30,20,110))
        img=Image.alpha_composite(img,sh.filter(ImageFilter.GaussianBlur(max(1,12*s))))
    if w>2 and h>2:
        im=spr.resize((w,h),Image.LANCZOS).rotate(sway,expand=True,resample=Image.BICUBIC,center=(w/2,h))
        bob=-abs(math.sin(t*7))*10*s*talk
        img.paste(im,(int(sx-(im.width-w)/2),int(sy-(im.height-h)+bob)),im)
    fg=layer_crop(FG,cx,cy,z,1.12)
    if blur: fg=fg.filter(ImageFilter.GaussianBlur(6))
    img=Image.alpha_composite(img,fg)
    if abs(rot)>0.05:
        img=img.rotate(rot,resample=Image.BICUBIC,expand=False)
        zf=1+abs(math.sin(math.radians(rot)))*1.25; w2,h2=int(OW/zf),int(OH/zf)
        img=img.crop(((OW-w2)//2,(OH-h2)//2,(OW-w2)//2+w2,(OH-h2)//2+h2)).resize((OW,OH),Image.BICUBIC)
    k=t-t0
    if t0>0 and k<0.08: img=Image.blend(img,Image.new("RGBA",(OW,OH),(255,255,255,255)),0.5*(1-k/0.08))
    for e in EMO: emoji(img,t,*e)
    for txt,col,a,b,r in STICK: sticker(img,txt,col,t,a,b,r)
    subtitles(img,t)
    return img.convert("RGB")
if __name__=="__main__":
    out=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3])
    for i in range(a,min(b,int(FPS*DUR))): frame(i/FPS).save(f"{out}/f{i:04d}.png")
