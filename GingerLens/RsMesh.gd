extends Spatial

var depth_data  # Your [x,y,z,x,y,z,...] data
var grid_width = 20    # Width of your depth grid (number of points, not actual width in space)
var grid_height = 10   # Height of your depth grid
var vertices = []

func _ready():
	vertices = _readCloudMMP()
	
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
