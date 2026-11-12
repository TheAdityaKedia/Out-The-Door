# Lay the Doorstep-back parts flat for the bed -> print-ready/*.stl
import FreeCAD as App, Part, Mesh
V=App.Vector; S='build/'; OUT='print-ready/'
def ld(n): s=Part.Shape(); s.importBrep(S+n+'.brep'); return s
def down_y(s):   # put the +y face (world back / F back) on the bed
    s=s.copy(); s.rotate(V(0,0,0),V(1,0,0),-90)
    b=s.optimalBoundingBox(); s.translate(V(-b.Center.x,-b.Center.y,-b.ZMin)); return s
parts={'doorstep_back_body_white':down_y(ld('cc_body')),     # back face down, front face up (supports inside only)
       'doorstep_back_cap_white':down_y(ld('cc_plate')),   # back face down, lips up
       'latch_drum_orange':down_y(ld('ccF_knob')),
       'latch_pin_orange':down_y(ld('ccF_pin'))}             # head down
offs={'doorstep_back_body_white':V(130,175,0),'doorstep_back_cap_white':V(130,105,0),'latch_drum_orange':V(205,105,0),'latch_pin_orange':V(205,140,0)}
for n,s in parts.items():
    s.translate(offs[n]); b=s.optimalBoundingBox()
    fs=[f for f in s.Faces if f.optimalBoundingBox().ZMax<0.01]
    print(n,"%.1f x %.1f x %.1f"%(b.XLength,b.YLength,b.ZLength),"valid",s.isValid(),"bed contact mm2",round(sum(f.Area for f in fs),1))
    m=Mesh.Mesh(); m.addFacets(s.tessellate(0.02)); m.write(OUT+n+'.stl')
