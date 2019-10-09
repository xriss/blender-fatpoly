bl_info = {
	"name": "fatpoly_smoothie",
	"category": "Mesh",
}

import bpy
import bmesh

from mathutils import *


class fatpoly_smoothie(bpy.types.Operator):
	"""fatpoly_smoothie"""
	bl_idname = "mesh.fatpoly_smoothie"
	bl_label = "fatpoly_smoothie"
	bl_options = {'REGISTER', 'UNDO'}

	boost : bpy.props.FloatProperty(name="Boost", default=0.1, min=0, max=1)
	steps : bpy.props.IntProperty(name="Steps", default=32, min=0, max=128)
	boom : bpy.props.FloatProperty(name="Boom", default=0.75, min=0.01, max=1)


	def cousin_verts(va):

		l=[]
# get all verts in linked faces
		for f in va.link_faces:
			for vb in f.verts:
				if va.index!=vb.index :
					l.append(vb)

# remove dupes
#		l=list(dict.fromkeys(l))

		return l

	def brother_verts(va):

		l=[]
# get all verts in linked faces
		for e in va.link_edges:
			l.append( e.other_vert(va) )

# remove dupes
		l=list(dict.fromkeys(l))

		return l


	def execute(self, context):
		bm = self.get_bm(context)
		if not bm :
			return {'CANCELLED'}
			
		lens    = [None] * len(bm.verts) # desired length for each vertex
		floods  = [None] * len(bm.verts) # flood fill weight calculation
		weights = [None] * len(bm.verts) # weighted xyz/w position for each vertex

# init
		for va in bm.verts:
			weights[va.index]=Vector((0,0,0,0))

			l=Vector((0,0))
			for vb in fatpoly_smoothie.brother_verts(va):
				if not va.select and not vb.select : # fixed lengths only
					l+=Vector(( (va.co-vb.co).length,1))
			l=l.x/( (l.y==0) and 1 or l.y)
			lens[va.index]=l*self.boom

# special case if all mesh is selected
		allselect=True
		for v in bm.verts:
			if not v.select :
				allselect=False
				break
		if allselect :
			l=Vector((0,0))
			for e in bm.edges:
				l+=Vector(( e.calc_length(),1))
			l=l.x/( (l.y==0) and 1 or l.y)
			for v in bm.verts:
				lens[va.index]=l*self.boom
			
# prebuild lens as weighted distance from fixed lens
# init
		for vw in bm.verts:
			weights[vw.index]=Vector((0,0))

# process each vertex
		for vw in bm.verts:
# this vertex has a len
			if lens[vw.index]!=0 :
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
							if lens[vb.index]==0 and floods[vb.index] > floods[va.index]+1 :
								floods[vb.index] = floods[va.index]+1
								active=True
# add weight dependent on edge distance from main vertex
				for v in bm.verts:
					f=floods[v.index]
					if lens[v.index]==0 and f<0x7fffffff and f>0 :
						weights[v.index]+=Vector((lens[vw.index],1))*(1.0/(f*f*f))

# apply all weights to find new vertex length
		for v in bm.verts:
			a=weights[v.index]
			if lens[v.index]==0 :
				if a.y!=0 :
					lens[v.index]=a.x/a.y

# Create a stable fixed mesh based on topology to start with
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


# Apply a normal boot to this stable mesh
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
						vo = v.co + vw.normal*(v.co-vw.co).length*f*self.boost
						weights[v.index]+=Vector((vo.x,vo.y,vo.z,1))*(1.0/(f*f*f))

# apply all weights to find new vertex location
		for v in bm.verts:
			a=weights[v.index]
			if v.select :
				if a.w!=0 :
					v.co=Vector((a.x,a.y,a.z))/a.w

		bm.normal_update()

# Perform spring solution of mesh to create smoothie result

		for i in range(self.steps):
# init
			for va in bm.verts:
				weights[va.index]=Vector((0,0,0,0))

# process each vertex
			for va in bm.verts:

# average length of edges
				l=Vector((0,0))
				for vb in fatpoly_smoothie.cousin_verts(va):
					l+=Vector(( (va.co-vb.co).length,1))
				l=l.x/( (l.y==0) and 1 or l.y)
				
				l=lens[va.index]

# push each edge to the same length
				for vb in fatpoly_smoothie.cousin_verts(va):
					vc=va.normal.cross(va.co-vb.co)
					vd=va.normal.cross(vc)
					vd.normalize()
					if vb.select:
						vo= va.co + vd*l
						weights[vb.index]+=Vector((vo.x,vo.y,vo.z,1))*3 # CHAOS
					if va.select:
						vo= vb.co + vd*-l
						weights[va.index]+=Vector((vo.x,vo.y,vo.z,1)) # ORDER

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
	self.layout.operator(fatpoly_smoothie.bl_idname)


def register():
	bpy.utils.register_class(fatpoly_smoothie)
#	bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)

def unregister():
#	bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
	bpy.utils.unregister_class(fatpoly_smoothie)


if __name__ == "__main__":
	register()
