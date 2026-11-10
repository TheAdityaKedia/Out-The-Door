import FreeCAD as App, FreeCADGui as Gui, Part
V=App.Vector; S='build/'
WH=(0.95,0.95,0.94); OR=(1.0,0.36,0.05); DK=(0.25,0.25,0.28)
def ldF(n): q=Part.Shape(); q.importBrep(S+'ccF_'+n+'.brep'); return q
Gui.showMainWindow()
clip=Part.makeBox(40,11,70,V(12,12,-35))
bb=clip.BoundBox; bb2=Part.makeBox(40,70,70,V(12,-10,-35)).BoundBox
pan=Part.makeCompound([s for s in ldF('panel').Solids if s.BoundBox.intersect(bb2)])
print('body cut'); body=ldF('body').common(clip); print('ok')
doc=App.newDocument('sec')
for n,sh,c in [('body',body,WH),('knob',ldF('knob'),OR),('pin',ldF('pin'),OR),('panel',pan,DK)]:
    o=doc.addObject('Part::Feature',n); o.Shape=sh; o.ViewObject.ShapeColor=c
doc.recompute(); Gui.updateGui(); v=Gui.ActiveDocument.ActiveView
v.viewRear(); v.setCameraType('Orthographic'); v.fitAll(); Gui.updateGui()
v.saveImage(S+'asm_sec.png',1400,1200,'White'); print('SEC OK')
v.viewTop(); v.fitAll(); Gui.updateGui(); v.saveImage(S+'asm_sectop.png',1400,1200,'White'); print('TOP OK')
