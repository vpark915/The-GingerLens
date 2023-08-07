tool
extends Spatial

var thread = Thread.new()
var depth_data  # Your [x,y,z,x,y,z,...] data
var grid_width = 20    # Width of your depth grid (number of points, not actual width in space)
var grid_height = 10   # Height of your depth grid
var vertices
var indices
var scandata

var interpreter_path = "PythonFiles/venv/Scripts/python.exe"
var script_path = "PythonFiles/RsLinearRegressionSimplification.py"

func _ready():
	#scandata = _getRsScan()
	#vertices = scandata[1]
	#print(vertices)
	#indices = scandata[0]
	#create_mesh_from_vertices(vertices,indices)
	OS.execute(interpreter_path, [script_path], true)

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
	while !file.file_exists("PythonFiles/temp/triangle_mmp.txt"):
		yield(get_tree().create_timer(0.01),"timeout")
	file.open("PythonFiles/temp/triangle_mmp.txt", File.READ)
	var content = file.get_as_text()
	file.close()
	var values = content.split(",",false)
	for i in range(0,values.size()):
		triangleArray.append(float(values[i]))
	return triangleArray
	
		
func _readCloudMMP():
	var array = PoolVector3Array()
	var file = File.new()
	while !file.file_exists("PythonFiles/temp/cloud_mmp.txt"):
		yield(get_tree().create_timer(0.01),"timeout")
	file.open("PythonFiles/temp/cloud_mmp.txt", File.READ)
	var content = file.get_as_text()
	file.close()
	var values = content.split(",",false)
	for i in range(0, values.size(), 3):
		var x = float(values[i])/100
		var y = float(values[i + 1])/100
		var z = float(values[i + 2])/100
		array.append(Vector3(x, y, z))
	return array 
	
func _getRsScan():
	OS.execute(interpreter_path, [script_path], true)
	var triangle_array = _readTriangleMMP()
	var cloud_array = _readCloudMMP()
	return [triangle_array,cloud_array]
	
func _on_exit_request():
	var file = File.new()
	if file.open("PythonFiles/terminate.txt", File.WRITE) == OK:
		file.store_line("t")
		file.close()
	if thread.is_active():
		thread.wait_to_finish()

func _basicRsFunc():
	OS.execute(interpreter_path, [script_path, ">", "PythonFiles/output.log", "2>&1"], true)
