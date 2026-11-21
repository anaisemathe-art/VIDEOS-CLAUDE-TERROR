import numpy as np, wave, json, re
exec(open("../v15/sfx.py").read().split("# --- events")[0].replace("DUR=15.4","DUR=49.8"))
import render as R
def alarm(d=1.5):
    n=int(d*SR); t=np.arange(n)/SR
    gate=(np.sin(2*np.pi*12*t)>0).astype(float)
    return (np.sin(2*np.pi*2100*t)+0.6*np.sin(2*np.pi*2630*t))*gate*0.22*np.minimum(1,(d-t)*8)
def tick(t0,n,per=0.5):
    for k in range(n):
        m=int(0.03*SR); tt=np.arange(m)/SR
        add(np.sin(2*np.pi*(3000 if k%2 else 2200)*tt)*np.exp(-tt*200)*0.5,t0+k*per,0.6)
add(alarm(1.5),0.0,1.0)
for i,(t0,f,r) in enumerate(R.PLAN[1:]): add(whoosh(0.35),t0-0.12,0.7)
for k,(ch,pos,size,t0,t1,wob) in enumerate(R.EMO): add(pop(800+(k%5)*150),t0,0.55)
for txt,col,t0,t1,r in R.STICK: add(hit(0.6),t0,0.45); add(pop(600),t0,0.7)
for t0,t1,nm,a,b,m in R.TL:
    if nm=="sorpresa" and a==48: add(boing(),t0+0.05,0.7)
add(ding(),29.45,0.8)
tick(R.W(22),5,0.45)
add(sparkle(1.2),R.W(40),0.6)
add(buzz(),R.W(102),0.7)
add(riser(0.8),R.W(121)-0.8,0.5)
add(hit(),45.9,0.6)
mix=out+music*0.45
mix/=max(1e-9,np.abs(mix).max())*1.12
w=wave.open("sfx.wav","wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(mix,-1,1)*32767).astype(np.int16).tobytes()); w.close(); print("ok")
