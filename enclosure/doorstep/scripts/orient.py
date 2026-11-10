import FreeCAD as App, Part, Mesh
V=App.Vector; S='build/'
OUT='print-ready/'
def ld(n): s=Part.Shape(); s.importBrep(S+n+'.brep'); return s
def down_y(s, flip=False):   # put the +y face on the bed (flip: -y face on bed)
    s=s.copy(); s.rotate(V(0,0,0),V(1,0,0), 90 if flip else -90)
    b=s.optimalBoundingBox(); s.translate(V(-b.Center.x,-b.Center.y,-b.ZMin)); return s
parts={'doorstep_body_white':down_y(ld('cc_body')),
       'doorstep_slope_front_white':down_y(ld('ccF_bevel')),
       'latch_drum_orange':down_y(ld('ccF_knob')),
       'latch_pin_orange':(lambda q:(q.translate(V(-q.BoundBox.Center.x,-q.BoundBox.Center.y,-q.BoundBox.ZMin)),q)[1])((lambda s:(s.rotate(V(0,0,0),V(1,0,0),90),s)[1])(ld('ccF_pin')))}
# arrange on plate centre 175,160
offs={'doorstep_body_white':V(130,175,0),'doorstep_slope_front_white':V(130,95,0),'latch_drum_orange':V(200,95,0),'latch_pin_orange':V(200,130,0)}
ms=[]
for n,s in parts.items():
    s.translate(offs[n]); b=s.optimalBoundingBox()
    print(n,"%.1f x %.1f x %.1f"%(b.XLength,b.YLength,b.ZLength),"zmin",round(b.ZMin,3),"valid",s.isValid())
    m=Mesh.Mesh(); m.addFacets(s.tessellate(0.02)); m.write(OUT+n+'.stl'); ms.append((n,m))
# check bed contact area
for n,s in parts.items():
    fs=[f for f in s.Faces if f.optimalBoundingBox().ZMax<0.01]
    print(n,"bed contact mm2",round(sum(f.Area for f in fs),1))
