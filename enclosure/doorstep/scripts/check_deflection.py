# Drum vs body when the springy arm deflects toward the wheel end (pressing the drum)
import Part
from FreeCAD import Vector as V
d='build/'
def L(n):
    s=Part.Shape(); s.read(d+'ccF_%s.brep'%n); return s
b=L('body'); k=L('knob')
for dx in (1.0,1.5,1.8):
    kk=k.copy(); kk.translate(V(dx,0,0))
    print('deflect',dx,'knob x body',round(kk.common(b).Volume,3))
