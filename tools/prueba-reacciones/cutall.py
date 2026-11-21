import sys,glob,numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
files=sorted(glob.glob("raw/r*.png")); a0,a1=int(sys.argv[1]),int(sys.argv[2])
for f in files[a0:a1]:
    im=Image.open(f).convert("RGB"); a=np.asarray(im).astype(int)
    bg=np.median(np.concatenate([a[0],a[-1],a[:,0],a[:,-1]]),axis=0)
    near=np.abs(a-bg).max(axis=2)<20
    lab,n=ndimage.label(near)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    fg=~np.isin(lab,list(border)); fg=ndimage.binary_opening(fg,iterations=1)
    l2,n2=ndimage.label(fg)
    if n2>1:
        sz=ndimage.sum(fg,l2,range(1,n2+1)); fg=np.isin(l2,[i+1 for i,s in enumerate(sz) if s>sz.max()*0.01])
    al=Image.fromarray((fg*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    o=im.convert("RGBA"); o.putalpha(al); o.save(f.replace("raw/r","cut/c"))
