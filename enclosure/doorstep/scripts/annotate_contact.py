import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.image as mi
im=mi.imread('build/contact_top.png')[230:960,240:1160]
f,a=plt.subplots(figsize=(9.2,8),dpi=120); a.imshow(im); a.axis('off')
a.set_title('Slice through the drum, seen from above (front of case at bottom)',fontsize=13,pad=14)
kw=dict(fontsize=12,arrowprops=dict(arrowstyle='->',lw=1.6,color='k'))
a.annotate('Small hub on the drum\nsits 1.85 mm into the\nCrowPanel wheel (overlap)',xy=(590,560),xytext=(10,130),**kw)
a.annotate('Drum (rim sticks out\nthe side window)',xy=(860,450),xytext=(700,90),**kw)
a.annotate('Pin, head at the front',xy=(690,585),xytext=(600,690),**kw)
a.annotate('Post on the springy arm',xy=(700,300),xytext=(380,160),**kw)
a.annotate('CrowPanel board',xy=(150,600),xytext=(20,690),**kw)
plt.tight_layout(); plt.savefig('docs/drum_contact_slice.png',facecolor='white'); print('ok')
