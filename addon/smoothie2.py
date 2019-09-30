bl_info = {
	"name": "smoothie2",
	"category": "Mesh",
}

import bpy
import bmesh

from mathutils import *


class smoothie2(bpy.types.Operator):
	"""smoothie2"""
	bl_idname = "mesh.smoothie2"
	bl_label = "smoothie2"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bm = self.get_bm(context)
		if not bm :
			return {'CANCELLED'}
			
		lens    = [None] * len(bm.edges) # cached edge lengths
		floods  = [None] * len(bm.verts) # flood fill weight calculation
		weights = [None] * len(bm.verts) # weighted xyz/w position for each vertex
		normals = [None] * len(bm.verts) # weighted xyz/w normal for each vertex

		'''
# calculate our own vertex normals
		for vw in bm.verts:
			if not vw.select :
				n=Vector((0,0,0,0))
				for f in vw.link_faces :
					valid = True
					for v in f.verts :
						if v.select :
							valid = False
					if valid :
						n+=Vector((f.normal.x,f.normal.y,f.normal.z,1))
				if n.w>0 :
					normals[vw.index]=Vector((n.x,n.y,n.z))/n.w
					normals[vw.index].normalize()
				else :
					normals[vw.index]=Vector((0,0,0))

		for v in bm.verts:
			if normals[v.index]:
				v.normal=normals[v.index]
			else:
				v.normal=Vector((0,0,0))

#		self.set_bm(context,bm)
#		return {'FINISHED'}
		'''

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
						vo = vw.co + vw.normal*(v.co-vw.co).length*f/2
						weights[v.index]+=Vector((vo.x,vo.y,vo.z,1))*(1.0/(f*f*f))

# apply all weights to find new vertex location
		for v in bm.verts:
			a=weights[v.index]
			if v.select :
				if a.w!=0 :
					v.co=Vector((a.x,a.y,a.z))/a.w

		bm.normal_update()
		self.set_bm(context,bm)
		
		return {'FINISHED'}


		bm.normal_update()
# init

		for vw in bm.verts:
			if vw.select :
				normals[vw.index]=Vector((0,0,0,0))
			else:
				normals[vw.index]=Vector((vw.normal.x,vw.normal.y,vw.normal.z,1))

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
						normals[v.index]+=Vector((vw.normal.x,vw.normal.y,vw.normal.z,1))*(1.0/(f*f*f))

# apply all weights to find new vertex location
		for v in bm.verts:
			n=normals[v.index]
			if n.w!=0 :
				normals[v.index]=Vector((n.x,n.y,n.z))/n.w
				normals[v.index].normalize()
			else:
				normals[v.index]=Vector((0,0,0))

# make sure normals are fixed

		for v in bm.verts:
			weights[v.index]=Vector((0,0,0,0))
			floods[v.index]=not v.select


		active=True
		while active :
			active=False
			for e in bm.edges:
				for ia in range(2): # flip flop
					va=e.verts[ia]
					vb=e.verts[(ia+1)%2]
					if floods[va.index] and (not floods[vb.index]) : # build vb from va
						
						n = normals[vb.index]
						d = n.dot(va.co-vb.co)
						vo = n*d + vb.co

#						vl = vb.co-va.co
#						na = normals[va.index]
#						nb = normals[vb.index]
#						vc = na.cross(vl)
#						vd = vc.cross(nb)
#						vd.normalize()
#						d=vl.length
#						vo = vd*d + va.co

						weights[vb.index]+=Vector((vo.x,vo.y,vo.z,1))
						active=True

			for v in bm.verts:
				a=weights[v.index]
				if not floods[v.index] and a.w > 0 :
					v.co=Vector((a.x,a.y,a.z))/a.w
					floods[v.index]=True




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
	self.layout.operator(smoothie2.bl_idname)


def register():
	bpy.utils.register_class(smoothie2)
#	bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)

def unregister():
#	bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
	bpy.utils.unregister_class(smoothie2)


if __name__ == "__main__":
	register()
