# Doorstep-back: one-piece body (bevelled front + window, no front plate). The CrowPanel goes in from the back,
# then a flat back plate snaps into an inset rabbet. Same outside as Doorstep (80 x 44 x 30, 6 deg lean).
# Frames: F = front face plane y=0, y grows backwards, z up, x towards the wheel end. World = F leaned back 6 deg,
# base on z, back face is the plane y=DB.
import FreeCAD as App, Part, math, os, sys
V=App.Vector
OUT='models/'   # run from enclosure/doorstep-back
os.makedirs('build',exist_ok=True); os.makedirs(OUT,exist_ok=True)
W,H,D,RC,LEAN=80.0,44.0,30.0,9.0,6.0
WALL,RF,RB=1.8,3.0,4.0         # wall, front edge fillet, back edge fillet
FW=2.0                         # front wall thickness
def rr_wire(w,h,r,y):
    a=w/2-r; b=h/2-r; k=math.sin(math.pi/4)
    e=[Part.LineSegment(V(-a,y,-h/2),V(a,y,-h/2)).toShape(),
       Part.Arc(V(a,y,-h/2),V(a+r*k,y,-b-r*k),V(w/2,y,-b)).toShape(),
       Part.LineSegment(V(w/2,y,-b),V(w/2,y,b)).toShape(),
       Part.Arc(V(w/2,y,b),V(a+r*k,y,b+r*k),V(a,y,h/2)).toShape(),
       Part.LineSegment(V(a,y,h/2),V(-a,y,h/2)).toShape(),
       Part.Arc(V(-a,y,h/2),V(-a-r*k,y,b+r*k),V(-w/2,y,b)).toShape(),
       Part.LineSegment(V(-w/2,y,b),V(-w/2,y,-b)).toShape(),
       Part.Arc(V(-w/2,y,-b),V(-a-r*k,y,-b-r*k),V(-a,y,-h/2)).toShape()]
    return Part.Wire(e)
ROT=App.Rotation(V(1,0,0),-LEAN); M=App.Placement(V(0,0,0),ROT).toMatrix()
def toW(s): return s.transformed(M)
def toF(s): return s.transformed(M.inverse())
def pW(p): return M.multVec(p)
s6=math.sin(math.radians(LEAN))
big=200
def rr_world(w,h,r,y0,L,zc=0.0):
    f=Part.Face(rr_wire(w,h,r,0)).extrude(V(0,L,0)); f.translate(V(0,y0,zc)); return f
def fslab(y0,y1): return toW(Part.makeBox(big,y1-y0,big,V(-big/2,y0,-big/2)))
def wslab(y0,y1): return Part.makeBox(big,y1-y0,big,V(-big/2,y0,-big/2))
def zbox(x0,x1,y0,y1,z0,z1): return Part.makeBox(abs(x1-x0),abs(y1-y0),abs(z1-z0),V(min(x0,x1),min(y0,y1),min(z0,z1)))
def fuse_ok(a,b):
    _b=a.fuse(b); _c=_b.removeSplitter(); return _c if _c.isValid() else _b
DB=D-H/2*s6                    # world y of the back face
ow=rr_world(W,H,RC,-20,20+DB).common(fslab(0,100))
onF=lambda e:(lambda bb:abs(bb.YMax)<1e-3 and abs(bb.YMin)<1e-3)(toF(e).BoundBox)
ow=ow.makeFillet(RF,[e for e in ow.Edges if onF(e)])
ow=ow.makeFillet(RB,[e for e in ow.Edges if abs(e.BoundBox.YMin-DB)<1e-3 and abs(e.BoundBox.YMax-DB)<1e-3])
iw=ow.makeOffsetShape(-WALL,0.01,join=0)
print("outer/inner valid",ow.isValid(),iw.isValid())
bw=ow.cut(iw.common(fslab(FW,100)))           # closed 2 mm front wall
outerF=toF(ow); innerF=toF(iw)
body=toF(bw)
# ---------- front: one convex bevel rolling from the flat face down to the window ----------
AAW,AAH=48.54,23.70
ow_,oh_,or_=W-2*RF-2.0,H-2*RF-2.0,RC-RF-1.0          # 72 x 36 r5: leaves a 1 mm flat band inside the edge fillet
iw_,ih_,ir_=AAW-0.6,AAH-0.6,0.8                      # window 0.3 mm inside the live area
secs=[rr_wire(ow_+(iw_-ow_)*t, oh_+(ih_-oh_)*t, or_+(ir_-or_)*t, FW*t**1.6) for t in (0.0,0.2,0.4,0.6,0.8,1.0)]
slope=Part.makeLoft(secs,True,False)
bcut=slope.fuse(Part.Face(rr_wire(iw_,ih_,ir_,FW)).extrude(V(0,1.0,0))).fuse(Part.Face(rr_wire(ow_+0.01,oh_+0.01,or_,-1)).extrude(V(0,1.0,0)))
body=body.cut(bcut)
print("front valid",body.isValid())
# ---------- panel ----------
pn=Part.read(os.environ.get('CROWPANEL_STEP','vendor/crowpanel_2.13.step'))
OY=FW+0.7+0.9; CX=-2.625      # glass 0.7 mm behind the front wall
PM=App.Matrix(0,0,-1,CX, 0,-1,0,OY, -1,0,0,0, 0,0,0,1)
pnF=pn.transformed(PM)
def P(px,py,pz): return PM.multVec(V(px,py,pz))
fy=lambda py:-py+OY
yF,yB=fy(0),fy(-1.6)          # board front / back face
# ---------- drum (same as Doorstep drum-3) ----------
AX=P(0,0,-27-7.3-4+1.85); ax=V(0,1,0)
def cyl(r,y0,y1,c=AX): return Part.makeCylinder(r,y1-y0,V(c.x,y0,c.z),ax)
hub=cyl(4.0,fy(-2.1),fy(-3.5)); spacer=cyl(3.0,fy(-3.5),fy(-5.6))
RD=12.0; drum=cyl(RD,fy(-5.6),fy(-10.9))
for i in range(80):
    a_=2*math.pi*i/80
    drum=drum.cut(Part.makeCylinder(0.4,10,V(AX.x+RD*math.cos(a_),fy(-5.6)-1,AX.z+RD*math.sin(a_)),ax))
knob=hub.fuse(spacer).fuse(drum).removeSplitter().cut(cyl(1.8,fy(-2.1)-1,fy(-10.9)+1))
YDB=fy(-10.9)
slot=cyl(RD+0.8,fy(-5.6)-0.5,fy(-10.9)+0.3).fuse(cyl(4.6,fy(-2.1)-0.5,fy(-5.6)-0.5))
win=Part.makeBox(20,fy(-10.9)-fy(-5.6)+0.8,24.2,V(AX.x,fy(-5.6)-0.5,AX.z-12.1)).fuse(Part.makeBox(39.55-AX.x,fy(-5.6)-fy(-2.1),9.2,V(AX.x,fy(-2.1)-0.5,AX.z-4.6)))
# springy axle mount, now with a through hole: the pin goes in from the back, head behind the boss
BOSS1=YDB+8.2
# the boss is flattened on the board side (x 31.95) so the panel's wheel (x max 31.72) slides past it as the
# board goes in; extra wall on the far side, where the wheel's push lands
boss=cyl(2.6,YDB+0.3,BOSS1).fuse(Part.makeCylinder(2.6,BOSS1-YDB-0.3,V(AX.x+0.8,YDB+0.3,AX.z),ax)).cut(zbox(20,31.95,YDB,BOSS1+1,-10,10))
sarm=Part.makeBox(1.2,5.0,30,V(AX.x-0.6,YDB+3.2,AX.z+2.0)).common(outerF)
hole=cyl(1.6,YDB,BOSS1+1)
pin=cyl(1.5,fy(-2.1)+0.2,BOSS1).fuse(cyl(2.0,BOSS1,BOSS1+0.8))   # 3 mm pin, 4 mm head at the back
# ---------- battery (103040) ----------
bat=Part.makeBox(40,10,30,V(-29.0,fy(-9.8)+0.6,-15))
# ---------- USB-C ----------
uc=P(15.6,-2.71,0.6)
tun=Part.makeBox(10.5,7.5,30,V(uc.x-5.25,uc.y-3.75,uc.z-30))
# ---------- back cap split (world) ----------
# The back opening has to be as big as the inside (the board slides in tilted 6 deg, the pin goes in at x 34),
# so there is no room for an inset plate with a flat rim to print on. Instead the back cap is the whole back
# face plus its 4 mm edge round, split off where the round meets the flat sides (world y = DB-4).
SPLIT=DB-RB
brd=[x for x in pnF.Solids if x.Volume>3000][0]
IWW,IWH,IWR=W-2*WALL,H-2*WALL,RC-WALL          # inside cross-section near the back: 76.4 x 40.4 r7.2
LIPD,LIPT,LCLR=3.5,1.0,0.1                      # cap lips: 3.5 deep, 1.0 thick, 0.1 off the wall
lipring=rr_world(IWW-2*LCLR,IWH-2*LCLR,IWR-LCLR,SPLIT-LIPD,LIPD+0.01).cut(rr_world(IWW-2*LCLR-2*LIPT,IWH-2*LCLR-2*LIPT,IWR-LCLR-LIPT,SPLIT-LIPD-1,LIPD+2))
LIPX=[(-26.0,-22.0),(-14.0,8.0),(16.0,22.0)]    # top/bottom lips (clear of the board-snap gussets)
TABX=[(-21.0,-15.0),(9.0,15.0)]                 # snap tabs between them
TABL=6.5; TH=0.45                               # tab length past the split, hook height

# ---------- internal parts (F frame) ----------
parts=[]
# front pads: ribs from the top/bottom walls onto the board's 1 mm bare front rim (glass ends at |z| 14.6),
# 45 deg underside so they print without supports (body prints back-down)
PADX=[(-24,-20),(-8,-4),(6,10),(18,22)]
for x0,x1 in PADX:
    for sz in (1,-1):
        pr=Part.Face(Part.makePolygon([V(x0,FW-0.01,14.85),V(x0,yF-0.03,14.85),V(x0,yF-0.03,15.75),V(x0,yF+5.0,20.8),V(x0,FW-0.01,20.8),V(x0,FW-0.01,14.85)])).extrude(V(x1-x0,0,0))
        if sz<0: pr=pr.mirror(V(0,0,0),V(0,0,1))
        parts.append(pr)
# edge stops (as Doorstep): rigid ribs 0.1 mm off the board's long edges
for _x,_s in [(-20.0,1),(uc.x,1),(15.0,1),(-20.0,-1),(uc.x-8.5,-1),(uc.x+8.5,-1),(15.0,-1)]:
    _zl,_zh=(15.7,23) if _s>0 else (-23,-15.7)
    parts.append(zbox(_x-1.5,_x+1.5,yF,yB,_zl,_zh))
# board snaps: springy arms beside the board edge, rooted 11 mm behind it; a hook catches the board's back
# face (0.6 mm over its edge), with a ramp facing the back so the board clicks in from behind
ARM_T,CLR,HOOK=1.0,0.15,0.6
ROOT=yB+11.0
SNAPX=[(-31.1,-27.1),(23.4,27.4)]
for x0,x1 in SNAPX:
    for sz in (1,-1):
        e=15.6+CLR
        arm=zbox(x0,x1,yB-0.8,ROOT,e,e+ARM_T)
        bridge=zbox(x0,x1,ROOT,ROOT+1.6,e,30)
        gus=Part.Face(Part.makePolygon([V(x0,ROOT+1.6,e),V(x0,ROOT+1.6,30),V(x0,ROOT+1.6+(30-e),30),V(x0,ROOT+1.6,e)])).extrude(V(x1-x0,0,0))
        hook=Part.Face(Part.makePolygon([V(x0,yB-0.12,e),V(x0,yB-0.12,e-HOOK-CLR),V(x0,yB+0.9,e),V(x0,yB-0.12,e)])).extrude(V(x1-x0,0,0))
        u=arm.fuse(bridge).fuse(gus).fuse(hook)
        if sz<0: u=u.mirror(V(0,0,0),V(0,0,1))
        parts.append(u)
# far end ribs (FPC passes between them)
xFar=-31.6+CX-0.05; xWheel=31.6+CX+CLR
for sz in (-1,1):
    parts.append(zbox(-40,xFar,yF-0.4,40,(10.5 if sz>0 else -14.5),(14.5 if sz>0 else -10.5)))
dsw=Part.makeBox(AX.x+2.0+40,fy(-10.9)-fy(-5.6)+0.8,25.0,V(-40,fy(-5.6)-0.5,AX.z-12.5)).fuse(Part.makeCylinder(RD+0.5,fy(-10.9)-fy(-5.6)+0.8,V(AX.x+2.0,fy(-5.6)-0.5,AX.z),ax))
for sz in (-1,1):   # wheel end: end stop, block into the side wall, pillar to the back, button press tab
    z0,z1=(10,14) if sz>0 else (-14,-10)
    zc=11.15 if sz>0 else -11.15; yb=fy(-3.35)
    wk=zbox(xWheel,30.2,yF-0.4,yB+0.2,z0,z1)
    wk=wk.fuse(zbox(30.2,38.6,yF-0.4,14.6,z0,z1))
    wk=wk.fuse(zbox(30.2,32.4,14.6,40,z0,z1))
    g3=Part.Face(Part.makePolygon([V(32.4,20,z0),V(32.4,40,z0),V(37.4,40,z0),V(32.4,20,z0)])).extrude(V(0,0,z1-z0))
    wk=wk.fuse(g3)
    wk=wk.cut(zbox(31.0,32.0,yb-0.75,14.0,z0-1,z1+1)).cut(zbox(30.2,32.0,yB+0.2,yb-0.75,z0-1,z1+1))
    nub=Part.Face(Part.makePolygon([V(30.2,yb-0.75,zc-0.5),V(29.85,yb,zc-0.5),V(29.85,yb+0.5,zc-0.5),V(30.2,yb+0.75,zc-0.5),V(30.2,yb-0.75,zc-0.5)])).extrude(V(0,0,1.0))
    parts.append(wk.fuse(nub).cut(dsw))
parts.append(boss.fuse(sarm))
# keep everything inside clear of the back plate: clip at 1.4 mm in front of the back face
clipF=toF(wslab(-100,SPLIT-0.2))
inner=parts[0]
for p in parts[1:]: inner=inner.fuse(p)
inner=inner.common(outerF).common(clipF)
body=fuse_ok(body,inner)
print("after inner valid",body.isValid())
# ---------- cap (world) ----------
cap=ow.common(wslab(SPLIT,DB+1)).cut(iw)
lips=None
for x0,x1 in LIPX+TABX:
    for zs in (1,-1):
        l=lipring.common(zbox(x0,x1,SPLIT-LIPD-1,SPLIT+1,0,zs*30))
        lips=l if lips is None else lips.fuse(l)
for x0,x1 in [(-38.5,-36.0)]:                   # far-end lip (middle of the end wall; the FPC is at the front)
    lips=lips.fuse(lipring.common(zbox(x0,x1,SPLIT-LIPD-1,SPLIT+1,-6,6)))
zin=IWH/2-LCLR                                  # tab outer face |z|
c=SPLIT-TABL+1.0                                # catch face (world y)
for x0,x1 in TABX:
    for zs in (1,-1):
        tab=zbox(x0,x1,SPLIT+0.01,SPLIT-TABL,zs*zin,zs*(zin-LIPT))
        hk=Part.Face(Part.makePolygon([V(x0,c,zs*zin),V(x0,c,zs*(zin+LCLR+TH)),V(x0,c-0.9,zs*zin),V(x0,c,zs*zin)])).extrude(V(x1-x0,0,0))
        lips=lips.fuse(tab).fuse(hk)
cap=fuse_ok(cap,lips)
# ---------- body (world) ----------
bw=toW(body)
bw=bw.cut(wslab(SPLIT,DB+5))
for x0,x1 in TABX:                              # pockets in the wall the hooks click into (wall stays 1.2 thick)
    for zs in (1,-1):
        bw=bw.cut(zbox(x0-0.3,x1+0.3,c+0.05,c-1.3,zs*(zin-0.5),zs*(zin+LCLR+TH+0.15)))
# clear the lips' path and the tabs' flex room through any internal part
for x0,x1 in LIPX+TABX:
    for zs in (1,-1):
        zz=zbox(x0-0.2,x1+0.2,SPLIT-TABL-0.2,SPLIT,zs*(zin-LIPT-0.8),zs*(zin+0.05)) if (x0,x1) in TABX else zbox(x0-0.2,x1+0.2,SPLIT-LIPD-0.2,SPLIT,zs*(zin-LIPT-0.15),zs*(zin+0.05))
        bw=bw.cut(zz)
bw=bw.cut(zbox(-38.7,-35.8,SPLIT-LIPD-0.2,SPLIT,-6.2,6.2).common(rr_world(IWW,IWH,IWR,SPLIT-10,11)))
# pry notch at the bottom of the seam
bw=bw.cut(zbox(-4,4,SPLIT-0.8,SPLIT+0.1,-H/2-1,-H/2+WALL+0.1))
body=toF(bw)
body=body.cut(slot).cut(win).cut(hole).cut(tun)
for px in(-11.15,11.15):
    bp=P(px,-3.35,-30.3)
    body=body.cut(Part.makeCylinder(0.8,12,V(31.5,bp.y,bp.z),V(1,0,0)))
_c=body.removeSplitter(); body=_c if _c.isValid() else body
print("body valid",body.isValid())
cap=cap.removeSplitter()
plate=toF(cap)
print("cap valid",plate.isValid(),"vol",round(plate.Volume,1))

# ---------- checks ----------
sol=pnF.Solids
def vol(a,b):
    try: return round(a.common(b).Volume,3)
    except Exception as e: return str(e)
def hits(sh,name):
    t=0
    for x in sol:
        if sh.BoundBox.intersect(x.BoundBox):
            v=sh.common(x).Volume
            if v>0.005: print("  %s hits panel part %.3f"%(name,v),x.BoundBox); t+=v
    return round(t,3)
print("panel x body:",hits(body,"body"))
print("knob x body:",vol(knob,body),"pin x body (0: printed hole comes out ~0.25 small = press fit):",vol(pin,body),"bat x body:",vol(bat,body))
print("knob x panel:",hits(knob,"knob"),"bat x panel:",hits(bat,"bat"),"plate x panel:",hits(plate,"plate"))
_ov=plate.common(body); print("  plate/body overlap at",[ (round(x.Volume,3),x.BoundBox) for x in _ov.Solids])
b=pnF.copy(); b.translate(V(0,12,0)); print("  board path hit at dy12:",[(round(bodyNS.common(x).Volume,3),bodyNS.common(x).BoundBox) for x in b.Solids if bodyNS.BoundBox.intersect(x.BoundBox) and bodyNS.common(x).Volume>0.01]) if False else None
print("plate x body (should be 0; hooks touch only):",vol(plate,body),"plate x bat:",vol(plate,bat),"plate x pin:",vol(plate,pin),"plate x knob:",vol(plate,knob))
print("tunnel x body:",vol(tun,body))
print("glass to front wall gap:",round(min(body.distToShape(x)[0] for x in sol if x.Volume>1300 and x.Volume<1400),3))
print("pads to board front:",round(min(body.common(zbox(-25,23,FW,yF+0.01,14,16)).distToShape(brd)[0],body.common(zbox(-25,23,FW,yF+0.01,-16,-14)).distToShape(brd)[0]),3))
# board insertion: slide the board in from the back along F-y; only the 4 snap hooks may touch it
snapzone=None
for x0,x1 in SNAPX:
    z=zbox(x0-0.1,x1+0.1,yB-1,ROOT,14.9,17); z=z.fuse(z.mirror(V(0,0,0),V(0,0,1)))
    snapzone=z if snapzone is None else snapzone.fuse(z)
pnl=pnF.copy()
bodyNS=body.cut(snapzone)
ins=[]
for dy in (0.3,2,5,10,15,20,25,30):
    b=pnl.copy(); b.translate(V(0,dy,0)); ins.append(round(sum(bodyNS.common(x).Volume for x in b.Solids if bodyNS.BoundBox.intersect(x.BoundBox)),2))
print("board path from back (non-snap) x body:",ins)
b=pnl.copy(); b.translate(V(0,12,0))
for x in b.Solids:
    if bodyNS.BoundBox.intersect(x.BoundBox):
        c=bodyNS.common(x)
        if c.Volume>0.01: print("  board path hit at dy12",round(c.Volume,3),c.BoundBox)
hk=[]
for dy in (0,0.5,1.0,1.5):
    b=brd.copy(); b.translate(V(0,dy,0)); hk.append(round(body.common(b).Volume,3))
print("board vs snap hooks at dy 0/0.5/1/1.5 (0 seated, >0 while clicking in):",hk)
hd=[]
for dz in (0.3,0.5,0.75):
    t=body.common(snapzone)
    hd.append(round(t.common(brd).Volume,3))
# drum: drop in from the back at the left, slide right
dp=[]
for dy in (16,12,8,4,2,0):
    k=knob.copy(); k.translate(V(29.0-(AX.x+RD),dy,0)); dp.append(round(k.common(body).Volume,2))
for dx in (0,4,8,12,(AX.x+RD-29.0)):
    k=knob.copy(); k.translate(V(29.0-(AX.x+RD)+dx,0,0)); dp.append(round(k.common(body).Volume,2))
print("drum drop+slide x body:",dp)
pp=[]
for dy in (20,10,5,2,0):
    p=pin.copy(); p.translate(V(0,dy,0)); pp.append(round(p.common(body.cut(boss)).Volume,2))
print("pin path from back (outside boss) x body:",pp)
pt=[]
for dy in (25,15,8,4,0.2):
    p=plate.copy(); p.translate(V(0,0,0)); q=toW(plate); q.translate(V(0,dy,0)); pt.append(round(toF(q).common(body).Volume,3))
print("plate going in (world y +25..+0.2) x body:",pt)
kb=toW(knob).BoundBox; bb=toW(body).BoundBox
print("world body bbox %.1f x %.1f x %.1f"%(bb.XLength,bb.YLength,bb.ZLength),"drum juts %.1f"%(kb.XMax-bb.XMax))
print("cap inner face to battery back (world y):",round(DB-WALL-toW(bat).BoundBox.YMax,2))
if not os.environ.get("CHECK"):
    for n,sh in [('body',body),('back_cap',plate),('drum',knob),('pin',pin)]:
        toW(sh).exportStep(OUT+n+'.step')
    for n,sh in [('body',body),('plate',plate),('knob',knob),('pin',pin),('bat',bat),('panel',pnF)]:
        sh.exportBrep('build/ccF_'+n+'.brep'); toW(sh).exportBrep('build/cc_'+n+'.brep')
    print("SAVED")
sys.stdout.flush()
