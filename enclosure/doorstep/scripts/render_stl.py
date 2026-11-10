# Render one print-ready STL from two angles: RSTL=in.stl ROUT=out_prefix  (needs GUI build under xvfb)
import FreeCAD as App, FreeCADGui as Gui, Mesh, os
V=App.Vector
Gui.showMainWindow()
App.ParamGet("User parameter:BaseApp/Preferences/View").SetBool("UseNavigationAnimations",False)
stl=os.environ['RSTL']; out=os.environ['ROUT']
col=(1.0,0.45,0.1) if 'orange' in stl else (0.93,0.93,0.91)
doc=App.newDocument('r'); o=doc.addObject('Mesh::Feature','m'); o.Mesh=Mesh.Mesh(stl)
o.ViewObject.ShapeColor=col; doc.recompute()
v=Gui.ActiveDocument.ActiveView; v.setCameraType('Perspective')
for name,rot in [('top',App.Rotation(V(1,0,0),35).multiply(App.Rotation(V(0,0,1),20))),('under',App.Rotation(V(1,0,0),145).multiply(App.Rotation(V(0,0,1),-20)))]:
    v.setCameraOrientation(rot.Q); v.fitAll(); Gui.updateGui(); v.saveImage(out+'_'+name+'.png',1000,800,'White')
print('OK'); App.closeDocument('r')
os._exit(0)
