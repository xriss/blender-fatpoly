bl_info = {
	"name": "flatop",
	"category": "Mesh",
}

import bpy
import bmesh

from mathutils import *


class flatop(bpy.types.Operator):
	"""flatop"""
	bl_idname = "mesh.flatop"
	bl_label = "flatop"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bm = self.get_bm(context)
		if not bm :
			return {'CANCELLED'}
			
		floods  = [None] * len(bm.verts) # flood fill weight calculation
		weights = [None] * len(bm.verts) # weighted xyz/w for each vertex

# init
		for v in bm.verts:
			weights[v.index]=Vector((0,0,0,0))


# process each vertex
		for vw in bm.verts:
# this vertex is locked
			if not vw.select :
# reset flood distance calc for this vertex
				for v in bm.verts:
					floods[v.index]=0x7fffffff
# seed start of flood
				floods[vw.index]=1.0
				active=True
				while active :
					active=False
					for e in bm.edges:
						for ia in range(2): # flip flop
							va=e.verts[ia]
							vb=e.verts[(ia+1)%2]
							if vb.select and floods[vb.index] > floods[va.index]+1 :
								floods[vb.index] = floods[va.index]+1
								active=True
# add weight dependent on edge distance from main vertex
				for v in bm.verts:
					f=floods[v.index]
					if v.select and f<0x7fffffff and f>0 :
						weights[v.index]+=Vector((vw.co.x,vw.co.y,vw.co.z,1))*(1.0/(f*f*f))

# apply all weights to find new vertex location
		for v in bm.verts:
			a=weights[v.index]
			if v.select :
				v.co=Vector((a.x,a.y,a.z))/( a.w==0 and 1 or a.w )
		
# make sure normals are fixed

		bm.normal_update()

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
			bmesh.update_edit_mesh(obj.data, False, False)
		else:
			bm.to_mesh(obj.data)
			obj.data.update()

def menu_func(self, context):
	self.layout.operator(flatop.bl_idname)


def register():
	bpy.utils.register_class(flatop)
	bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)

def unregister():
	bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
	bpy.utils.unregister_class(flatop)


if __name__ == "__main__":
	register()
