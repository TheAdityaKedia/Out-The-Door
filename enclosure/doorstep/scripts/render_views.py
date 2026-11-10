import FreeCAD as App, FreeCADGui as Gui, Part
V=App.Vector; S='build/'
WH=(0.95,0.95,0.94); OR=(1.0,0.36,0.05); DK=(0.25,0.25,0.28)
def ldF(n): q=Part.Shape(); q.importBrep(S+'ccF_'+n+'.brep'); return q
Gui.showMainWindow()
body=ldF('body'); knob=ldF('knob'); pin=ldF('pin'); bev=ldF('bevel')
pan=ldF('panel'); reg=Part.makeBox(30,30,30,V(20,0,0)).BoundBox
panN=Part.makeCompound([s for s in pan.Solids if s.BoundBox.intersect(reg)])
def shot(name,items,view,ortho=True,cam=None):
    doc=App.newDocument(name)
    for n,sh,c in items:
        o=doc.addObject('Part::Feature',n); o.Shape=sh; o.ViewObject.ShapeColor=c
    doc.recompute(); v=Gui.ActiveDocument.ActiveView
    getattr(v,view)(); v.setCameraType('Orthographic' if ortho else 'Perspective')
    if cam: v.setCameraOrientation(cam)
    v.fitAll(); Gui.updateGui(); v.saveImage(S+'new_'+name+'.png',1400,1100,'White'); print('OK',name)
# A: wheel side from outside
shot('side',[('body',body,WH),('knob',knob,OR)],'viewRight')
# B: slice through the top button, seen from above (front at bottom)
zc=11.15
cut=Part.makeBox(25,40,30,V(22,-2,zc-30))
shot('button',[('body',body.common(cut),WH),('panel',panN.common(cut),DK)],'viewTop')
# C: body mouth from the front, seat + tongue
shot('mouth',[('body',body,WH),('knob',knob,OR),('pin',pin,OR)],'viewIsometric',False,App.Rotation(V(1,0,0),70).Q)
# D: plate back
shot('plateback',[('bev',bev,WH)],'viewRear')
shot('under',[('body',body,WH)],'viewBottom')
