import FreeCAD as App, FreeCADGui as Gui, Part, os
V=App.Vector; S='build/'
M=App.Placement(V(),App.Rotation(V(1,0,0),-6.0)).toMatrix()
def ld(n): s=Part.Shape(); s.importBrep(S+'cc_'+n+'.brep'); return s
WH=(0.95,0.95,0.94); OR=(1.0,0.36,0.05); DK=(0.25,0.25,0.28); BL=(0.3,0.45,0.75)
fwd=M.multVec(V(0,-1,0)); right=V(1,0,0)
P={n:ld(n) for n in ['body','bevel','knob','pin','panel','bat']}
COL={'body':WH,'bevel':WH,'knob':OR,'pin':OR,'panel':DK,'bat':BL}
Gui.showMainWindow()
App.ParamGet("User parameter:BaseApp/Preferences/View").SetBool("UseNavigationAnimations",False)
def cam(v,yaw,pitch):
    r=App.Rotation(V(0,0,1),yaw).multiply(App.Rotation(V(1,0,0),90-pitch)); v.setCameraOrientation(r.Q,False)
def shot(name,items,yaw=35,pitch=22):
    doc=App.newDocument(name)
    for n,off in items:
        o=doc.addObject('Part::Feature',n); o.Shape=P[n]; o.Placement.Base=off
        o.ViewObject.ShapeColor=COL[n]; o.ViewObject.LineWidth=0.5
    doc.recompute(); Gui.updateGui(); v=Gui.ActiveDocument.ActiveView
    cam(v,yaw,pitch); v.setCameraType('Perspective'); v.fitAll(); Gui.updateGui()
    v.saveImage(S+'asm_'+name+'.png',1200,900,'White'); App.closeDocument(name)
z=V()
for n in P: shot('part_'+n,[(n,z)], *( (35,22) if n not in ('pin',) else (35,40) ))
shot('s1',[('body',z),('knob',fwd*30-right*12)])
shot('s2',[('body',z),('knob',z),('pin',fwd*28)])
shot('s3',[('body',z),('knob',z),('pin',z),('bat',fwd*45)])
shot('s4',[('body',z),('knob',z),('pin',z),('bat',z),('panel',fwd*30)])
shot('s5',[('body',z),('knob',z),('pin',z),('bat',z),('panel',z),('bevel',fwd*22)])
shot('s6',[('body',z),('knob',z),('pin',z),('bat',z),('panel',z),('bevel',z)])
# how-it-works section (F frame, seen from the front, front half of body removed)
def ldF(n): q=Part.Shape(); q.importBrep(S+'ccF_'+n+'.brep'); return q
clip=Part.makeBox(40,60,70,V(12,17.5,-35))
clipf=Part.makeBox(40,60,70,V(12,-10,-35))
doc=App.newDocument('sec')
for n,sh,c in [('body',ldF('body').common(clip),WH),('knob',ldF('knob'),OR),('pin',ldF('pin'),OR),('panel',ldF('panel').common(clipf),DK)]:
    o=doc.addObject('Part::Feature',n); o.Shape=sh; o.ViewObject.ShapeColor=c
doc.recompute(); Gui.updateGui(); v=Gui.ActiveDocument.ActiveView
v.viewFront(); v.setCameraType('Orthographic'); v.fitAll(); Gui.updateGui()
v.saveImage(S+'asm_sec.png',1400,1200,'White'); App.closeDocument('sec')
print('RENDER OK')
