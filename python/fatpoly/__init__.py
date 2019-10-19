bl_info = {
	"name": "FatPoly",
	"category": "Mesh",
	"version": (0, 1),
	"blender": (2, 80, 0),
}


from . import fatpoly_smoothie



def register():
	fatpoly_smoothie.register()



def unregister():
	fatpoly_smoothie.unregister()



if __name__ == "__main__":
	register()


