import FreeCAD as App, FreeCADGui as Gui, Part
V=App.Vector; S='build/'
def ldF(n): q=Part.Shape(); q.importBrep(S+'ccF_'+n+'.brep'); return q
kn=ldF('knob'); pin=ldF('pin'); az=pin.BoundBox.Center.z
print('axle z',round(az,2),'knob bbox',kn.BoundBox)
reg=Part.makeBox(30,30,40,V(15,-2,az-20))
pan=[s for s in ldF('panel').Solids if s.BoundBox.intersect(reg.BoundBox)]
hits=[(round(s.common(kn).Volume,2),s.BoundBox) for s in pan]
for h in hits:
    if h[0]>0: print('overlap',h)
half=Part.makeBox(60,60,40,V(5,-5,az-40))   # keep below axle -> cut at axle plane
Gui.showMainWindow()
doc=App.newDocument('c')
WH=(0.95,0.95,0.94); OR=(1.0,0.36,0.05); DK=(0.25,0.25,0.28)
for n,sh,c in [('body',ldF('body').common(Part.makeBox(30,40,40,V(15,-5,az-40))),WH),('knob',kn.common(half),OR),('pin',pin.common(half),OR),('panel',Part.makeCompound([s.common(half) for s in pan]),DK)]:
    o=doc.addObject('Part::Feature',n); o.Shape=sh; o.ViewObject.ShapeColor=c
doc.recompute(); v=Gui.ActiveDocument.ActiveView
v.viewTop(); v.setCameraType('Orthographic'); v.fitAll(); Gui.updateGui()
v.saveImage(S+'contact_top.png',1400,1200,'White'); print('IMG OK')
