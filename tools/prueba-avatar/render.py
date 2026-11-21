import math, sys, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OW,OH=720,1280; FPS=30; DUR=10.0; AOFF=0.5
FONT="/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
BG=Image.open("bg_back.png"); BGB=Image.open("bg_back_blur.png"); FG=Image.open("bg_fore.png")
WW,WH=BG.size
SPR={n:Image.open(n+".png") for n in ["present","surprised","angry"]}
TURN=[Image.open(f) for f in sorted(glob.glob("turn/t*.png"))]
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
segs=[(0.16,3.02,"¿Sabías que tu corazón late unas cien mil veces al día?"),
      (3.71,6.68,"¡Eso son más de treinta y cinco millones de latidos al año…"),
      (6.88,8.47,"sin descansar ni un segundo!")]
KEY={"CORAZÓN","CIEN","MIL","MILLONES","LATIDOS","DESCANSAR","SEGUNDO!","SEGUNDO"}
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
SHOTS=[(0.0,3.75,[(0,720,1350,1.0,0),(1.6,720,1250,1.15,-1.5),(3.75,700,1050,1.55,1.5)]),
       (3.75,7.25,[(3.75,720,820,2.6,-3),(5.5,720,800,2.9,2),(7.25,730,790,3.2,-1)]),
       (7.25,10.0,[(7.25,720,1150,1.9,4),(8.6,720,1300,1.25,-2),(10.0,720,1320,1.15,0)])]
def camera(t):
    for t0,t1,kf in SHOTS:
        if t0<=t<t1 or t>=SHOTS[-1][1]:
            c=list(kf[-1][1:])
            for (a,*pa),(b,*pb) in zip(kf,kf[1:]):
                if a<=t<=b: x=eio((t-a)/(b-a)); c=[lerp(p,q,x) for p,q in zip(pa,pb)]; break
            k=t-t0; c[2]*=1+0.10*max(0,1-k/0.25)
            c[0]+=math.sin(t*2.1)*4+math.sin(t*4.7)*2; c[1]+=math.cos(t*1.7)*4
            if t0==3.75 and k<0.4: c[0]+=math.sin(k*70)*18*(1-k/0.4); c[1]+=math.cos(k*60)*12*(1-k/0.4)
            return c,t0
def layer_crop(img,cx,cy,z,par):
    cx=WW/2+(cx-WW/2)*par; cy=WH/2+(cy-WH/2)*par
    vw=WW/ z; vh=vw*OH/OW
    box=(cx-vw/2,cy-vh/2,cx+vw/2,cy+vh/2)
    return img.transform((OW,OH),Image.EXTENT,box,Image.BILINEAR)
def to_screen(x,y,cx,cy,z):
    s=OW/(WW/z); return ((x-cx)*s+OW/2,(y-cy)*s+OH/2),s
# ---- character pose timeline
def char_sprite(t):
    if t<1.55:
        i=min(len(TURN)-1,int(t/1.55*len(TURN))); return TURN[i],None
    if t<3.75: return SPR["present"],1.55
    if t<7.25: return SPR["surprised"],3.75
    return SPR["angry"],7.25
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
    s=bounce(t-t0)*(1-ease((t-(t1-0.15))/0.15) if t>t1-0.15 else 1)
    if s<=0.02: return
    f=font(size); d0=ImageDraw.Draw(img)
    bb=d0.textbbox((0,0),txt,font=f,stroke_width=7)
    w,h=bb[2]-bb[0]+40,bb[3]-bb[1]+40
    im=Image.new("RGBA",(w,h),(0,0,0,0)); dd=ImageDraw.Draw(im)
    dd.text((20-bb[0]+4,20-bb[1]+6),txt,font=f,fill=(0,0,0,120),stroke_width=7,stroke_fill=(0,0,0,120))
    dd.text((20-bb[0],20-bb[1]),txt,font=f,fill=col,stroke_width=7,stroke_fill=(40,15,10))
    fit=min(1,(OW*0.92)/w)
    im=im.resize((max(1,int(w*s*fit)),max(1,int(h*s*fit))),Image.BICUBIC).rotate(rot+math.sin(t*3)*2,expand=True,resample=Image.BICUBIC)
    img.paste(im,(int(cx-im.width/2),int(cy-im.height/2)),im)
def subtitles(img,t):
    for c in chunks:
        words,end=c[:-1],c[-1]
        if not(words[0][1]<=t<end): continue
        k=t-words[0][1]; s=0.85+0.15*bounce(k) if k<0.6 else 1.0
        f=font(62); d=ImageDraw.Draw(img)
        toks=[w[0].upper() for w in words]
        widths=[d.textbbox((0,0),w,font=f,stroke_width=8)[2] for w in toks]
        gap=18; total=sum(widths)+gap*(len(toks)-1)
        im=Image.new("RGBA",(int(total+60),150),(0,0,0,0)); dd=ImageDraw.Draw(im); x=30
        for (w,a,b),tok,wd in zip(words,toks,widths):
            active=a<=t<b or (t>=b and (w,a,b)==words[-1]); said=t>=a
            col=(255,214,40) if active else ((255,255,255) if said else (255,255,255,160))
            if active and tok.strip("¿?¡!,.…") in KEY: col=(90,230,140)
            yoff=-10*max(0,1-(t-a)/0.15) if said and t-a<0.15 else 0
            dd.text((x+4,30+yoff+6),tok,font=f,fill=(0,0,0,150),stroke_width=8,stroke_fill=(0,0,0,150))
            dd.text((x,30+yoff),tok,font=f,fill=col,stroke_width=8,stroke_fill=(15,10,20)); x+=wd+gap
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
    spr,ps=char_sprite(t)
    H=1650; sc=H/spr.height
    talk=env(t)
    breath=1+0.012*math.sin(t*2.4)+0.02*talk
    pop=1.0
    if ps is not None and t-ps<0.5: pop=0.85+0.15*bounce(t-ps)
    sway=math.sin(t*1.6)*2.0+ (math.sin(t*9)*1.5*talk)
    feet=(720,2230)
    (sx,sy),s=to_screen(*feet,cx,cy,z)
    w=int(spr.width*sc*s*pop); h=int(spr.height*sc*s*pop*breath)
    # shadow
    sh=Image.new("RGBA",(OW,OH),(0,0,0,0)); sd=ImageDraw.Draw(sh)
    sd.ellipse((sx-w*0.45,sy-30*s,sx+w*0.45,sy+30*s),fill=(60,30,20,110))
    img=Image.alpha_composite(img,sh.filter(ImageFilter.GaussianBlur(max(1,12*s))))
    if w>2 and h>2:
        im=spr.resize((w,h),Image.BICUBIC).rotate(sway,expand=True,resample=Image.BICUBIC,center=(w/2,h))
        bob=-abs(math.sin(t*7))*14*s*talk
        img.paste(im,(int(sx-im.width/2),int(sy-im.height+bob+ (im.height-h)*0.0)),im)
    # hearts / graphics in world
    d=ImageDraw.Draw(img)
    if 1.7<t<3.75:
        (hx,hy),s2=to_screen(1150,1020,cx,cy,z); beat=1+0.15*abs(math.sin(t*math.pi*1.3))**8
        r=110*s2*bounce(t-1.7)*beat; draw_heart(d,hx,hy,r,ow=max(2,int(6*s2)))
    if 7.4<t:
        (hx,hy),s2=to_screen(1130,1050,cx,cy,z)
        beat=1+0.2*abs(math.sin(t*math.pi*2.2))**8
        r=120*s2*bounce(t-7.4)*beat
        for k in range(10):
            a=k*math.pi/5+t; rr=r*1.5
            d.line((hx+math.cos(a)*rr,hy+math.sin(a)*rr,hx+math.cos(a)*rr*1.3,hy+math.sin(a)*rr*1.3),fill=(255,214,40),width=max(2,int(8*s2)))
        draw_heart(d,hx,hy,r,ow=max(2,int(6*s2)))
    # foreground plant (parallax)
    fg=layer_crop(FG,cx,cy,z,1.15)
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
    tc=wtime("cien") or 1.5
    sticker(img,"100.000 LATIDOS",360,170,(255,214,40),t,tc,3.75,64,-4)
    sticker(img,"¡AL DÍA!",360,250,(255,90,90),t,(wtime("día") or 3.0),3.75,58,5)
    tm=wtime("treinta") or 4.6
    if tm<=t<7.25:
        n=int(35_000_000*ease((t-tm)/1.6)); txt=f"{n:,}".replace(",",".")
        sticker(img,txt,360,170,(255,214,40),t,tm,7.25,80,-3)
        sticker(img,"LATIDOS AL AÑO",360,260,(255,255,255),t,tm+0.3,7.25,48,3)
    sticker(img,"¡SIN DESCANSAR!",360,170,(255,90,90),t,(wtime("descansar") or 7.5),10.0,70,-4)
    subtitles(img,t)
    # vignette
    return img.convert("RGB")
VIG=None
if __name__=="__main__":
    out=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3])
    for i in range(a,min(b,int(FPS*DUR))): frame(i/FPS).save(f"{out}/f{i:04d}.png")
