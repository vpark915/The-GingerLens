extends Spatial

var depth_data  # Your [x,y,z,x,y,z,...] data
var grid_width = 20    # Width of your depth grid (number of points, not actual width in space)
var grid_height = 10   # Height of your depth grid

func _ready():
	var mesh = ArrayMesh.new()
	var arrays = []

	for i in range(8):
		arrays.append(PoolVector3Array())

	# Create vertices from depth data
	arrays[0] = _readCloudMMP()

	# Generate triangles (assuming your depth data forms a grid)
	var indices = PoolIntArray()
	for y in range(grid_height - 1):
		for x in range(grid_width - 1):
			# Calculate the index of the current point in the grid
			var idx = x + y * grid_width

			# Two triangles per grid cell
			indices.append(idx, idx + 1, idx + grid_width)
			indices.append(idx + 1, idx + 1 + grid_width, idx + grid_width)

	arrays[7] = indices

	# Apply the arrays to the mesh
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)

	$MeshInstance.mesh = mesh

func _readCloudMMP():
	var array = []
	var file = File.new()
	if file.open("PythonFiles/cloud_mmp.txt", File.READ) == OK:
		var content = file.get_as_text()
		file.close()
		var values = content.split(",",false)
		for i in range(0, values.size(), 3):
			var x = float(values[i])
			var y = float(values[i + 1])
			var z = float(values[i + 2])
			array.append(Vector3(x, y, z))
	else:
		print("Failed to open the file.")
	return array 
