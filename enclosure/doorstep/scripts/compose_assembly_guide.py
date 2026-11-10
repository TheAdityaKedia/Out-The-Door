import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.image as mi, numpy as np
def crop(f,pad=20):
    im=mi.imread(f); m=(im[:,:,:3]<0.97).any(axis=2); ys,xs=np.where(m)
    return im[max(ys.min()-pad,0):ys.max()+pad, max(xs.min()-pad,0):xs.max()+pad]
parts=[('body','Body (white)'),('bevel','Slope front (white)'),('knob','Latch drum (orange)'),('pin','Latch pin (orange)\nprint standing on its head'),('panel','CrowPanel'),('bat','LiPo battery')]
steps=[('s1','1  Drop the drum in on the left,\nslide it right until its rim\npokes out of the side slot'),('s2','2  Push the pin in from the front,\nthrough the drum into the post,\nuntil its head meets the drum'),('s3','3  Plug in the battery and lay\nit in the back of the case'),('s4','4  Push the drum out to the side,\npress the CrowPanel in until\nthe corner hooks click, let go'),('s5','5  Press the Slope front\ninto the pocket'),('sec','How it works (seen from behind):\nthe post hangs on a thin arm that\nbends, so the drum is always\npressed onto the wheel. Press the\ndrum to click the wheel button.')]
f=plt.figure(figsize=(15,15.5),dpi=100)
f.text(0.02,0.975,'Doorstep Slope: parts',fontsize=22,fontweight='bold')
for i,(n,t) in enumerate(parts):
    a=f.add_axes([0.01+(i%3)*0.33,0.835-(i//3)*0.16,0.31,0.11]); a.imshow(crop('build/asm_part_'+n+'.png')); a.axis('off'); a.set_title(t,fontsize=13)
f.text(0.02,0.63,'Assembly',fontsize=22,fontweight='bold')
for i,(n,t) in enumerate(steps):
    a=f.add_axes([0.01+(i%3)*0.33,0.315-(i//3)*0.305,0.31,0.26]); a.imshow(crop('build/asm_'+n+'.png')); a.axis('off'); a.set_title(t,fontsize=13,loc='left')
plt.savefig('docs/assembly_guide.png',facecolor='white'); print('ok')
