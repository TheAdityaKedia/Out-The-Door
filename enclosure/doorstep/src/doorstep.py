# Clock-style case for CrowPanel 2.13". Front frame F: front face plane y=0, outward -y, z up, x right.
import FreeCAD as App, Part, math, os
V=App.Vector
OUT='/mnt/project-files/cloud-freecad/clock-case/snap-ring/'
W,H,D,RC,LEAN=68.0,44.0,30.0,9.0,6.0
WALL,RF,RB=1.8,3.0,4.0         # wall, front edge fillet, back edge fillet
LENS=1.5                       # front acrylic thickness
def rrect(w,h,r,y=0):
    p=Part.Face(Part.Wire(Part.makePolygon([V(-w/2+r,y,-h/2),V(w/2-r,y,-h/2),V(w/2-r,y,h/2),V(-w/2+r,y,h/2),V(-w/2+r,y,-h/2)])))
    f=Part.makeBox(w-2*r,1,h,V(-w/2+r,y,-h/2)).fuse(Part.makeBox(w,1,h-2*r,V(-w/2,y,-h/2+r)))
    for sx in(-1,1):
        for sz in(-1,1): f=f.fuse(Part.makeCylinder(r,1,V(sx*(w/2-r),y,sz*(h/2-r)),V(0,1,0)))
    return f.removeSplitter()
def prism(w,h,r,y0,L):
    s=rrect(w,h,r); s=s.common(Part.makeBox(w+2,1,h+2,V(-w/2-1,0,-h/2-1)))
    f=[x for x in s.Faces if abs(x.Surface.Axis.y if hasattr(x.Surface,'Axis') else 0)>0.99 and x.CenterOfMass.y<0.01][0] if False else None
    return Part.makeBox(1,1,1) if False else s.Faces and s  # placeholder
# simple roundrect prism via 2D wire extrusion
def rr_wire(w,h,r,y):
    import Part
    a=w/2-r; b=h/2-r
    edges=[]
    pts=[(a,-h/2),(w/2,-b),(w/2,b),(a,h/2),(-a,h/2),(-w/2,b),(-w/2,-b),(-a,-h/2)]
    edges.append(Part.LineSegment(V(-a,y,-h/2),V(a,y,-h/2)).toShape())
    edges.append(Part.Arc(V(a,y,-h/2),V(a+r*math.sin(math.pi/4),y,-b-r*math.cos(math.pi/4)),V(w/2,y,-b)).toShape())
    edges.append(Part.LineSegment(V(w/2,y,-b),V(w/2,y,b)).toShape())
    edges.append(Part.Arc(V(w/2,y,b),V(a+r*math.sin(math.pi/4),y,b+r*math.cos(math.pi/4)),V(a,y,h/2)).toShape())
    edges.append(Part.LineSegment(V(a,y,h/2),V(-a,y,h/2)).toShape())
    edges.append(Part.Arc(V(-a,y,h/2),V(-a-r*math.sin(math.pi/4),y,b+r*math.cos(math.pi/4)),V(-w/2,y,b)).toShape())
    edges.append(Part.LineSegment(V(-w/2,y,b),V(-w/2,y,-b)).toShape())
    edges.append(Part.Arc(V(-w/2,y,-b),V(-a-r*math.sin(math.pi/4),y,-b-r*math.cos(math.pi/4)),V(-a,y,-h/2)).toShape())
    return Part.Wire(edges)
def rr_prism(w,h,r,y0,L): return Part.Face(rr_wire(w,h,r,y0)).extrude(V(0,L,0))
# world <- F : rotate about x by -LEAN (top goes back)
ROT=App.Rotation(V(1,0,0),-LEAN); PL=App.Placement(V(0,0,0),ROT); M=PL.toMatrix()
def toW(s): return s.transformed(M)
def toF(s): return s.transformed(M.inverse())
s,c=math.sin(math.radians(LEAN)),math.cos(math.radians(LEAN))
zb=-H/2*c; yfb=-H/2*s          # world z of base, world y of front-bottom edge
big=200
def world_clip(inset=0):
    # half-spaces in world: z>=zb+inset, y<=yfb+D-inset ; return as F-frame solid
    b=Part.makeBox(big,big,big,V(-big/2,yfb+D-inset-big,zb+inset))
    return toF(b)
# ---------- body (built in world, then expressed in F) ----------
def rr_world(w,h,r,y0,L):   # roundrect in world XZ, extruded along world +y
    f=Part.Face(rr_wire(w,h,r,0)).extrude(V(0,L,0)); f.translate(V(0,y0,0)); return f
def fslab(y0,y1):           # slab between F-planes y=y0..y1, in world coords
    return toW(Part.makeBox(big,y1-y0,big,V(-big/2,y0,-big/2)))
DB=D-H/2*s                  # world y of back face (front plane passes world origin at z=0)
ow=rr_world(W,H,RC,-20,20+DB).common(fslab(0,100))
def fillet_by(shape,r,pred):
    return shape.makeFillet(r,[e for e in shape.Edges if pred(e)])
onF=lambda e:(lambda bb:abs(bb.YMax)<1e-3 and abs(bb.YMin)<1e-3)(toF(e).BoundBox)
ow=fillet_by(ow,RF,onF)
ow=fillet_by(ow,RB,lambda e:abs(e.BoundBox.YMin-DB)<1e-3 and abs(e.BoundBox.YMax-DB)<1e-3)
print("outer valid",ow.isValid(),"vol",round(ow.Volume))
iw=ow.makeOffsetShape(-WALL,0.01,join=0)
print("inner valid",iw.isValid())
bw=ow.cut(iw)
bw=bw.cut(rr_world(W-2*RF,H-2*RF,RC-RF,-30,60).common(fslab(-1,LENS)))          # lens pocket
bw=bw.cut(rr_world(W-2*RF-3,H-2*RF-3,RC-RF-1.5,-30,60).common(fslab(-1,10)))     # front opening
lensw=rr_world(W-2*RF-0.2,H-2*RF-0.2,RC-RF-0.1,-30,60).common(fslab(0,LENS))
body,lens,inner=toF(bw),toF(lensw),toF(iw)
zb=-H/2
# ---------- panel ----------
pn=Part.read('/mnt/project-files/case/crowpanel_2.13.step')
OY=LENS+0.1+0.9; CX=0.0   # body centred on the board; display sits 2.6 mm right of centre
PM=App.Matrix(0,0,-1,CX, 0,-1,0,OY, -1,0,0,0, 0,0,0,1)   # F = PM * panel
pnF=pn.transformed(PM)
def P(px,py,pz): return PM.multVec(V(px,py,pz))
# ---------- orange snap-on ring (MENU/BACK buttons removed from the board) ----------
# C-shaped ring with internal teeth that snaps over the wheel's knurled rim (tips r 7.3) in the layer
# panel y -3.6..-2.6, clear of the board and of every other part as it turns.
fy=lambda py:-py+OY
WC=P(0,0,-27); ax=V(0,1,0)
RI,RO=7.0,10.5
def cyl(r,y0,y1): return Part.makeCylinder(r,y1-y0,V(WC.x,y0,WC.z),ax)
ring=cyl(RO,fy(-2.6),fy(-3.6)).cut(cyl(RI,fy(-2.6),fy(-3.6)))
# 230 deg C: open toward the board, 12 mm gap at the inner edge snaps over the rim's ~9.7 mm exposed chord
gap=Part.makeBox(30,5,12.0,V(WC.x-30-RI+2.2,fy(-2.6)-1,WC.z-6.0))
ring=ring.cut(gap)
for i in range(64):
    a_=2*math.pi*i/64
    ring=ring.cut(Part.makeCylinder(0.45,5,V(WC.x+RO*math.cos(a_),fy(-2.6)-1,WC.z+RO*math.sin(a_)),ax))
knob=ring.removeSplitter()
slot=Part.makeCylinder(RO+0.8,fy(-3.6)-fy(-2.6)+1.0,V(WC.x,fy(-2.6)-0.5,WC.z),ax)
body=body.cut(slot)
# ---------- battery (103040, ~1500 mAh) ----------
bat=Part.makeBox(40,10,30,V(-24,fy(-9.8)+0.6,-15))
# ---------- USB-C tunnel through base + cable groove ----------
uc=P(15.6,-2.71,0.6)
tun=Part.makeBox(13,7.5,30,V(uc.x-6.5,uc.y-3.75,uc.z-30))
body=body.cut(tun)
gw=toW(body); gb=gw.BoundBox
groove=Part.makeBox(5.5,60,3.2,V(toW(Part.Vertex(uc)).Point.x-2.75,toW(Part.Vertex(uc)).Point.y,zb-1))
body=toF(gw.cut(groove))
print("body valid",body.isValid())
# ---------- checks ----------
cav=inner
def vol(a,b):
    try: return round(a.common(b).Volume,2)
    except Exception as e: return str(e)
solids=[x for x in pnF.Solids if not (50<x.Volume<60 or 5<x.Volume<6)]   # MENU/BACK removed
for x in solids:
    if knob.BoundBox.intersect(x.BoundBox):
        v=knob.common(x).Volume
        if v>0.01: print("knob hits", round(v,2), x.BoundBox)
print("knob x body:",vol(knob,body),"bat x body:",vol(bat,body),"bat x panel:",round(sum(bat.common(x).Volume for x in solids if bat.BoundBox.intersect(x.BoundBox)),2))
print("panel x body:",round(sum(body.common(x).Volume for x in solids if body.BoundBox.intersect(x.BoundBox)),2))
print("panel x lens:",round(sum(lens.common(x).Volume for x in solids if lens.BoundBox.intersect(x.BoundBox)),2))
kb=toW(knob).BoundBox; bb=toW(body).BoundBox
print("world body bbox %.1f x %.1f x %.1f"%(bb.XLength,bb.YLength,bb.ZLength),"knob juts %.1f mm"%(kb.XMax-bb.XMax))
# ---------- save ----------
if not os.environ.get("CHECK"):
    for n,sh in [('body',body),('front_lens',lens),('orange_snap_ring',knob)]:
        w=toW(sh); w.exportStep(OUT+n+'.step')
        import Mesh; m=Mesh.Mesh(); m.addFacets(w.tessellate(0.03)); m.write(OUT+n+'.stl')
    import pickle
    for n,sh in [('body',body),('lens',lens),('knob',knob),('bat',bat),('panel',pnF)]:
        sh.exportBrep('/tmp/claude-0/-home-user-Out-The-Door/56822852-6d72-5c39-94af-40178e0e6955/scratchpad/fc/crF_'+n+'.brep')
        toW(sh).exportBrep('/tmp/claude-0/-home-user-Out-The-Door/56822852-6d72-5c39-94af-40178e0e6955/scratchpad/fc/cr_'+n+'.brep')
    print("SAVED")
