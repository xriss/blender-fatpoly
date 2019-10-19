
To install the Fatpoly add-on, first download this zip file

https://github.com/xriss/blender-fatpoly/raw/releases/fatpoly.zip

Run Blender and go to user preferences and open the add-ons tab.

Click Install add-on from file and choose this zip file.

Finally you must check the box next to Fatpoly to enable this addon.


To use hit F3 and type fatpoly and you should see "Fatpoly Smoothie" as 
an available mesh tool.


## Fatpoly Smoothie

This mesh tool will perform a mass spring system style smoothing of the 
selected vertexes using the unselected vertexes as immovable anchor 
points and the edges as the springs.

It is best not to select the entire mesh, although this will work it 
will behave similar to the normal blender smooth slowly shrinking the 
mesh every time is is run as there is nothing to anchor the solution 
and no initial topology coordinates can be generated from fixed anchor 
points.

Ideally most of the mesh will remain unselected and only whole polygons 
( not edges or vertexes ) should be selected, this helps to keep the 
simulation stable and will stop edges twisting or inverting.

For instance select the cheek area of a face and "Fatpoly Smoothie" 
will use the surrounding normals and tangents as well as the topology 
of the area selected to create a smooth solution to the surface. The 
initial starting point of these vertexes is ignored, only the location 
of the surrounding unselected vertexes are taken into account. This 
means that we will come to the same stable solution every time we are 
run. Picture it as if the surrounding polygons are control points on a 
bezier surface.

	Boost = 0.10 
		This gives the initial topology coordinates solution a gentle 
		push outwards to help prevent inverted solutions. Ideally this 
		should be a small value but not 0.
		
		Best to leave this value alone.
		
	Steps = 32
		The number of iterations to try and solve the spring system, if 
		set to 0 then only the initial topology solution is performed. 
		This initial state will generally be a flat plane with a low 
		boost and an ugly bump with a higher boost. Each step from this 
		state will create a more pleasing solution but the higher this 
		number is the slower the code runs.

		Best to leave this value alone.
		
	Boom = 0.75
		This adjusts the length of all springs used in the system, as 
		the springs increase in length so the polygons will push 
		outward like a blister and visa versa.
		
		This is a value you can tweak up and down until you are 
		happy with the results.

	Blend = 1.0
		Blend from initial coordinates of vertex to the new smoothed 
		coordinate. This allows you to perform only a partial smooth 
		from the stating coordinates.

		Although best left at 1.0 you may want to tweak this value up 
		and down to blend to and from the smoothed state. 
