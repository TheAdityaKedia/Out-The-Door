import FreeCAD as App, FreeCADGui as Gui, Part
V=App.Vector; S='build/'
WH=(0.95,0.95,0.94); OR=(1.0,0.36,0.05)
def ldF(n): q=Part.Shape(); q.importBrep(S+'ccF_'+n+'.brep'); return q
Gui.showMainWindow()
body=ldF('body').common(Part.makeBox(30,60,60,V(14,-5,-30)))
pin=ldF('pin')
for name,items in [('post_nodrum',[('body',body,WH)]),('post_pin',[('body',body,WH),('pin',pin,OR)])]:
    doc=App.newDocument(name)
    for n,sh,c in items:
        o=doc.addObject('Part::Feature',n); o.Shape=sh; o.ViewObject.ShapeColor=c
    doc.recompute(); v=Gui.ActiveDocument.ActiveView
    v.setCameraOrientation(App.Rotation(V(0,0,1),-25).multiply(App.Rotation(V(1,0,0),70)).Q)
    v.setCameraType('Perspective'); v.fitAll(); Gui.updateGui(); v.saveImage(S+name+'.png',1400,1200,'White'); print('OK',name)
