#tool
extends Node

# Declare member variables here. Examples:



# Called when the node enters the scene tree for the first time.
func _ready():
	_create_render_instance()


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass

func _create_render_instance():
	#Create a new thread 
	var pythread = Thread.new()
	
	#Retrieve the right local positions 
	var script = load("RsRender.gd")
	var tempLoc = get_node("../RigidBody").translation
	var tempAng = get_node("../RigidBody/Camera").rotation_degrees 
	
	#Create the new node 
	var render_node = Spatial.new()
	render_node.translation = tempLoc
	render_node.rotation_degrees = Vector3(-1*tempAng.x,0,-1*tempAng.z)
	render_node.set_script(script)
	self.add_child(render_node)
	
	#Run the display function 
	pythread.start(render_node,"_getRsScan")
	
