import Mesh, zipfile
D='print-ready/'
names=['doorstep_body_white','doorstep_slope_front_white','latch_drum_orange','latch_pin_orange']
objs=[];items=[]
for i,n in enumerate(names,1):
    m=Mesh.Mesh(D+n+'.stl'); pts,fac=m.Topology
    v=''.join('<vertex x="%.4f" y="%.4f" z="%.4f"/>'%(p.x,p.y,p.z) for p in pts)
    t=''.join('<triangle v1="%d" v2="%d" v3="%d"/>'%f for f in fac)
    objs.append('<object id="%d" name="%s" type="model"><mesh><vertices>%s</vertices><triangles>%s</triangles></mesh></object>'%(i,n,v,t))
    items.append('<item objectid="%d"/>'%i)
model='<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>%s</resources><build>%s</build></model>'%(''.join(objs),''.join(items))
with zipfile.ZipFile(D+'doorstep_slope_plate.3mf','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    z.writestr('3D/3dmodel.model',model)
print('ok')
