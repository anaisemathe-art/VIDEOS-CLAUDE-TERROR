import sys,glob,os,numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
def cut(f,tol=20):
    im=Image.open(f).convert("RGB"); a=np.asarray(im).astype(int)
    # per-border-pixel tolerance vs local bg: use smoothed background estimate (gradient bgs)
    small=im.resize((im.width//8,im.height//8)); 
    near=np.zeros(a.shape[:2],bool)
    bgc=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]])
    med=np.median(bgc,axis=0)
    lum=a.mean(axis=2); sat=a.max(axis=2)-a.min(axis=2)
    near=(sat<14)&(lum>max(150,med.mean()-45))   # light, desaturated = background
    lab,_=ndimage.label(near)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    fg=~np.isin(lab,list(border)); fg=ndimage.binary_opening(fg,iterations=2)
    l2,n2=ndimage.label(fg)
    if n2>1:
        sz=ndimage.sum(fg,l2,range(1,n2+1)); fg=np.isin(l2,[i+1 for i,s in enumerate(sz) if s>sz.max()*0.01])
    al=Image.fromarray((fg*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
    o=im.filter(ImageFilter.UnsharpMask(1.2,40,2)).convert("RGBA"); o.putalpha(al); return o
if __name__=="__main__":
    jobs=sorted(glob.glob("src/*/*.png")); k,n=int(sys.argv[1]),int(sys.argv[2])
    for f in jobs[k::n]:
        out=f.replace("src/","").replace(".png",".webp")
        if not os.path.exists(out): cut(f).save(out,"WEBP",quality=92,method=4)
