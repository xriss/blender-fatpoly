bl_info = {
	"name": "smoothie3",
	"category": "Mesh",
}

import bpy
import bmesh

from mathutils import *


class smoothie3(bpy.types.Operator):
	"""smoothie3"""
	bl_idname = "mesh.smoothie3"
	bl_label = "smoothie3"
	bl_options = {'REGISTER', 'UNDO'}

	steps : bpy.props.IntProperty(name="Steps", default=20, min=1, max=100)

	def execute(self, context):
		bm = self.get_bm(context)
		if not bm :
			return {'CANCELLED'}
			
		lens    = [None] * len(bm.edges) # cached edge lengths
		floods  = [None] * len(bm.verts) # flood fill weight calculation
		weights = [None] * len(bm.verts) # weighted xyz/w position for each vertex
		normals = [None] * len(bm.verts) # weighted xyz/w normal for each vertex

# init
		for vw in bm.verts:
			weights[vw.index]=Vector((0,0,0,0))

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
						vo = vw.co
						weights[v.index]+=Vector((vo.x,vo.y,vo.z,1))*(1.0/(f*f*f))

# apply all weights to find new vertex location
		for v in bm.verts:
			a=weights[v.index]
			if v.select :
				if a.w!=0 :
					v.co=Vector((a.x,a.y,a.z))/a.w

		bm.normal_update()

		for i in range(self.steps):
# init
			for vw in bm.verts:
				weights[vw.index]=Vector((0,0,0,0))
#				weights[vw.index]=Vector((vw.co.x,vw.co.y,vw.co.z,1))*0

# process each vertex
			for va in bm.verts:

# average length of edges
				l=Vector((0,0))
				for e in va.link_edges:
					l+=Vector((e.calc_length(),1))
				l=l.x/(l.y==0 and 1 or l.y)

# push each edge to the same length
				for e in va.link_edges:
					vb=e.other_vert(va)
					if vb.select:
						vc=va.normal.cross(va.co-vb.co)
						vd=va.normal.cross(vc)
						vd.normalize()
						vo= va.co + vd*l
						weights[vb.index]+=Vector((vo.x,vo.y,vo.z,1))
						if va.select:
							vo= vb.co + vd*-l
							weights[va.index]+=Vector((vo.x,vo.y,vo.z,1))

# apply all weights to find new vertex location
			for v in bm.verts:
				a=weights[v.index]
				if v.select :
					if a.w!=0 :
						v.co=Vector((a.x,a.y,a.z))/a.w

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
	self.layout.operator(smoothie3.bl_idname)


def register():
	bpy.utils.register_class(smoothie3)
#	bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)

def unregister():
#	bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
	bpy.utils.unregister_class(smoothie3)


if __name__ == "__main__":
	register()
