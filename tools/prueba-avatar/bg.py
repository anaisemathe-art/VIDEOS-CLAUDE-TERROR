import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
W,H=1440,2560
FLOOR=2150
random.seed(3)
def vgrad(w,h,c0,c1):
    a=np.linspace(0,1,h)[:,None,None]; c0=np.array(c0)[None,None,:]; c1=np.array(c1)[None,None,:]
    return Image.fromarray((c0*(1-a)+c1*a).repeat(w,axis=1).astype(np.uint8))
def back_layer():
    img=vgrad(W,H,(246,222,200),(233,190,165)).convert("RGBA"); d=ImageDraw.Draw(img)
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    for x in range(0,W,90): od.rectangle((x,0,x+44,FLOOR),fill=(255,255,255,22))
    img=Image.alpha_composite(img,ov); d=ImageDraw.Draw(img)
    # wainscot
    d.rectangle((0,1650,W,FLOOR),fill=(214,160,135)); d.rectangle((0,1630,W,1660),fill=(250,236,222))
    for x in range(30,W,240): d.rounded_rectangle((x,1700,x+190,FLOOR-40),12,outline=(196,140,115),width=6)
    # window
    wx0,wy0,wx1,wy1=820,330,1340,1150
    sky=vgrad(wx1-wx0,wy1-wy0,(255,170,110),(150,110,190)); img.paste(sky,(wx0,wy0))
    d.ellipse((1150,780,1290,920),fill=(255,226,150))
    for i in range(14):
        bx=wx0+i*40+random.randint(-10,10); bh=random.randint(120,330); bw=random.randint(40,80)
        d.rectangle((bx,wy1-bh,bx+bw,wy1),fill=(95,70,130))
        for k in range(6):
            if random.random()<0.6: d.rectangle((bx+10,wy1-bh+20+k*45,bx+20,wy1-bh+32+k*45),fill=(255,214,140))
    d.rectangle((wx0,wy0,wx1,wy1),outline=(255,248,240),width=26); d.line((wx0+(wx1-wx0)//2,wy0,wx0+(wx1-wx0)//2,wy1),fill=(255,248,240),width=18)
    d.line((wx0,wy0+(wy1-wy0)//2,wx1,wy0+(wy1-wy0)//2),fill=(255,248,240),width=18)
    d.rectangle((wx0-40,wy1,wx1+40,wy1+40),fill=(255,248,240))
    # curtains
    for cx in (wx0-130,wx1-10):
        d.rounded_rectangle((cx,260,cx+150,1500),40,fill=(120,160,140))
        for k in range(4): d.line((cx+25+k*35,280,cx+25+k*35,1480),fill=(100,140,120),width=8)
    d.rectangle((wx0-180,240,wx1+180,270),fill=(140,100,80))
    # shelf left
    for sy in (650,950):
        d.rectangle((60,sy,620,sy+26),fill=(160,110,80))
        x=80
        while x<560:
            bw=random.randint(28,55); bh=random.randint(150,230)
            col=random.choice([(230,90,90),(80,140,200),(250,200,80),(120,180,120),(170,110,190),(240,150,90)])
            if random.random()<0.15:
                d.polygon([(x,sy),(x+bw,sy),(x+bw+60,sy-bh+20),(x+60-bw*0.2,sy-bh)],fill=col); x+=bw+70; continue
            d.rounded_rectangle((x,sy-bh,x+bw,sy),6,fill=col); d.rectangle((x+6,sy-bh+30,x+bw-6,sy-bh+40),fill=tuple(min(255,c+60) for c in col)); x+=bw+6
    # frames
    d.rounded_rectangle((120,250,380,520),10,fill=(255,250,240),outline=(150,100,70),width=14)
    d.polygon([(150,490),(250,330),(350,490)],fill=(120,170,150)); d.ellipse((290,300,340,350),fill=(250,200,90))
    d.rounded_rectangle((430,320,600,520),10,fill=(250,230,210),outline=(150,100,70),width=12)
    d.ellipse((480,370,550,440),fill=(230,120,120))
    # sofa (behind, right)
    d.rounded_rectangle((760,1480,1500,1820),70,fill=(70,140,150)); d.rounded_rectangle((720,1640,1500,2000),60,fill=(60,125,135))
    for k in range(3): d.rounded_rectangle((800+k*230,1540,1010+k*230,1700),40,fill=(85,155,165))
    d.rounded_rectangle((900,1520,1060,1660),40,fill=(250,200,90)); d.rounded_rectangle((1150,1530,1300,1660),40,fill=(240,130,120))
    # floor lamp left
    d.line((260,1200,260,2100),fill=(70,60,60),width=18); d.ellipse((170,2080,350,2130),fill=(70,60,60))
    d.polygon([(150,1200),(370,1200),(320,1000),(200,1000)],fill=(255,228,170))
    # floor
    fl=vgrad(W,H-FLOOR,(190,130,95),(150,95,70)); img.paste(fl,(0,FLOOR)); d=ImageDraw.Draw(img)
    for k in range(-12,24): d.line((W/2+k*130,FLOOR,W/2+k*330,H),fill=(170,112,80),width=5)
    d.rectangle((0,FLOOR-6,W,FLOOR+8),fill=(120,80,60))
    d.ellipse((160,2230,1280,2520),fill=(230,200,170)); d.ellipse((230,2260,1210,2490),outline=(210,170,140),width=10)
    # warm light glows
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); g=ImageDraw.Draw(glow)
    for r,a in [(520,40),(360,55),(200,70)]: g.ellipse((260-r,1100-r,260+r,1100+r),fill=(255,200,120,a))
    for r,a in [(700,30),(450,40)]: g.ellipse((1080-r,740-r,1080+r,740+r),fill=(255,170,110,a))
    glow=glow.filter(ImageFilter.GaussianBlur(80)); img=Image.alpha_composite(img,glow)
    return img.convert("RGB")
def fore_layer():
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    # big plant bottom-right foreground
    d.rounded_rectangle((1080,2180,1400,2560),40,fill=(200,110,80))
    for k in range(11):
        a=-2.6+k*0.22; L=random.randint(380,560)
        x0,y0=1240,2200; x1,y1=x0+math.cos(a)*L*0.7,y0+math.sin(a)*L
        d.line((x0,y0,x1,y1),fill=(60,120,70,255),width=12)
        col=random.choice([(70,150,85,255),(90,170,95,255),(60,135,75,255)])
        ca,sa=math.cos(a),math.sin(a); Lf=150
        pts=[(x1+ca*Lf*math.cos(u)-(-sa)*0,y1) for u in []]
        leaf=[(x1+ca*Lf*v - sa*55*math.sin(math.pi*v), y1+sa*Lf*v + ca*55*math.sin(math.pi*v)) for v in [i/12 for i in range(13)]]
        leaf+=[(x1+ca*Lf*v + sa*55*math.sin(math.pi*v), y1+sa*Lf*v - ca*55*math.sin(math.pi*v)) for v in [1-i/12 for i in range(13)]]
        d.polygon(leaf,fill=col)
        d.line((x1,y1,x1+ca*Lf,y1+sa*Lf),fill=(50,110,60,255),width=5)
    return img
if __name__=="__main__":
    b=back_layer(); b.save("bg_back.png"); fore_layer().save("bg_fore.png")
    b.filter(ImageFilter.GaussianBlur(10)).save("bg_back_blur.png")
    prev=b.copy(); prev.paste(fore_layer(),(0,0),fore_layer()); prev.resize((360,640)).save("bgchk.jpg")
