import numpy as np, wave
SR=44100; DUR=15.4
out=np.zeros(int(SR*DUR))
rng=np.random.default_rng(1)
def add(sig,t,g=1.0):
    i=int(t*SR); n=min(len(sig),len(out)-i); out[i:i+n]+=sig[:n]*g
def env(n,a=0.005,r=None):
    t=np.arange(n)/SR; e=np.ones(n)
    ai=int(a*SR); e[:ai]=np.linspace(0,1,ai)
    return e
def lp(x,a):  # one-pole lowpass, a in (0,1)
    y=np.zeros_like(x); s=0
    for i in range(len(x)): s+=a*(x[i]-s); y[i]=s
    return y
def whoosh(d=0.45,up=True):
    n=int(d*SR); x=rng.standard_normal(n)
    t=np.linspace(0,1,n); f=(t if up else 1-t)
    # time-varying lowpass via blocks
    y=np.zeros(n); s=0
    for i in range(n):
        a=0.02+0.35*f[i]; s+=a*(x[i]-s); y[i]=s
    e=np.sin(np.pi*t)**1.5
    return y*e*2.2
def pop(f=900,d=0.09):
    n=int(d*SR); t=np.arange(n)/SR
    fr=f*np.exp(-t*25)+f*0.4
    ph=2*np.pi*np.cumsum(fr)/SR
    return np.sin(ph)*np.exp(-t*45)*0.9
def ding(f=1318.5,d=1.0):
    n=int(d*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*f*2.01*t)+0.25*np.sin(2*np.pi*f*3.02*t))*np.exp(-t*4)*0.35
def buzz(d=0.35):
    n=int(d*SR); t=np.arange(n)/SR
    s=np.sign(np.sin(2*np.pi*110*t))+0.6*np.sign(np.sin(2*np.pi*116*t))
    return lp(s,0.25)*np.minimum(1,t*80)*np.exp(-t*3)*0.28
def thud(d=0.35):
    n=int(d*SR); t=np.arange(n)/SR
    return np.sin(2*np.pi*(55+60*np.exp(-t*30))*t)*np.exp(-t*12)*0.9 + lp(rng.standard_normal(n),0.08)*np.exp(-t*25)*0.6
def sparkle(d=1.2):
    n=int(d*SR); y=np.zeros(n)
    for k in range(14):
        st=int(rng.uniform(0,d*0.75)*SR); f=rng.uniform(2200,4200)
        m=int(0.18*SR); t=np.arange(m)/SR
        seg=np.sin(2*np.pi*f*t)*np.exp(-t*28)*0.22
        y[st:st+m]+=seg[:max(0,min(m,n-st))]
    return y
def boing(d=0.5):
    n=int(d*SR); t=np.arange(n)/SR
    fr=300+180*np.sin(2*np.pi*9*t)*np.exp(-t*4)+t*250
    return np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-t*5)*0.45
def riser(d=0.9):
    n=int(d*SR); t=np.linspace(0,1,n)
    x=rng.standard_normal(n); y=np.zeros(n); s=0
    for i in range(n):
        a=0.01+0.4*t[i]**2; s+=a*(x[i]-s); y[i]=s
    return y*t**2*1.6
def hit(d=1.2):
    n=int(d*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*(45+80*np.exp(-t*20))*t)*np.exp(-t*4)*1.0+lp(rng.standard_normal(n),0.15)*np.exp(-t*9)*0.5)
# --- music bed (100 bpm)
bpm=100; beat=60/bpm
music=np.zeros_like(out)
def madd(sig,t,g):
    i=int(t*SR); n=min(len(sig),len(music)-i)
    if n>0: music[i:i+n]+=sig[:n]*g
chords=[[261.6,329.6,392.0],[220.0,261.6,329.6],[174.6,220.0,261.6],[196.0,246.9,293.7]]
nb=int(DUR/beat)+1
for b in range(nb):
    tb=b*beat
    k=int(0.25*SR); tt=np.arange(k)/SR
    madd(np.sin(2*np.pi*(50+70*np.exp(-tt*35))*tt)*np.exp(-tt*14),tb,0.55)   # kick
    h=int(0.05*SR); madd(rng.standard_normal(h)*np.exp(-np.arange(h)/SR*90),tb+beat/2,0.08)  # hat
    ch=chords[(b//4)%4]
    for j in range(2):
        f=ch[(b*2+j)%3]*2; m=int(0.3*SR); tt=np.arange(m)/SR
        madd((np.sin(2*np.pi*f*tt)+0.3*np.sin(4*np.pi*f*tt))*np.exp(-tt*9),tb+j*beat/2,0.12)
    if b%4==0:
        m=int(beat*4*SR); tt=np.arange(m)/SR
        madd(np.sin(2*np.pi*ch[0]/2*tt)*np.minimum(1,tt*4)*np.exp(-tt*0.6),tb,0.12)  # bass pad
fade=np.ones_like(music); fe=int(0.6*SR); fade[-fe:]=np.linspace(1,0,fe)
music*=fade
# --- events
add(whoosh(0.4),0.0,0.7); add(pop(1000),0.35,0.8)
add(thud(),1.25,0.7)
add(whoosh(0.35),2.25,0.8); add(buzz(),2.65,1.0)
add(riser(0.5),3.15,0.5); add(whoosh(0.4,False),3.55,0.8); add(pop(800),3.9,0.8)
add(whoosh(0.35),6.05,0.8); add(sparkle(1.4),6.5,0.9); add(pop(1200),6.6,0.7)
add(ding(),8.9,1.0)
add(whoosh(0.4),9.65,0.8); add(pop(900),10.1,0.7)
add(riser(0.8),12.1,0.6); add(whoosh(0.3),12.85,0.8); add(boing(),13.0,0.9)
add(hit(),14.75,0.9)
mix=out+music*0.55
mix/=max(1e-9,np.abs(mix).max())*1.12
for name,sig in [("sfx.wav",mix)]:
    w=wave.open(name,"wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(sig,-1,1)*32767).astype(np.int16).tobytes()); w.close()
print("ok")
