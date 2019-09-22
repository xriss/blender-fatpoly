bl_info = {
	"name": "smoothie",
	"category": "Mesh",
}

import bpy
import bmesh


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

		for v in bm.verts:
			v.co.x += 1.00
		
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
