import FreeCAD as App, FreeCADGui as Gui, Part
V=App.Vector; S='build/'
def ldF(n): q=Part.Shape(); q.importBrep(S+'ccF_'+n+'.brep'); return q
Gui.showMainWindow()
for name,sh,box,rot in [('lock_body',ldF('body'),Part.makeBox(90,60,60,V(-45,3.0,-30)),App.Rotation(V(1,0,0),90)),('lock_plate',ldF('bevel'),None,App.Rotation(V(1,0,0),-90))]:
    doc=App.newDocument(name); o=doc.addObject('Part::Feature','p'); o.Shape=sh.common(box) if box else sh; o.ViewObject.ShapeColor=(0.95,0.95,0.94)
    doc.recompute(); v=Gui.ActiveDocument.ActiveView; v.setCameraOrientation(rot.Q); v.setCameraType('Orthographic'); v.fitAll(); Gui.updateGui()
    v.saveImage(S+name+'.png',1600,1000,'White'); print('OK',name)
