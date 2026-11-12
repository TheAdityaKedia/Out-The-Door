# Preview images of the assembled Doorstep-back -> build/v_*.png (run under xvfb from the case folder)
import FreeCAD as App, FreeCADGui as Gui, Part, os
V=App.Vector; S='build/'
WH=(0.95,0.95,0.94); OR=(1.0,0.36,0.05); DK=(0.22,0.22,0.24); GN=(0.2,0.5,0.3); BL=(0.3,0.45,0.75)
def ld(n): q=Part.Shape(); q.importBrep(S+'cc_'+n+'.brep'); return q
Gui.showMainWindow()
App.ParamGet("User parameter:BaseApp/Preferences/View").SetBool("UseNavigationAnimations",False)
body,cap,knob,pin,pan,bat=[ld(n) for n in ('body','plate','knob','pin','panel','bat')]
def moved(s,d): s=s.copy(); s.translate(d); return s
def shot(name,items,rot,ortho=False):
    doc=App.newDocument(name)
    for n,sh,c in items:
        o=doc.addObject('Part::Feature',n); o.Shape=sh; o.ViewObject.ShapeColor=c
    doc.recompute(); v=Gui.ActiveDocument.ActiveView
    v.setCameraType('Orthographic' if ortho else 'Perspective'); v.setCameraOrientation(rot.Q)
    v.fitAll(); Gui.updateGui(); v.saveImage(S+'v_'+name+'.png',1400,1100,'White'); App.closeDocument(name); print('OK',name)
R=lambda ax,a:App.Rotation(V(*ax),a)
front=R((1,0,0),90).multiply(R((0,1,0),0))     # camera looks along +y (from the front)
q34=App.Rotation(V(0,0,1),28).multiply(App.Rotation(V(1,0,0),78))
shot('front',[('body',body,WH),('cap',cap,WH),('knob',knob,OR),('panel',pan,DK)],q34)
qb=App.Rotation(V(0,0,1),160).multiply(App.Rotation(V(1,0,0),70))
shot('back_open',[('body',body,WH),('cap',moved(cap,V(0,60,-45)),WH),('knob',knob,OR),('pin',pin,OR),('panel',pan,GN),('bat',moved(bat,V(0,30,0)),BL)],qb)
shot('back_empty',[('body',body,WH)],qb)
shot('cap_inside',[('cap',cap,WH)],App.Rotation(V(0,0,1),-20).multiply(App.Rotation(V(1,0,0),100)))
os._exit(0)
