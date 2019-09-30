
from pathlib import Path

base_path = Path(__file__).parent


print( "LOADING FATPOLY" )

for name in ("smoothie1.py","smoothie2.py") :

	filepath=(base_path / name).resolve()
	print( filepath )

	global_namespace = {"__file__": filepath, "__name__": "__main__"}
	with open(filepath, 'rb') as file:
		exec(compile(file.read(), filepath, 'exec'), global_namespace)
    
    
print( "LOADED FATPOLY" )
