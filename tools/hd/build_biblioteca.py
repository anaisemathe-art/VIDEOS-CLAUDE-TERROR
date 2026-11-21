import sys,glob,os,numpy as np,cv2
cv2.setNumThreads(1)
from PIL import Image, ImageFilter
from scipy import ndimage
sr=cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel("../sr/FSRCNN_x2.pb"); sr.setModel("fsrcnn",2)
need={"giro":(0,77),"senalar":(30,115),"sorpresa":(48,91),"pensar":(30,101),"reir":(48,113)}
allj=sorted(glob.glob("src/*/*.png"))
def pri(f):
    nm=f.split("/")[1]; i=int(f[-7:-4])-1; a,b=need.get(nm,(0,0))
    return (0 if a<=i<b else 1, f)
jobs=sorted(allj,key=pri); k,n=int(sys.argv[1]),int(sys.argv[2])
for f in jobs[k::n]:
    out=f.replace("src/","").replace(".png",".webp")
    if os.path.exists(out): continue
    im=Image.open(f).convert("RGB"); a=np.asarray(im).astype(int)
    bg=np.median(np.concatenate([a[0],a[-1],a[:,0],a[:,-1]]),axis=0)
    near=np.abs(a-bg).max(axis=2)<20
    lab,_=ndimage.label(near)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    fg=~np.isin(lab,list(border)); fg=ndimage.binary_opening(fg,iterations=1)
    l2,n2=ndimage.label(fg)
    if n2>1:
        sz=ndimage.sum(fg,l2,range(1,n2+1)); fg=np.isin(l2,[i+1 for i,s in enumerate(sz) if s>sz.max()*0.01])
    al=Image.fromarray((fg*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3))
    al=al.resize((im.width*2,im.height*2),Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.0))
    up=sr.upsample(cv2.imread(f)); up=Image.fromarray(cv2.cvtColor(up,cv2.COLOR_BGR2RGB)).filter(ImageFilter.UnsharpMask(1.5,70,2))
    o=up.convert("RGBA"); o.putalpha(al); o.save(out,"WEBP",quality=92,method=4)
