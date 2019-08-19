import bpy
import bmesh
import mathutils
import os

obj = bpy.context.active_object

bm = bmesh.from_edit_mesh(obj.data)
sel_verts = [ vert for vert in bm.verts if vert.select ]
print("number of verts: {}".format(len(sel_verts)))

path = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(path,
                        'scripts',
                        "%s_dump.tab" % obj.name)
f = open(file_path, 'w')
for v in sel_verts:   
    row = "%s\t%s\t%s\t%s\n" % (v.index,
                                v.co.x,
                                v.co.y,
                                v.co.z)
    f.write(row)
f.close()

And to restore:

import bpy
import bmesh
import os

obj = bpy.context.active_object
path = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(path,
                        'scripts',
                        "%s_dump.tab" % obj.name)
f = open(file_path)

verts = {}

for line in f:
    (index, x, y, z) = line.strip().split("\t")
    verts[int(index)] = { 'x': float(x),
                          'y': float(y),
                          'z': float(z) }

bm = bmesh.from_edit_mesh(obj.data)
for v in bm.verts:
  if v.index in verts:
      vv = verts[v.index]
      v.co.x = vv['x']
      v.co.y = vv['y']
      v.co.z = vv['z']

bmesh.update_edit_mesh(obj.data, True)
