bl_info = {
	"name": "test2",
	"category": "Mesh",
}

import bpy
import bmesh


class test2(bpy.types.Operator):
	"""test2"""
	bl_idname = "mesh.test2"
	bl_label = "test2"
	bl_options = {'REGISTER', 'UNDO'}

	total: bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)

	def execute(self, context):
		bm = self.get_bm(context)
		if not bm :
			return {'CANCELLED'}

		print(bm)

		return {'FINISHED'}

	def get_bm(self,context):
		obj = context.active_object
		if not obj:
			return
		if obj.mode == "EDIT" and obj.type == "MESH":
			return bmesh.from_edit_mesh(obj.data)

def menu_func(self, context):
	self.layout.operator(test2.bl_idname)


def register():
	bpy.utils.register_class(test2)
	bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)

def unregister():
	bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
	bpy.utils.unregister_class(test2)


if __name__ == "__main__":
	register()
