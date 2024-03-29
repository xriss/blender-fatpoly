
import bpy

from pathlib import Path

base_path = Path(__file__).parent

#base_path = Path("/home/kriss/git/blender-fatpoly/python")

bpy.ops.script.reload()

print( "LOADING FATPOLY" )

for name in ( "fatpoly/fatpoly_smoothie.py" , "" ) :
	if name :
		filepath=(base_path / name).resolve()
		print( filepath )

		global_namespace = {"__file__": filepath, "__name__": "__main__"}
		with open(filepath, 'rb') as file:
			exec(compile(file.read(), filepath, 'exec'), global_namespace)
		
    
print( "LOADED FATPOLY" )
