import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
W,H=1440,2560; FLOOR=2150
random.seed(7)
def vgrad(w,h,c0,c1):
    a=np.linspace(0,1,h)[:,None,None]
    return Image.fromarray((np.array(c0)*(1-a)+np.array(c1)*a).repeat(w,axis=1).astype(np.uint8))
def back():
    img=vgrad(W,H,(150,130,200),(120,100,170)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    for y in range(0,FLOOR,70):
        for x in range((y//70)%2*35,W,70): od.ellipse((x,y,x+8,y+8),fill=(255,255,255,18))
    img=Image.alpha_composite(img,ov); d=ImageDraw.Draw(img)
    # window night
    wx0,wy0,wx1,wy1=120,330,640,1080
    img.paste(vgrad(wx1-wx0,wy1-wy0,(30,40,90),(70,60,130)),(wx0,wy0)); d=ImageDraw.Draw(img)
    for _ in range(40):
        x=random.randint(wx0+20,wx1-20); y=random.randint(wy0+20,wy1-200); r=random.choice([2,3,4])
        d.ellipse((x-r,y-r,x+r,y+r),fill=(255,250,220))
    d.ellipse((440,400,580,540),fill=(255,240,190)); d.ellipse((480,385,610,515),fill=(40,48,100))
    for i in range(10):
        bx=wx0+i*55; bh=random.randint(100,260)
        d.rectangle((bx,wy1-bh,bx+50,wy1),fill=(25,25,60))
        for k in range(5):
            if random.random()<0.5: d.rectangle((bx+15,wy1-bh+20+k*40,bx+25,wy1-bh+30+k*40),fill=(255,214,120))
    d.rectangle((wx0,wy0,wx1,wy1),outline=(240,235,250),width=24); d.line(((wx0+wx1)//2,wy0,(wx0+wx1)//2,wy1),fill=(240,235,250),width=16)
    d.rectangle((wx0-40,wy1,wx1+40,wy1+36),fill=(240,235,250))
    for cx in (wx0-120,wx1-20):
        d.rounded_rectangle((cx,260,cx+140,1400),40,fill=(240,170,150))
        for k in range(4): d.line((cx+22+k*32,280,cx+22+k*32,1380),fill=(220,150,130),width=7)
    d.rectangle((wx0-170,240,wx1+170,268),fill=(110,80,70))
    # string lights
    pts=[(x, 200+40*math.sin(x/180)) for x in range(700,1440,8)]
    d.line(pts,fill=(60,50,70),width=4)
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); g=ImageDraw.Draw(glow)
    for i,(x,y) in enumerate(pts[::12]):
        c=[(255,210,120),(255,150,170),(150,220,255)][i%3]
        d.ellipse((x-12,y+6,x+12,y+34),fill=c); g.ellipse((x-60,y-40,x+60,y+80),fill=c+(90,))
    # posters
    d.rounded_rectangle((820,420,1060,760),12,fill=(255,214,90),outline=(250,250,250),width=10)
    d.ellipse((880,480,1000,600),fill=(240,120,100)); d.rectangle((870,640,1010,700),fill=(90,80,160))
    d.rounded_rectangle((1110,480,1330,780),12,fill=(110,200,190),outline=(250,250,250),width=10)
    d.polygon([(1140,740),(1220,560),(1300,740)],fill=(255,250,240))
    # bed (right)
    d.rounded_rectangle((760,1180,1500,1700),50,fill=(120,85,70))          # headboard
    d.rounded_rectangle((720,1560,1520,2120),40,fill=(250,245,250))        # mattress
    d.rounded_rectangle((800,1460,1080,1640),60,fill=(255,255,255),outline=(225,220,235),width=6)
    d.rounded_rectangle((1110,1470,1390,1650),60,fill=(255,255,255),outline=(225,220,235),width=6)
    d.rounded_rectangle((700,1680,1540,2140),50,fill=(90,150,220))         # blanket
    for k in range(6): d.line((760+k*130,1700,720+k*130,2120),fill=(80,135,205),width=10)
    d.rectangle((700,2120,1540,2170),fill=(100,70,60))
    # nightstand + lamp left
    d.rounded_rectangle((90,1720,470,2160),24,fill=(170,120,95)); d.line((110,1930,450,1930),fill=(140,95,75),width=8)
    d.ellipse((260,1880,300,1920),fill=(240,210,150)); d.ellipse((260,2030,300,2070),fill=(240,210,150))
    d.rectangle((265,1560,295,1720),fill=(90,80,90)); d.polygon([(170,1560),(390,1560),(340,1380),(220,1380)],fill=(255,226,160))
    d.rounded_rectangle((350,1660,420,1720),10,fill=(240,110,110))   # alarm clock
    for r,a in [(560,60),(380,80),(220,110)]: g.ellipse((280-r,1480-r,280+r,1480+r),fill=(255,190,110,a))
    for r,a in [(420,40)]: g.ellipse((380-r,700-r,380+r,700+r),fill=(140,160,255,a))
    # floor
    img.paste(vgrad(W,H-FLOOR,(150,105,90),(110,75,65)),(0,FLOOR)); d=ImageDraw.Draw(img)
    for k in range(-12,24): d.line((W/2+k*130,FLOOR,W/2+k*330,H),fill=(130,90,75),width=5)
    d.rectangle((0,FLOOR-6,W,FLOOR+8),fill=(90,60,55))
    d.ellipse((140,2230,1300,2530),fill=(200,170,220)); d.ellipse((220,2265,1220,2495),outline=(180,150,205),width=10)
    glow=glow.filter(ImageFilter.GaussianBlur(70)); img=Image.alpha_composite(img,glow)
    # dark vignette for night mood
    v=Image.new("L",(W,H),0); vd=ImageDraw.Draw(v); vd.ellipse((-500,-300,W+500,H+300),fill=255)
    v=v.filter(ImageFilter.GaussianBlur(250)); dark=Image.new("RGBA",(W,H),(20,10,40,255))
    img=Image.composite(img,Image.alpha_composite(img,Image.new("RGBA",(W,H),(20,10,40,120))),v)
    return img.convert("RGB")
def fore():
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    # stack of books + mug bottom-left foreground
    d.rounded_rectangle((-40,2330,420,2420),14,fill=(230,90,90,255)); d.rounded_rectangle((0,2250,380,2335),14,fill=(80,140,200,255))
    d.rounded_rectangle((-20,2420,440,2560),14,fill=(250,200,80,255))
    d.rounded_rectangle((120,2120,260,2250),20,fill=(250,250,250,255)); d.ellipse((240,2150,310,2220),outline=(250,250,250,255),width=16)
    return img
if __name__=="__main__":
    b=back(); b.save("bg_back.png"); b.filter(ImageFilter.GaussianBlur(10)).save("bg_back_blur.png")
    f=fore(); f.save("bg_fore.png"); p=b.copy(); p.paste(f,(0,0),f); p.resize((360,640)).save("bgchk.jpg")
