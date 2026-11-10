import Part
from FreeCAD import Vector as V
d='build/'
def L(n):
    s=Part.Shape(); s.read(d+'ccF_%s.brep'%n); return s
b=L('body'); k=L('knob'); o=L('oring')
for dx in (1.0,1.5,1.8):
    kk=k.copy(); kk.translate(V(dx,0,0)); oo=o.copy(); oo.translate(V(dx,0,0))
    print('deflect',dx,'knob x body',round(kk.common(b).Volume,3),'oring x body',round(oo.common(b).Volume,3))
oo=o.copy(); oo.translate(V(1.5,0,0)); c=oo.common(b); print('deflect hit bbox',c.BoundBox)
print('deflect oring true xmax', round(o.optimalBoundingBox().XMax,3), 'knob xmax', round(k.optimalBoundingBox().XMax,3))
