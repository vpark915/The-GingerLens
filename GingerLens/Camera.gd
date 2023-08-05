extends Camera


# Declare member variables here. Examples:
var controller_node


# Called when the node enters the scene tree for the first time.
func _ready():
	controller_node = get_node("..") # Replace with the actual path to your Script1 node


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if controller_node and controller_node.sensorData != null:
		var sensor_data = controller_node.sensorData
		rotation = Vector3(deg2rad(-1*sensor_data[1]),deg2rad(-1*sensor_data[0]),deg2rad(-1*sensor_data[2]))
