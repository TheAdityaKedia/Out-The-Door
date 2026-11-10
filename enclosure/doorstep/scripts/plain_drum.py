exec(open('scripts/orient.py').read().split('parts=')[0])
k=ld('ccF_knob'); p=ld('ccF_pin'); c=p.BoundBox.Center
hub=Part.makeCylinder(4.0,1.4,V(c.x,5.7,c.z),V(0,1,0))
bore=Part.makeCylinder(1.8,12,V(c.x,4,c.z),V(0,1,0))
k=k.fuse(hub).removeSplitter().cut(bore)
print('valid',k.isValid(),'vol',round(k.Volume,1))
d=down_y(k); m=Mesh.Mesh(); m.addFacets(d.tessellate(0.03)); m.write(OUT+'latch_drum_orange_plain.stl'); print('ok', d.BoundBox)
