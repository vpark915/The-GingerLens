#@tool
extends MeshInstance3D

@export var xSize = 20
@export var zSize = 20

@export var update = false 
@export var clear_vert_vis = false
func _ready():
	print("hello")
	generate_terrain()
	
func generate_terrain():
	#MESH DETAILS 
	var a_mesh:ArrayMesh
	var surftool = SurfaceTool.new()
	surftool.begin(Mesh.PRIMITIVE_TRIANGLES)
	
	for z in range(zSize+1):
		for x in range(xSize+1):
			var y = 0 
			surftool.add_vertex(Vector3(x,y,z))
			#draw_sphere(Vector3(x,y,z))
	surftool.add_index(0)
	surftool.add_index(1)
	surftool.add_index(xSize+1)
	
	#COMMIT MESH 
	a_mesh = surftool.commit()
	mesh = a_mesh
	
#func _process(delta):
#	draw_sphere(Vector3(0,0,0))
#	var sprite3d = Sprite3D.new()
#	add_child(sprite3d)

func draw_sphere(pos:Vector3):
	var ins = MeshInstance3D.new()
	add_child(ins)
	ins.position = pos 
	var sphere = SphereMesh.new()
	sphere.radius = 0.1
	sphere.height = 0.2
	ins.mesh = sphere 
