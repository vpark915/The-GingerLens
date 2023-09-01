#tool
extends Spatial

var pythread = Thread.new()
var vertices
var indices
var scandata

var interpreter_path = "PythonFiles/venv/Scripts/python.exe"
var script_path = "PythonFiles/RsFasterRead.py"

#func _ready():
	#pythread.start(self,"_getRsScan")
	#_basicRsFunc()

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
		#surftool.add_vertex(depth)
	#for index in inds: 
		#surftool.add_index(index)
	#a_mesh = surftool.commit()
	#get_node("MeshInstance3D").mesh = a_mesh

func _create_mesh_node(pos:Vector3):
	var new_spatial = Spatial.new()
	new_spatial.transform.origin = Vector3(pos)
	add_child(new_spatial)

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
	#var relative = get_node("../RigidBody/Camera").rotation_degrees
	#print(relative)
	OS.execute(interpreter_path, [script_path], true)
	var triangle_array = _readTriangleMMP()
	var cloud_array = _readCloudMMP()
	create_mesh_from_vertices(cloud_array,triangle_array)
	#self.rotation_degrees = Vector3(-1*relative.x,0,-1*relative.z)
	return
	
func _on_exit_request():
	var file = File.new()
	if file.open("PythonFiles/terminate.txt", File.WRITE) == OK:
		file.store_line("t")
		file.close()
	if pythread.is_active():
		pythread.wait_to_finish()

