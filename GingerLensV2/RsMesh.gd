tool
extends Spatial

var depth_data  # Your [x,y,z,x,y,z,...] data
var grid_width = 20    # Width of your depth grid (number of points, not actual width in space)
var grid_height = 10   # Height of your depth grid
var vertices = []
var indices = []

func _ready():
	vertices = _readCloudMMP()
	print(vertices)
	indices = _readTriangleMMP()
	create_mesh_from_vertices(vertices,indices)

#func generate_terrain():
#	#MESH DETAILS 
#	var a_mesh:ArrayMesh
#	var surftool = SurfaceTool.new()
#	surftool.begin(Mesh.PRIMITIVE_TRIANGLES)
#	for depth in range(200):
#		surftool.add_vertex(Vector3(x,y,z))
#	surftool.add_index(0)
#	surftool.add_index(1)
#	surftool.add_index(xSize+1)
#
#	#COMMIT MESH 
#	a_mesh = surftool.commit()
#	mesh = a_mesh

func draw_sphere(pos:Vector3):
	var ins = MeshInstance.new()
	add_child(ins)
	ins.translation = pos 
	var sphere = SphereMesh.new()
	sphere.radius = 0.3
	sphere.height = 0.3
	ins.mesh = sphere 
	
func create_mesh_from_vertices(verts: PoolVector3Array, inds: PoolIntArray):
	var a_mesh:ArrayMesh 
	var surftool = SurfaceTool.new()
	surftool.begin(Mesh.PRIMITIVE_TRIANGLES)
	for depth in verts:
		draw_sphere(depth)
		surftool.add_vertex(depth)
	for index in inds: 
		surftool.add_index(index)
	a_mesh = surftool.commit()
	#get_node("MeshInstance3D").mesh = a_mesh


func _readTriangleMMP():
	var triangleArray = PoolIntArray()
	var file = File.new()
	file.open("PythonFiles/triangle_mmp.txt", File.READ)
	var content = file.get_as_text()
	file.close()
	var values = content.split(",",false)
	for i in range(0,values.size()):
		triangleArray.append(float(values[i]))
	return triangleArray
	
		
func _readCloudMMP():
	var array = PoolVector3Array()
	var file = File.new()
	file.open("PythonFiles/cloud_mmp.txt", File.READ)
	var content = file.get_as_text()
	file.close()
	var values = content.split(",",false)
	for i in range(0, values.size(), 3):
		var x = float(values[i])/100
		var y = float(values[i + 1])/100
		var z = float(values[i + 2])/100
		array.append(Vector3(x, y, z))
	return array 
