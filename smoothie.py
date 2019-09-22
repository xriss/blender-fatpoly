bl_info = {
	"name": "smoothie",
	"category": "Mesh",
}

import bpy
import bmesh

from mathutils import *


class smoothie(bpy.types.Operator):
	"""smoothie"""
	bl_idname = "mesh.smoothie"
	bl_label = "smoothie"
	bl_options = {'REGISTER', 'UNDO'}

	total: bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)

	def execute(self, context):
		bm = self.get_bm(context)
		if not bm :
			return {'CANCELLED'}

		print(bm)
		
		lens = [] # length of each edge
		aves = [] # smoothed xyz of each vertex

# initialize aves
		for v in bm.verts:
			aves.append( Vector((0,0,0,0)) )
			print(v.index,v.co)

# initialize lens and build smooth aves
		for e in bm.edges:
			lens.append( e.calc_length() )
			for v in e.verts:
				aves[e.verts[0].index]+=Vector((v.co.x,v.co.y,v.co.z,1))
				aves[e.verts[1].index]+=Vector((v.co.x,v.co.y,v.co.z,1))

# apply aves to vertex location ( smooth )
		for v in bm.verts:
			a=aves[v.index]
			v.co=Vector((a.x/a.w,a.y/a.w,a.z/a.w))
			print(v.index,v.co,a)

		for i in range(1,4):
# reset aves
			for v in bm.verts:
				aves[v.index]=Vector((0,0,0,0))

# build spring aves
			for e in bm.edges:
				d=Vector((e.verts[0].co-e.verts[1].co))
				d.normalize()
				d*=((lens[e.index]-e.calc_length())*0.5)
				for v in e.verts:
					aves[e.verts[0].index]+=Vector((d.x,d.y,d.z,1))
					aves[e.verts[1].index]+=Vector((-d.x,-d.y,-d.z,1))


# apply aves to vertex location ( springs )
			for v in bm.verts:
				a=aves[v.index]
				v.co+=Vector((a.x/a.w,a.y/a.w,a.z/a.w))
		
		self.set_bm(context,bm)
		
		return {'FINISHED'}

	def get_bm(self,context):
		obj = context.active_object
		if not obj:
			return
		if obj.type != "MESH" :
			return
		if obj.mode == "EDIT" :
			return bmesh.from_edit_mesh(obj.data)
		else:
			bm = bmesh.new()
			bm.from_mesh(obj.data)
			return bm

	def set_bm(self,context,bm):
		obj = context.active_object
		if not obj:
			return
		if obj.type != "MESH" :
			return
		if obj.mode == "EDIT" :
			bmesh.update_edit_mesh(obj.data, True, True)
		else:
			bm.to_mesh(me)
			me.update()

def menu_func(self, context):
	self.layout.operator(smoothie.bl_idname)


def register():
	bpy.utils.register_class(smoothie)
	bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)

def unregister():
	bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
	bpy.utils.unregister_class(smoothie)


if __name__ == "__main__":
	register()
#	bpy.ops.object.smoothie()
