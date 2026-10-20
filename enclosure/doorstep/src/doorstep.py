# Clock-style case for CrowPanel 2.13". Front frame F: front face plane y=0, outward -y, z up, x right.
import FreeCAD as App, Part, math, os
V=App.Vector
OUT='/mnt/project-files/cloud-freecad/clock-case/bezel/'
W,H,D,RC,LEAN=80.0,44.0,30.0,9.0,6.0
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
body,inner,outer_F=toF(bw),toF(iw),toF(ow)
# sloped bezel: the whole flat front rolls inward in one continuous convex curve, from where the outer
# edge fillet ends down to a window 0.3 mm inside the active area. Symmetric (display centred on the body).
AAW,AAH=48.54,23.70
FRONT=float(os.environ.get("FRONT","2.0"))                         # glass sits this far behind the face
ow_,oh_,or_=W-2*RF,H-2*RF,RC-RF   # outline of the flat front
iw_,ih_,ir_=AAW-0.6,AAH-0.6,0.8   # window at the glass
secs=[]
for t in (0.0,0.2,0.4,0.6,0.8,1.0):
    y=FRONT*t**1.6
    secs.append(rr_wire(ow_+(iw_-ow_)*t, oh_+(ih_-oh_)*t, or_+(ir_-or_)*t, y))
slope=Part.makeLoft(secs,True,False)
cutter=slope.fuse(Part.Face(rr_wire(iw_,ih_,ir_,FRONT)).extrude(V(0,1.0,0))).fuse(Part.Face(rr_wire(ow_,oh_,or_,-1)).extrude(V(0,1.0,0)))
body=body.fuse(outer_F.common(Part.makeBox(200,FRONT,200,V(-100,0,-100)))).cut(cutter)
# pocket for the CrowPanel behind a thin front wall (board 63.2 x 31.3 + 0.4 clearance)
body=body.cut(Part.makeBox(63.6,4.0,31.7,V(-31.8-2.625,FRONT,-15.85)))
lens=Part.makeBox(AAW,0.05,AAH,V(-AAW/2,FRONT-0.05,-AAH/2))   # stands in for the e-paper surface in renders
zb=-H/2
# ---------- panel ----------
pn=Part.read('/mnt/project-files/case/crowpanel_2.13.step')
OY=FRONT+0.9; CX=-2.625      # glass sits against the back of the front wall
PM=App.Matrix(0,0,-1,CX, 0,-1,0,OY, -1,0,0,0, 0,0,0,1)   # F = PM * panel
pnF=pn.transformed(PM)
def P(px,py,pz): return PM.multVec(V(px,py,pz))
# ---------- orange side drum (idler that drives the wheel rim) ----------
# The CrowPanel wheel sits in a housing; only a 2.7 mm sliver of its knurled rim sticks out past the board end.
# A hub (r 4) presses on that sliver; a bigger drum on the same axle juts out of the right side.
fy=lambda py:-py+OY
WC=P(0,0,-27)
AX=P(0,0,-27-7.3-4+0.2)          # axle centre, 0.2 mm preload into the wheel teeth
ax=V(0,1,0)
def cyl(r,y0,y1,c=AX): return Part.makeCylinder(r,y1-y0,V(c.x,y0,c.z),ax)
hub=cyl(4.0,fy(-2.1),fy(-3.5))
spacer=cyl(2.5,fy(-3.5),fy(-4.2))
RD=9.0; drum=cyl(RD,fy(-4.2),fy(-9.5))
for i in range(60):
    a_=2*math.pi*i/60
    drum=drum.cut(Part.makeCylinder(0.4,10,V(AX.x+RD*math.cos(a_),fy(-4.2)-1,AX.z+RD*math.sin(a_)),ax))
axle=cyl(1.5,fy(-9.5),fy(-9.5)+11)
knob=hub.fuse(spacer).fuse(drum).fuse(axle).removeSplitter()
# slot in the right wall for hub + drum (0.8 mm radial, 0.5 mm axial clearance)
slot=cyl(RD+0.8,fy(-2.1)-0.5,fy(-9.5)+0.5)
body=body.cut(slot)
# axle post from the back wall, with a hole slotted 1.2 mm toward the wheel so a press clicks it
post=cyl(3.4,fy(-9.5)+0.6,fy(-9.5)+40).common(inner.common(Part.makeBox(200,200,200,V(-100,-100,-100))))
hole=cyl(1.65,fy(-9.5),fy(-9.5)+12).fuse(cyl(1.65,fy(-9.5),fy(-9.5)+12,AX+V(-1.2,0,0))).fuse(Part.makeBox(1.2,12,3.3,V(AX.x-1.2,fy(-9.5),AX.z-1.65)))
body=body.fuse(post).cut(hole)
# ---------- battery (103040, ~1500 mAh) ----------
bat=Part.makeBox(40,10,30,V(-33.5,fy(-9.8)+0.6,-15))
# ---------- USB-C tunnel through base + cable groove ----------
uc=P(15.6,-2.71,0.6)
tun=Part.makeBox(13,7.5,30,V(uc.x-6.5,uc.y-3.75,uc.z-30))
body=body.cut(tun)
gw=toW(body); gb=gw.BoundBox
groove=Part.makeBox(5.5,60,3.2,V(toW(Part.Vertex(uc)).Point.x-2.75,toW(Part.Vertex(uc)).Point.y,zb-1))
body=toF(gw.cut(groove))
# ---------- button pin-holes (MENU/EXIT) on right end ----------
for px in(-11.15,11.15):
    bp=P(px,-3.35,-30.3)
    body=body.cut(Part.makeCylinder(0.8,20,V(bp.x,bp.y,bp.z),V(1,0,0)))
SPLIT=5.5
slabF=Part.makeBox(200,SPLIT+50,200,V(-100,-50,-100))
lid=body.common(slabF); shell=body.cut(slabF)
print("body valid",body.isValid(),"lid",lid.isValid(),"shell",shell.isValid())
# ---------- checks ----------
cav=inner
def vol(a,b):
    try: return round(a.common(b).Volume,2)
    except Exception as e: return str(e)
solids=pnF.Solids
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
    for n,sh in [('front_lid',lid),('back_shell',shell),('orange_drum',knob)]:
        w=toW(sh); w.exportStep(OUT+n+'.step')
        import Mesh; m=Mesh.Mesh(); m.addFacets(w.tessellate(0.03)); m.write(OUT+n+'.stl')
    import pickle
    for n,sh in [('lid',lid),('shell',shell),('lens',lens),('knob',knob),('bat',bat),('panel',pnF)]:
        sh.exportBrep('/tmp/claude-0/-home-user-Out-The-Door/56822852-6d72-5c39-94af-40178e0e6955/scratchpad/fc/cbF_'+n+'.brep')
        toW(sh).exportBrep('/tmp/claude-0/-home-user-Out-The-Door/56822852-6d72-5c39-94af-40178e0e6955/scratchpad/fc/cb_'+n+'.brep')
    print("SAVED")
