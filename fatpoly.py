
from pathlib import Path

base_path = Path(__file__).parent


for name in ("smoothie.py") :

	filepath=(base_path / "smoothie.py").resolve()
	print( filepath )

	global_namespace = {"__file__": filepath, "__name__": "__main__"}
	with open(filepath, 'rb') as file:
		exec(compile(file.read(), filepath, 'exec'), global_namespace)
    
    
