import math, sys, os
from PIL import Image, ImageDraw, ImageFont
OW,OH=720,1280; SS=2; CW,CH=OW*SS,OH*SS
FPS=30; DUR=15.3
FONT="/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
def ease(x): x=max(0.0,min(1.0,x)); return 1-(1-x)**3
def eio(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)
def lerp(a,b,x): return a+(b-a)*x
def bounce(x):
    if x<=0: return 0.0
    if x>=0.6: return 1.0
    return ease(x/0.35)*(1+0.18*math.sin(x*16)*(1-x/0.6))
# ---------- timing
segs=[(0.35,2.21,"¿Por qué abres la nevera cuando estás aburrido?"),(2.64,3.21,"No es hambre."),
(3.61,5.94,"Es tu cerebro buscando una recompensa rápida."),(6.54,7.84,"La comida libera dopamina,"),
(8.17,9.57,"y tu cerebro aprende el truco."),(10.09,10.50,"Por eso,"),(10.82,11.64,"la próxima vez,"),
(11.93,12.57,"pregúntate:"),(12.97,13.61,"¿tengo hambre…"),(13.98,14.90,"o solo estoy aburrido?")]
KEY={"NEVERA","ABURRIDO","HAMBRE","CEREBRO","RECOMPENSA","DOPAMINA","TRUCO","PRÓXIMA","PREGÚNTATE"}
chunks=[]
for a,b,txt in segs:
    ws=txt.split(); wt=[len(w)+2 for w in ws]; tot=sum(wt); t=a; timed=[]
    for w,x in zip(ws,wt):
        d=(b-a)*x/tot; timed.append((w,t,t+d)); t+=d
    cur=[]
    for it in timed:
        cur.append(it)
        if len(cur)==3 or sum(len(x[0]) for x in cur)>=13 or it[0][-1] in ",.?:…":
            chunks.append(cur); cur=[]
    if cur: chunks.append(cur)
for i,c in enumerate(chunks):  # hold chunk until next starts (max +0.35)
    nxt=chunks[i+1][0][1] if i+1<len(chunks) else c[-1][2]+0.6
    c.append(min(nxt,c[-1][2]+0.35))
# ---------- camera keyframes: (t, cx, cy, zoom, rot)
SH=[ # shots
 (0.0, 2.25,  [(0,300,520,0.95,-2),(2.25,380,470,1.25,2)]),          # kitchen wide, push in
 (2.25,3.55,  [(2.25,270,620,2.3,-4),(3.55,270,640,2.6,3)]),         # belly close-up
 (3.55,6.05,  [(3.55,275,250,2.0,0),(4.1,275,230,3.2,-3),(6.05,280,225,3.6,3)]), # into head
 (6.05,9.65,  [(6.05,340,400,1.45,4),(7.8,320,340,1.7,-2),(8.8,300,250,2.8,0),(9.65,300,240,3.0,2)]), # dopamine travel
 (9.65,12.9,  [(9.65,330,520,1.0,-3),(12.9,360,500,1.35,2)]),        # wide pan to fridge
 (12.9,15.4,  [(12.9,290,240,3.4,-5),(14.2,285,235,3.0,4),(15.4,285,235,3.15,0)]), # face close-up
]
def camera(t):
    for t0,t1,kf in SH:
        if t0<=t<t1 or (t>=t1 and t1==SH[-1][1]):
            for (a,*pa),(b,*pb) in zip(kf,kf[1:]):
                if a<=t<=b:
                    x=eio((t-a)/(b-a)); c=[lerp(p,q,x) for p,q in zip(pa,pb)]
                    break
            else: c=list(kf[-1][1:])
            # punch-in at shot start
            k=t-t0; c[2]*=1+0.12*max(0,1-k/0.25)
            # handheld shake
            c[0]+=math.sin(t*2.3)*2+math.sin(t*5.1)*1; c[1]+=math.cos(t*1.9)*2
            return c,t0
    return [270,480,1,0],0
class Cam:
    def __init__(s,cx,cy,z): s.cx,s.cy,s.z=cx,cy,z*OW/540*SS
    def p(s,x,y): return ((x-s.cx)*s.z+CW/2,(y-s.cy)*s.z+CH/2)
    def r(s,v): return v*s.z
    def box(s,x0,y0,x1,y1):
        a=s.p(x0,y0); b=s.p(x1,y1); return (a[0],a[1],b[0],b[1])
def RR(d,c,b,rad,**k): d.rounded_rectangle(c.box(*b),radius=c.r(rad),**k)
def EL(d,c,b,**k): d.ellipse(c.box(*b),**k)
def EC(d,c,x,y,r,**k): d.ellipse(c.box(x-r,y-r,x+r,y+r),**k)
def LN(d,c,pts,w,**k): d.line([c.p(*q) for q in pts],width=max(1,int(c.r(w))),**k)
# ---------- scene
def kitchen(d,c,t):
    d.rectangle((0,0,CW,CH),fill=(214,226,246))
    # wall tiles
    for i in range(-2,14):
        for j in range(-2,12):
            x=i*60; y=j*60
            if y<700: d.rectangle(c.box(x+2,y+2,x+58,y+58),fill=(222,233,250))
    # window
    RR(d,c,(30,180,190,400),14,fill=(160,200,240),outline=(250,250,255),width=int(c.r(8)))
    EC(d,c,140,230,24,fill=(255,238,150))
    # counter left
    RR(d,c,(-200,600,150,880),10,fill=(250,214,170)); d.rectangle(c.box(-200,590,160,615),fill=(250,250,255))
    # fridge
    RR(d,c,(400,250,560,860),28,fill=(245,248,255),outline=(190,200,225),width=int(c.r(4)))
    LN(d,c,[(400,470),(560,470)],4,fill=(190,200,225))
    LN(d,c,[(415,320),(415,420)],8,fill=(170,180,210)); LN(d,c,[(415,500),(415,640)],8,fill=(170,180,210))
    # floor
    d.rectangle(c.box(-600,860,1200,1600),fill=(205,196,236))
    for i in range(-10,20): LN(d,c,[(i*80,860),(i*80-120,1600)],2,fill=(190,180,225))
    EL(d,c,(-600,850,1200,875),fill=(196,186,230))
def character(d,c,t,x0,walk,xray,mood,hand_food,brainmood):
    bob=abs(math.sin(t*6))*8*walk + math.sin(t*2.2)*3*(1-walk)
    sway=math.sin(t*3)*4*walk
    dx=x0-270; dy=-bob
    def P(x,y): return (x+dx+sway*(y<600)*0.5, y+dy)
    def B(a,b,cc,e): return (*P(a,b),*P(cc,e))
    EL(d,c,(x0-130,858,x0+130,884),fill=(180,170,220))
    # legs
    lw=math.sin(t*6)*22*walk
    RR(d,c,B(205,740,262,880+lw*0.2),22,fill=(150,140,205)); RR(d,c,B(278,740,335,880-lw*0.2),22,fill=(150,140,205))
    EL(d,c,B(190,862+lw*0.2,262,890+lw*0.2),fill=(90,80,150)); EL(d,c,B(278,862-lw*0.2,350,890-lw*0.2),fill=(90,80,150))
    # arms
    aw=math.sin(t*6)*25*walk
    sx,sy=P(395,380)
    if hand_food:
        LN(d,c,[(sx,sy),(sx+35,sy+110),(sx-10,sy+60)],46,fill=(246,170,200),joint="curve")
        EC(d,c,sx-10,sy+60,30,fill=(250,214,184))
        fx,fy=sx-15,sy+35+math.sin(t*4)*4
        global FOOD; FOOD=(fx,fy)
    else:
        LN(d,c,[(sx,sy),(sx+20+aw*0.3,sy+120),(sx+10+aw,sy+215)],46,fill=(246,170,200),joint="curve")
        EC(d,c,sx+10+aw,sy+215,26,fill=(250,214,184))
    lx,ly=P(145,380)
    LN(d,c,[(lx,ly),(lx-20-aw*0.3,ly+120),(lx-10-aw,ly+215)],46,fill=(246,170,200),joint="curve")
    EC(d,c,lx-10-aw,ly+215,26,fill=(250,214,184))
    # torso
    RR(d,c,B(150,330,390,780),70,fill=(246,170,200))
    if xray:
        RR(d,c,B(176,430,364,760),55,fill=(252,226,236),outline=(235,150,185),width=int(c.r(3)))
        # stomach
        sx2,sy2=P(250,520)
        EL(d,c,(sx2-45,sy2-35,sx2+60,sy2+40),fill=(240,140,170),outline=(210,100,140),width=int(c.r(3)))
        pts=[]
        for i in range(90):
            u=i/89; pts.append(P(270+math.sin(u*math.pi*5)*(55-20*u)+math.sin(t*3+u*8)*3,580+u*160))
        LN(d,c,pts,24,fill=(232,110,140),joint="curve"); LN(d,c,pts,11,fill=(246,150,175),joint="curve")
    if hand_food:
        fx,fy=FOOD
        EC(d,c,fx,fy,44,fill=(220,150,90)); EC(d,c,fx,fy,36,fill=(255,140,190))
        for k in range(7):
            a=k*0.9+1; EC(d,c,fx+math.cos(a)*24,fy+math.sin(a)*24,4,fill=[(255,255,255),(255,220,60),(120,210,255)][k%3])
        EC(d,c,fx,fy,13,fill=(252,226,236))
        EC(d,c,sx-10,sy+60,30,fill=(250,214,184))
    # neck & head
    RR(d,c,B(248,282,292,345),15,fill=(250,214,184))
    hx,hy=P(270,220); tilt=math.sin(t*1.7)*4
    hx+=tilt
    EC(d,c,hx,hy-78,36,fill=(110,70,55))
    EL(d,c,(hx-68,hy-72,hx+68,hy+70),fill=(110,70,55))
    EL(d,c,(hx-66,hy-55,hx+66,hy+72),fill=(250,214,184) if not xray else (252,232,214))
    if xray:
        bm=brainmood; br=44+3*math.sin(t*5)
        EL(d,c,(hx-br,hy-br*0.85-10,hx+br,hy+br*0.85-10),fill=(214,170,214),outline=(170,110,180),width=int(c.r(3)))
        for k in range(-2,3): d.arc(c.box(hx+k*16-12,hy-40,hx+k*16+12,hy-5),200,340,fill=(170,110,180),width=int(c.r(2)))
        look=math.sin(t*2.5)*5 if bm=="search" else 0
        for ex in(-16,16):
            EC(d,c,hx+ex,hy-8,11,fill="white",outline=(60,40,60),width=int(c.r(2)))
            EC(d,c,hx+ex+look,hy-8,5,fill=(40,30,50))
        if bm=="happy": d.arc(c.box(hx-14,hy+2,hx+14,hy+22),20,160,fill=(110,60,110),width=int(c.r(3)))
        else: LN(d,c,[(hx-8,hy+14),(hx+8,hy+14)],3,fill=(110,60,110))
        return (hx,hy-10)
    # face
    blink= (t%3.1)<0.12
    for ex in(-24,24):
        if blink: LN(d,c,[(hx+ex-7,hy+5),(hx+ex+7,hy+5)],3,fill=(60,40,40))
        else: EL(d,c,(hx+ex-7,hy-4,hx+ex+7,hy+13),fill=(60,40,40))
    EC(d,c,hx-40,hy+25,9,fill=(250,180,170)); EC(d,c,hx+40,hy+25,9,fill=(250,180,170))
    if mood=="think":
        LN(d,c,[(hx-12,hy+38),(hx+12,hy+34)],4,fill=(160,90,90))
    elif mood=="sad":
        d.arc(c.box(hx-16,hy+34,hx+16,hy+54),200,340,fill=(160,90,90),width=int(c.r(4)))
    else:
        d.arc(c.box(hx-18,hy+20,hx+18,hy+46),20,160,fill=(160,90,90),width=int(c.r(4)))
    return (hx,hy)
# ---------- overlays (screen space)
def font(px): return ImageFont.truetype(FONT,int(px))
FC={}
def F(px):
    px=int(px)
    if px not in FC: FC[px]=font(px)
    return FC[px]
def sticker(img,txt,cx,cy,col,t,t0,t1,size=64,rot=-4):
    if not(t0<=t<t1): return
    s=bounce(t-t0); out=1-ease((t-(t1-0.15))/0.15) if t>t1-0.15 else 1
    s*=out
    if s<=0.02: return
    f=F(size*SS); d0=ImageDraw.Draw(img)
    bb=d0.textbbox((0,0),txt,font=f,stroke_width=int(7*SS))
    w,h=bb[2]-bb[0]+60,bb[3]-bb[1]+60
    im=Image.new("RGBA",(w,h),(0,0,0,0)); dd=ImageDraw.Draw(im)
    dd.text((30-bb[0]+6,30-bb[1]+8),txt,font=f,fill=(0,0,0,110),stroke_width=int(7*SS),stroke_fill=(0,0,0,110))
    dd.text((30-bb[0],30-bb[1]),txt,font=f,fill=col,stroke_width=int(7*SS),stroke_fill=(40,20,10))
    fit=min(1,(CW*0.9)/w)
    im=im.resize((max(1,int(w*s*fit)),max(1,int(h*s*fit))),Image.BICUBIC).rotate(rot+math.sin(t*3)*2,expand=True,resample=Image.BICUBIC)
    img.paste(im,(int(cx*SS-im.width/2),int(cy*SS-im.height/2)),im)
def icon_x(img,cx,cy,t,t0,t1):
    if not(t0<=t<t1): return
    s=bounce(t-t0); r=60*SS*s; d=ImageDraw.Draw(img); x,y=cx*SS,cy*SS
    d.ellipse((x-r,y-r,x+r,y+r),fill=(235,60,60),outline="white",width=int(8*SS*s+1))
    k=r*0.45; d.line((x-k,y-k,x+k,y+k),fill="white",width=int(16*SS*s+1)); d.line((x-k,y+k,x+k,y-k),fill="white",width=int(16*SS*s+1))
def icon_q(img,pts,t,t0):
    if t<t0: return
    for i,(cx,cy) in enumerate(pts):
        s=bounce(t-t0-i*0.12)
        if s<=0: continue
        f=F(90*SS*s+1); d=ImageDraw.Draw(img)
        y=cy*SS+math.sin(t*4+i)*10*SS
        d.text((cx*SS,y),"?",font=f,fill=(255,214,40),stroke_width=int(6*SS),stroke_fill=(40,20,10),anchor="mm")
def bulb(img,cx,cy,t,t0,t1):
    if not(t0<=t<t1): return
    s=bounce(t-t0); d=ImageDraw.Draw(img); x,y=cx*SS,cy*SS; r=50*SS*s
    for k in range(8):
        a=k*math.pi/4+t; d.line((x+math.cos(a)*r*1.3,y+math.sin(a)*r*1.3,x+math.cos(a)*r*1.75,y+math.sin(a)*r*1.75),fill=(255,214,40),width=int(8*SS*s+1))
    d.ellipse((x-r,y-r,x+r,y+r),fill=(255,230,80),outline=(40,20,10),width=int(6*SS*s+1))
    d.rectangle((x-r*0.4,y+r*0.85,x+r*0.4,y+r*1.35),fill=(150,150,170),outline=(40,20,10),width=int(4*SS*s+1))
def subtitles(img,t):
    for c in chunks:
        words,end=c[:-1],c[-1]
        if not(words[0][1]<=t<end): continue
        k=t-words[0][1]; s=bounce(k)*0.15+0.85 if k<0.6 else 1.0
        f=F(74*SS); d=ImageDraw.Draw(img)
        toks=[w[0].upper() for w in words]
        widths=[d.textbbox((0,0),w,font=f,stroke_width=int(9*SS))[2] for w in toks]
        gap=22*SS; total=sum(widths)+gap*(len(toks)-1)
        im=Image.new("RGBA",(int(total+80),int(170*SS)),(0,0,0,0)); dd=ImageDraw.Draw(im)
        x=40
        for (w,a,b),tok,wd in zip(words,toks,widths):
            active=a<=t<b or (t>=b and (w,a,b)==words[-1])
            said=t>=a
            col=(255,214,40) if active else ((255,255,255) if said else (255,255,255,170))
            clean=tok.strip("¿?,.:…")
            if active and clean in KEY: col=(90,230,140)
            yoff=-10*SS*max(0,1-(t-a)/0.15) if said and t-a<0.15 else 0
            dd.text((x+5*SS,40*SS+yoff+7*SS),tok,font=f,fill=(0,0,0,140),stroke_width=int(9*SS),stroke_fill=(0,0,0,140))
            dd.text((x,40*SS+yoff),tok,font=f,fill=col,stroke_width=int(9*SS),stroke_fill=(15,10,20))
            x+=wd+gap
        fit=min(1,(CW*0.92)/im.width)*s
        im=im.resize((max(1,int(im.width*fit)),max(1,int(im.height*fit))),Image.BICUBIC)
        img.paste(im,(int(CW/2-im.width/2),int(CH*0.70-im.height/2)),im)
FOOD=(400,440)
# ---------- frame
def frame(t):
    (cx,cy,z,rot),t0=camera(t)
    c=Cam(cx,cy,z)
    img=Image.new("RGB",(CW,CH)); d=ImageDraw.Draw(img)
    kitchen(d,c,t)
    # character position & state by time
    if t<2.25: x0=lerp(150,300,eio(t/2.2)); walk=1 if t<2.0 else 0; xray=False; mood="smile"; food=False; bm=None
    elif t<3.55: x0=300; walk=0; xray=True; mood="smile"; food=False; bm="search"
    elif t<6.05: x0=300; walk=0; xray=True; mood="smile"; food=False; bm="search"
    elif t<9.65: x0=300; walk=0; xray=True; mood="smile"; food=True; bm="happy"
    elif t<12.9: x0=lerp(220,320,eio((t-9.65)/3)); walk=1 if t<12.4 else 0; xray=False; mood="smile"; food=False; bm=None
    else: x0=320; walk=0; xray=False; mood="think"; food=False; bm=None
    head=character(d,c,t,x0,walk,xray,mood,food,bm)
    # fridge door opening in shot 1
    if 1.2<t<2.25:
        o=ease((t-1.2)/0.4)
        RR(d,c,(400+160*(1-o)*0+0,250,400+160*(1-o)+0.01+ (0 if o<1 else 0),860),20,fill=(250,252,255),outline=(190,200,225),width=int(c.r(4)))
        d.polygon([c.p(400,250),c.p(400+160*(1-o),250+20*o),c.p(400+160*(1-o),860-20*o),c.p(400,860)],fill=(240,244,252),outline=(190,200,225))
        if o>0.5:
            for k in range(6):
                a=t*3+k; EC(d,c,480+math.cos(a)*40,400+k*60+math.sin(a)*10,5,fill=(200,230,255))
    # dopamine particles
    if 6.3<t<9.65:
        fx,fy=c.p(*FOOD); hx,hy=c.p(head[0]+(0),head[1])
        for k in range(18):
            u=((t-6.3)*0.7+k/18)%1
            px=lerp(fx,hx,u)+math.sin(u*9+k)*c.r(25); py=lerp(fy,hy,u)-math.sin(u*math.pi)*c.r(60)
            r=c.r(7)*(1-u*0.4)
            d.ellipse((px-r,py-r,px+r,py+r),fill=(255,214,40),outline=(220,150,0),width=max(1,int(c.r(1.5))))
    # rotate & crop for camera roll
    if abs(rot)>0.05:
        img=img.rotate(rot,resample=Image.BICUBIC,expand=False,fillcolor=(214,226,246))
        zf=1+abs(math.sin(math.radians(rot)))*1.2
        w2,h2=int(CW/zf),int(CH/zf); img=img.crop(((CW-w2)//2,(CH-h2)//2,(CW-w2)//2+w2,(CH-h2)//2+h2)).resize((CW,CH),Image.BICUBIC)
    # flash on cuts
    k=t-t0
    if 0<=k<0.08 and t0>0:
        img=Image.blend(img,Image.new("RGB",(CW,CH),(255,255,255)),0.55*(1-k/0.08))
    # overlays
    sticker(img,"¿ABURRIDO?",360,190,(255,214,40),t,0.35,2.25,70,-5)
    sticker(img,"NO ES HAMBRE",360,190,(255,90,90),t,2.62,3.55,70,4)
    icon_x(img,560,420,t,2.7,3.55)
    sticker(img,"RECOMPENSA RÁPIDA",360,180,(255,214,40),t,3.9,6.05,62,-3)
    sticker(img,"DOPAMINA",360,180,(255,214,40),t,6.55,8.8,80,3)
    sticker(img,"APRENDE EL TRUCO",360,180,(90,230,140),t,8.85,9.65,64,-4)
    bulb(img,560,330,t,8.85,9.65)
    sticker(img,"LA PRÓXIMA VEZ…",360,190,(255,214,40),t,10.1,12.9,66,-3)
    sticker(img,"¿HAMBRE O ABURRIMIENTO?",360,170,(255,214,40),t,12.95,15.4,58,3)
    icon_q(img,[(120,330),(600,300),(560,520)],t,13.0)
    subtitles(img,t)
    # vignette
    return img.resize((OW,OH),Image.LANCZOS)
if __name__=="__main__":
    out=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3])
    for i in range(a,b):
        if i>=int(FPS*DUR): break
        frame(i/FPS).save(f"{out}/f{i:04d}.png")
