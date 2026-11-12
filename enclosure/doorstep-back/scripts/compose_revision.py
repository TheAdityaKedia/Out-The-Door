import sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.image as mi, numpy as np
def crop(f,pad=15):
    im=mi.imread(f); m=(im[:,:,:3]<0.97).any(axis=2); ys,xs=np.where(m)
    return im[max(ys.min()-pad,0):ys.max()+pad, max(xs.min()-pad,0):xs.max()+pad]
rev,prev,title,out=sys.argv[1:5]
rows=[(prev,'before: '+prev)] if prev!='-' else []
rows.append((rev,('after: ' if rows else '')+rev))
f,ax=plt.subplots(len(rows),2,figsize=(10,4.2*len(rows)),dpi=110,squeeze=False)
for i,(r,lab) in enumerate(rows):
    for j,v in enumerate(('top','under')):
        ax[i][j].imshow(crop('r_%s_%s.png'%(r,v))); ax[i][j].axis('off')
    ax[i][0].set_title(lab,fontsize=14,loc='left',fontweight='bold')
f.suptitle(title,fontsize=15); plt.tight_layout(); plt.savefig(out,facecolor='white'); print('ok',out)
