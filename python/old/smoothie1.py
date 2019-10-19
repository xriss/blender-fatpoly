bl_info = {
	"name": "smoothie1",
	"category": "Mesh",
}

import bpy
import bmesh

from mathutils import *


class smoothie1(bpy.types.Operator):
	"""smoothie1"""
	bl_idname = "mesh.smoothie1"
	bl_label = "smoothie1"
	bl_options = {'REGISTER', 'UNDO'}

	x : bpy.props.IntProperty()
	y : bpy.props.IntProperty()
    
	steps : bpy.props.IntProperty(name="Steps", default=1, min=1, max=100)

	def invoke(self, context, event):
		self.x = event.mouse_x
		self.y = event.mouse_y
		return self.execute(context)

	def execute(self, context):
		bm = self.get_bm(context)
		if not bm :
			return {'CANCELLED'}
			
		self.report({'INFO'}, "Mouse coords are %d %d" % (self.x, self.y))


		lens = [] # length of each edge
		aves = [] # smoothed xyz of each vertex
		
# average centre of verts

		center=Vector((0,0,0,0))
		for v in bm.verts:
			center+=Vector((v.co.x,v.co.y,v.co.z,1))
		center=Vector((center.x/center.w,center.y/center.w,center.z/center.w))

		size=0.0
		count=0.0
		for v in bm.verts:
			if v.select :
				size+=(v.co-center).length
				count+=1.0
		if count==0 : count=1
		startsize=size/count

# initialize lists outside of the main loop
		for e in bm.edges:
			lens.append( e.calc_length() )
#			lens.append( startsize/1024.0 )
		for v in bm.verts:
			aves.append( Vector((0,0,0,0)) )

		for i in range(self.steps):

# initialize aves
			for v in bm.verts:
#				aves[v.index]+=Vector((v.co.x,v.co.y,v.co.z,1))
				aves[v.index]=Vector((0,0,0,0))

# build smooth aves
			for e in bm.edges:
				for ia in range(2):
					ib=(ia+1)%2
					va=e.verts[ia]
					vb=e.verts[ib]
					vc=va.normal.cross(vb.co-va.co)
					vd=va.normal.cross(vc)
					vd.normalize()
					vd*=(vb.co-va.co).length
					vd+=va.co
					aves[vb.index]+=Vector((vd.x,vd.y,vd.z,1))
#					aves[vb.index]+=Vector((vb.co.x,vb.co.y,vb.co.z,1))

				for v in e.verts:
					aves[e.verts[0].index]+=Vector((v.co.x,v.co.y,v.co.z,1))
					aves[e.verts[1].index]+=Vector((v.co.x,v.co.y,v.co.z,1))
#				aves[e.verts[0].index]+=Vector((e.verts[1].co.x,e.verts[1].co.y,e.verts[1].co.z,1))
#				aves[e.verts[1].index]+=Vector((e.verts[0].co.x,e.verts[0].co.y,e.verts[0].co.z,1))

# apply aves to vertex location ( smooth )
			for v in bm.verts:
				a=aves[v.index]
				if v.select :
					v.co=Vector((a.x/a.w,a.y/a.w,a.z/a.w))

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
#				if v.select :
#					v.co+=Vector((a.x/a.w,a.y/a.w,a.z/a.w))
		
# make sure normals are fixed

			bm.normal_update()


# try and keep the vert cloud the sameish size

		size=0.0
		count=0.0
		for v in bm.verts:
			if v.select :
				size+=(v.co-center).length
				count+=1.0
		if count==0 : count=1
		size=size/count
		resize=startsize/size
#		for v in bm.verts:
#			if v.select :
#				v.co=((v.co-center)*resize)+center

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
	self.layout.operator(smoothie1.bl_idname)


def register():
	bpy.utils.register_class(smoothie1)
#	bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)

def unregister():
#	bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
	bpy.utils.unregister_class(smoothie1)


if __name__ == "__main__":
	register()
#	bpy.ops.object.smoothie1()
