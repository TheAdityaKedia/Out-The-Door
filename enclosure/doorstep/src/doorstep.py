# Clock-style case for CrowPanel 2.13". Front frame F: front face plane y=0, outward -y, z up, x right.
import FreeCAD as App, Part, math, os
V=App.Vector
OUT='/mnt/project-files/cloud-freecad/clock-case/'
W,H,D,RC,LEAN=80.0,44.0,30.0,9.0,6.0
WALL,RF,RB=1.8,3.0,4.0         # wall, front edge fillet, back edge fillet
LENS=2.0                       # front pocket depth: 2 mm acrylic OR the 2 mm bevelled insert
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
# bevelled insert: same outline/thickness as the lens; its front rolls inward in one convex curve
# from the seam down to a window 0.3 mm inside the active area at its back face
AAW,AAH=48.54,23.70
ow_,oh_,or_=W-2*RF-0.2,H-2*RF-0.2,RC-RF-0.1
iw_,ih_,ir_=AAW,AAH,0.8   # window flush with the screen's live area
SE=LENS
secs=[rr_wire(ow_+(iw_-ow_)*t, oh_+(ih_-oh_)*t, or_+(ir_-or_)*t, SE*t**1.6) for t in (0.0,0.2,0.4,0.6,0.8,1.0)]
slope=Part.makeLoft(secs,True,False)
bcut=slope.fuse(Part.Face(rr_wire(iw_,ih_,ir_,SE)).extrude(V(0,1.0,0))).fuse(Part.Face(rr_wire(ow_+2,oh_+2,or_+1,-1)).extrude(V(0,1.0,0)))
bevel=lens.cut(bcut)
# friction ridges: 0.45 mm proud (0.35 mm interference with the 0.1 mm pocket gap); 4 on top/bottom, 2 on the ends
RP=0.45
for bx in ():
    for sz in (-1,1):
        bevel=bevel.fuse(Part.makeCylinder(0.6,6,V(bx-3,LENS/2,sz*(oh_/2-0.6+RP)),V(1,0,0)))
# continuous groove in the plate's back (1.0 wide, 1.0 deep, 0.5 mm in from its edge) takes the body's tongue
# continuous lip on the plate's back (0.8 thick, 0.95 tall, flush with its outer edge) goes into the body's groove
LIPR=Part.Face(rr_wire(ow_,oh_,or_,LENS)).extrude(V(0,0.95,0)).cut(Part.Face(rr_wire(ow_-1.6,oh_-1.6,or_-0.8,LENS)).extrude(V(0,0.95,0)))
bevel=bevel.fuse(LIPR).removeSplitter()
bevel=bevel.removeSplitter()
print("bevel valid",bevel.isValid(),round(bevel.Volume,1))
zb=-H/2
# ---------- panel ----------
pn=Part.read('/mnt/project-files/case/crowpanel_2.13.step')
OY=LENS+0.7+0.9; CX=-2.625   # 0.7 mm gap glass-to-front (was 0.1: the panel pushed the front out)
PM=App.Matrix(0,0,-1,CX, 0,-1,0,OY, -1,0,0,0, 0,0,0,1)   # F = PM * panel
pnF=pn.transformed(PM)
def P(px,py,pz): return PM.multVec(V(px,py,pz))
# ---------- orange side drum (idler that drives the wheel rim) ----------
# The CrowPanel wheel sits in a housing; only a 2.7 mm sliver of its knurled rim sticks out past the board end.
# A hub (r 4) presses on that sliver; a bigger drum on the same axle juts out of the right side.
fy=lambda py:-py+OY
WC=P(0,0,-27)
AX=P(0,0,-27-7.3-4+1.85)         # axle centre, 1.85 mm nominal into the wheel: the springy arm takes up the
                                  # real-world error (test print missed by ~1.3 mm) and keeps the hub pressed on
ax=V(0,1,0)
def cyl(r,y0,y1,c=AX): return Part.makeCylinder(r,y1-y0,V(c.x,y0,c.z),ax)
# hub carries a rubber tyre: 6 mm ID x 1 mm nitrile O-ring stretched into a groove open at the front
# (floor r 2.85, back flange r 3.3, so only rubber can touch the wheel); the rubber (outer r ~3.8) is what touches the wheel
hub=cyl(2.85,fy(-2.1),fy(-3.2)).fuse(cyl(3.3,fy(-3.2),fy(-3.5)))
oring=Part.Face(Part.Wire(Part.makeCircle(0.475,V(AX.x+3.325,fy(-2.65),AX.z),V(0,0,1))))
oring=oring.revolve(V(AX.x,0,AX.z),V(0,1,0),360)
spacer=cyl(3.0,fy(-3.5),fy(-5.6))   # longer spacer: drum sits behind the wheel housing (y 8.7)
RD=12.0; drum=cyl(RD,fy(-5.6),fy(-10.9))   # 24 mm drum: pops out ~3 mm more
for i in range(80):
    a_=2*math.pi*i/80
    drum=drum.cut(Part.makeCylinder(0.4,10,V(AX.x+RD*math.cos(a_),fy(-5.6)-1,AX.z+RD*math.sin(a_)),ax))
# drum spins on a separate 3 mm pin (assembly: drum goes in sideways through the wall window,
# then the pin is pushed in from the front, through the drum, into a press-fit hole in the post)
knob=hub.fuse(spacer).fuse(drum).removeSplitter().cut(cyl(1.8,fy(-2.1)-1,fy(-10.9)+1))   # 3.6 mm bore: prints ~3.3-3.4, spins free on the 3 mm pin
YDB=fy(-10.9)                     # drum back face
pin=cyl(1.5,fy(-2.1),YDB+7.5).fuse(cyl(2.0,fy(-2.1)-0.7,fy(-2.1)))   # 3 mm pin with a 4 mm head that keeps the drum on the wheel
axle=pin
# slot in the right wall for hub + drum (0.8 mm radial, 0.5 mm axial clearance)
slot=cyl(RD+0.8,fy(-5.6)-0.5,fy(-10.9)+0.3).fuse(cyl(4.6,fy(-2.1)-0.5,fy(-5.6)-0.5))
body=body.cut(slot)
# straight-sided window through the right wall so the 18 mm drum can be passed in edge-first
win=Part.makeBox(20,fy(-10.9)-fy(-5.6)+0.8,24.2,V(AX.x,fy(-5.6)-0.5,AX.z-12.1)).fuse(Part.makeBox(39.55-AX.x,fy(-5.6)-fy(-2.1),9.2,V(AX.x,fy(-2.1)-0.5,AX.z-4.6)))   # hub pocket stops 0.45 mm short of the outside
body=body.cut(win)
# springy axle mount: a boss right behind the drum (0.2 mm gap, so the drum can't slide back off the wheel)
# hung from the top wall on a thin arm that flexes sideways. The arm pushes the hub into the wheel;
# pushing the drum bends it further and clicks the wheel's button.
boss=cyl(2.6,YDB+0.3,YDB+8.2)   # 0.3 mm behind the drum
sarm=Part.makeBox(1.2,5.0,30,V(AX.x-0.6,YDB+3.2,AX.z+2.0)).common(toF(ow))
hole=cyl(1.6,YDB,YDB+7.2)        # pin bottoms out here, leaving its head 0.3 mm off the drum (no clamping);        # 3.2 mm: prints undersize, snug push fit for the 3 mm pin
body=body.fuse(boss.fuse(sarm)).cut(hole)
# ---------- battery (103040, ~1500 mAh) ----------
bat=Part.makeBox(40,10,30,V(-29.0,fy(-9.8)+0.6,-15))
# ---------- USB-C tunnel through base + cable groove ----------
uc=P(15.6,-2.71,0.6)
tun=Part.makeBox(10.5,7.5,30,V(uc.x-5.25,uc.y-3.75,uc.z-30))   # plain opening for a straight USB-C plug from below
body=body.cut(tun)
gw=toW(body); gb=gw.BoundBox
groove=Part.makeBox(5.5,60,3.2,V(toW(Part.Vertex(uc)).Point.x-2.75,toW(Part.Vertex(uc)).Point.y,zb-1))
body=toF(gw)
# ---------- button pin-holes (MENU/EXIT) on right end ----------
for px in(-11.15,11.15):
    bp=P(px,-3.35,-30.3)
    body=body.cut(Part.makeCylinder(0.8,20,V(bp.x,bp.y,bp.z),V(1,0,0)))
# ---------- Kindle-style corner snaps (replaces back-wall posts) ----------
# Near each corner: a springy arm beside the board edge with a hook that snaps over the 1 mm bare
# margin on the board's front face, plus a small shelf under the board's back. Both hang off the
# top/bottom walls. The board pushes in from the front; the arms flex out and click over it.
outerF=toF(ow)
PB=-1.6                      # board back face (panel y) at the edges
ARM_T,CLR,HOOK,LIP=1.2,0.15,0.6,0.6
yF,yB=fy(0),fy(PB)           # board front / back face in F
ROOT=12.0                    # arm root depth (F y): long arm, low strain
snaps=[]
def zbox(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(min(x0,x1),y0,z0))
for sz in (-1,1):
    for (a0,a1),(t0,t1) in [((24.5,28.5),(29.4,31.4)),((-30.0,-26.0),(-25.5,-23.5))]:
        x0,x1=sorted((-a0+CX,-a1+CX))
        e=15.6+CLR                       # board edge clearance plane |z|
        arm=zbox(x0,x1,yF-LIP,ROOT,e,e+ARM_T)
        bridge=zbox(x0,x1,ROOT,ROOT+2.0,e,30)
        # hook: catch face at board front, ramp forward to the arm face
        tri=Part.Face(Part.makePolygon([V(x0,yF,e),V(x0,yF,e-HOOK-CLR),V(x0,yF-LIP,e),V(x0,yF,e)])).extrude(V(x1-x0,0,0))
        u=arm.fuse(bridge).fuse(tri)
        if sz<0: u=u.mirror(V(0,0,0),V(0,0,1))
        snaps.append(u)
# back stops: continuous ledges along both long walls under the board's back edge (1 mm overlap),
# with a 45 deg gusset to the wall so they print without supports (body prints back-down)
LT,OV=1.2,1.0
for sz in (-1,1):
    for xa,xb in [(-34.0,-31.6),(-26.6,22.9)]:
        tri=Part.Face(Part.makePolygon([V(xa,yB,15.6-OV),V(xa,yB+LT,15.6-OV),V(xa,yB+LT+6.0,21.6-OV),V(xa,yB,21.6-OV+6),V(xa,yB,15.6-OV)])).extrude(V(xb-xa,0,0))
        led=tri.fuse(zbox(xa,xb,yB,yB+LT,15.6-OV,30)).fuse(zbox(xa,xb,yB,yB+LT+6.0,21.6-OV,30))
        if sz<0: led=led.mirror(V(0,0,0),V(0,0,1))
        for x in pnF.Solids:     # notch around parts on the board's back near the edge
            if x.Volume<3000 and x.BoundBox.intersect(led.BoundBox) and led.common(x).Volume>0.001:
                bb=x.BoundBox; led=led.cut(Part.makeBox(bb.XLength+1.0,40,bb.ZLength+1.0,V(bb.XMin-0.5,0,bb.ZMin-0.5)))
        snaps.append(led)
# end stops: ribs from the back wall that touch the board's short edges (0.15 mm gap), so it can't slide sideways.
# Far end: one wide rib. Wheel end: two ribs beside the wheel housing, clear of the drum (|z| 10..14).
xFar=-31.6+CX-0.05; xWheel=31.6+CX+CLR
for sz in (-1,1):   # far end: two corner ribs, middle left open for the panel's flat cable that wraps round this end
    snaps.append(zbox(-40,xFar,yF-0.4,40,(10.5 if sz>0 else -14.5),(14.5 if sz>0 else -10.5)))
for sz in (-1,1):
    z0,z1=(10,14) if sz>0 else (-14,-10)
    zc=11.15 if sz>0 else -11.15; yb=fy(-3.35)        # button plunger centre (tip at x 29.78)
    wk=zbox(xWheel,30.2,yF-0.4,yB+0.2,z0,z1)           # end stop: touches the PCB end, in front of the plunger
    wk=wk.fuse(zbox(30.2,38.6,yF-0.4,14.6,z0,z1))      # solid block tied into the side wall
    wk=wk.fuse(zbox(30.2,32.4,14.6,40,z0,z1))          # pillar to the back wall
    zo=(z1,z1+5) if sz>0 else (z0-5,z0)                 # base gussets (body prints back-down: bed = back wall)
    g1=Part.Face(Part.makePolygon([V(30.2,18,z1 if sz>0 else z0),V(30.2,40,z1 if sz>0 else z0),V(30.2,40,(z1 if sz>0 else z0)+5*sz),V(30.2,18,z1 if sz>0 else z0)])).extrude(V(2.2,0,0))
    g2=Part.Face(Part.makePolygon([V(30.2,18,z0 if sz>0 else z1),V(30.2,40,z0 if sz>0 else z1),V(30.2,40,(z0-5) if sz>0 else (z1+5)),V(30.2,18,z0 if sz>0 else z1)])).extrude(V(2.2,0,0))
    g3=Part.Face(Part.makePolygon([V(32.4,20,z0),V(32.4,40,z0),V(37.4,40,z0),V(32.4,20,z0)])).extrude(V(0,0,z1-z0))
    wk=wk.fuse(g1).fuse(g2).fuse(g3)
    # press tab: 0.8 mm leaf facing the plunger, free at the front, 1 mm gap behind it; a pin pushed
    # through the side-wall hole bends it onto the button. A ramped nub sits 0.08 mm off the plunger tip.
    wk=wk.cut(zbox(31.0,32.0,yb-0.75,14.0,z0-1,z1+1)).cut(zbox(30.2,32.0,yB+0.2,yb-0.75,z0-1,z1+1))
    nub=Part.Face(Part.makePolygon([V(30.2,yb-0.75,zc-0.5),V(29.85,yb,zc-0.5),V(29.85,yb+0.5,zc-0.5),V(30.2,yb+0.75,zc-0.5),V(30.2,yb-0.75,zc-0.5)])).extrude(V(0,0,1.0))
    dsw=Part.makeBox(AX.x+2.0+40,fy(-10.9)-fy(-5.6)+0.8,25.0,V(-40,fy(-5.6)-0.5,AX.z-12.5)).fuse(Part.makeCylinder(RD+0.5,fy(-10.9)-fy(-5.6)+0.8,V(AX.x+2.0,fy(-5.6)-0.5,AX.z),ax))
    snaps.append(wk.fuse(nub).cut(dsw))
# seat: ledge round the mouth 2 mm behind the face (the plate rests on it, so it always sits flush),
# 45 deg chamfer underneath (prints back-down without supports); continuous tongue on it for the plate's groove
PW,PH,PR=W-2*RF,H-2*RF,RC-RF                 # pocket outline 74 x 38 r 6
seat=Part.Face(rr_wire(PW+6,PH+6,PR+3,LENS)).extrude(V(0,4.0,0)).cut(Part.makeLoft([rr_wire(PW-3.8,PH-3.8,PR-1.9,LENS-0.01),rr_wire(PW-3.8,PH-3.8,PR-1.9,LENS+0.6),rr_wire(PW+3.4,PH+3.4,PR+1.7,LENS+4.0)],True,True))
pcut=Part.Shape(cyl(2.4,-3,fy(-2.1)))      # notch the seat so the pin's 4 mm head can be pushed in from the front
seat=seat.cut(pcut)
for _sz in (-1,1):                          # clear the seat's chamfer where the corner snap arms flex out
    for _x0,_x1 in ((-31.6,-26.6),(22.9,27.9)):
        seat=seat.cut(zbox(_x0,_x1,LENS+0.6,LENS+5,(15.6 if _sz>0 else -21),(21 if _sz>0 else -15.6)))
snaps.append(seat)
print("snaps valid",[x.isValid() for x in snaps])
supports=snaps[0]
for x_ in snaps[1:]: supports=supports.fuse(x_)
supports=supports.common(outerF)
if os.environ.get("DIAG"):
    for i,x_ in enumerate(snaps):
        print("fuse",i,body.fuse(x_.common(outerF)).isValid())
_b=body.fuse(supports); print("fuse no-splitter valid",_b.isValid())
_c=_b.removeSplitter(); print("splitter valid",_c.isValid())
body=_c if _c.isValid() else _b
print("after supports valid",body.isValid())
body=body.cut(tun)          # re-open the USB-C tunnel (the bottom ledge had filled it)
SGRV=Part.Face(rr_wire(PW,PH,PR,LENS-0.1)).extrude(V(0,1.1,0)).cut(Part.Face(rr_wire(PW-2.0,PH-2.0,PR-1.0,LENS-0.1)).extrude(V(0,1.1,0)))
body=body.cut(SGRV)                       # continuous 1.0 x 1.0 mm groove in the seat for the plate's lip
body=body.cut(win).cut(slot)                # re-open the wheel window and hub pocket (the seat chamfer had filled part of it)
print("after tun+groove valid",body.isValid())
for px in(-11.15,11.15):   # button pin holes: one straight bore from the tab's gap out through the side wall
    bp=P(px,-3.35,-30.3)
    body=body.cut(Part.makeCylinder(0.8,12,V(31.5,bp.y,bp.z),V(1,0,0)))
print("after pinholes valid",body.isValid())
for x in pnF.Solids:
    if x.BoundBox.intersect(supports.BoundBox):
        v=supports.common(x).Volume
        if v>0.01: print("support hits",round(v,2),x.BoundBox)
print("support x bat",round(supports.common(bat).Volume,2),"support x knob",round(supports.common(knob).Volume,2))
print("body valid",body.isValid())
print("bevel x body (seat/tongue fit):",round(bevel.common(body).Volume,3))
_hits=[]
for _dy in (-16,-12,-8,-4,-2,0):          # drop in at the left (drum x max 29.0), then slide right
    _kb=knob.copy(); _kb.translate(V(29.0-(AX.x+RD),_dy,0)); _hits.append(round(_kb.common(body).Volume,2))
for _dx in (0,4,8,12,(AX.x+RD-29.0)):
    _kb=knob.copy(); _kb.translate(V(29.0-(AX.x+RD)+_dx,0,0)); _hits.append(round(_kb.common(body).Volume,2))
print("drum insertion path x body:",_hits)
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
for x in solids:
    if oring.BoundBox.intersect(x.BoundBox):
        v=oring.common(x).Volume
        if v>0.01: print("oring presses wheel", round(v,2), x.BoundBox)
print("oring vol",round(oring.Volume,2),"outer r",round(oring.BoundBox.XMax-AX.x,2))
print("pin path from front x body:",vol(cyl(1.6,-3,fy(-2.1)),body),"pin x body (should be ~press):",vol(pin,body))
print("tunnel x body:",vol(tun,body)); print("bevel x panel:",round(sum(bevel.common(x).Volume for x in pnF.Solids if bevel.BoundBox.intersect(x.BoundBox)),3))
print("boss to right wall gap:", round(min(f.distToShape(boss)[0] for f in [Part.makeBox(1,40,10,V(38.2,YDB,-5))]),2)); print("arm length:",round(sarm.BoundBox.ZLength,1), sarm.BoundBox, "vol",round(sarm.Volume,1)); print("pinhead vs wheel x:", round(pin.BoundBox.XMax,2), "drum front y", round(pin.BoundBox.YMin,2)); print("pin len",round(pin.BoundBox.YLength,2),"hole depth 7.7")
print("knob x body:",vol(knob,body),"bat x body:",vol(bat,body),"bat x panel:",round(sum(bat.common(x).Volume for x in solids if bat.BoundBox.intersect(x.BoundBox)),2))
print("panel x body:",round(sum(body.common(x).Volume for x in solids if body.BoundBox.intersect(x.BoundBox)),2))
print("panel x lens:",round(sum(lens.common(x).Volume for x in solids if lens.BoundBox.intersect(x.BoundBox)),2))
kb=toW(knob).BoundBox; bb=toW(body).BoundBox
print("world body bbox %.1f x %.1f x %.1f"%(bb.XLength,bb.YLength,bb.ZLength),"knob juts %.1f mm"%(kb.XMax-bb.XMax))
# ---------- save ----------
if not os.environ.get("CHECK"):
    for n,sh in [('body',body),('front_lens',lens),('front_bevel',bevel),('orange_wheel_cap',knob),('latch_pin',pin)]:
        w=toW(sh); w.exportStep(OUT+n+'.step')
        import Mesh; m=Mesh.Mesh(); m.addFacets(w.tessellate(0.03)); m.write(OUT+n+'.stl')
    import pickle
    for n,sh in [('body',body),('lens',lens),('bevel',bevel),('knob',knob),('pin',pin),('bat',bat),('panel',pnF),('oring',oring)]:
        sh.exportBrep('/tmp/claude-0/-home-user-Out-The-Door/56822852-6d72-5c39-94af-40178e0e6955/scratchpad/fc/ccF_'+n+'.brep')
        toW(sh).exportBrep('/tmp/claude-0/-home-user-Out-The-Door/56822852-6d72-5c39-94af-40178e0e6955/scratchpad/fc/cc_'+n+'.brep')
    print("SAVED")
