import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
def cut(src,dst,tol=26):
    im=Image.open(src).convert("RGB"); a=np.asarray(im).astype(int)
    h,w,_=a.shape
    bg=np.median(np.concatenate([a[0],a[-1],a[:,0],a[:,-1]]),axis=0)
    near=(np.abs(a-bg).max(axis=2)<tol)
    lab,n=ndimage.label(near)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bgmask=np.isin(lab,list(border))
    fg=~bgmask
    fg=ndimage.binary_opening(fg,iterations=1)
    # keep largest component
    l2,n2=ndimage.label(fg)
    if n2>1:
        sizes=ndimage.sum(fg,l2,range(1,n2+1)); keep=np.argmax(sizes)+1
        big=sizes.max(); ids=[i+1 for i,s in enumerate(sizes) if s>big*0.01]
        fg=np.isin(l2,ids)
    fg=ndimage.binary_fill_holes(fg) if False else fg
    alpha=Image.fromarray((fg*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    out=im.convert("RGBA"); out.putalpha(alpha)
    bb=out.getbbox(); out=out.crop(bb)
    out.save(dst)
if __name__=="__main__":
    for s,d in zip(sys.argv[1::2],sys.argv[2::2]): cut(s,d)
