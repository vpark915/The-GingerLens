extends RigidBody

var thread = Thread.new()
var udp_server = PacketPeerUDP.new()
var listening_port = 12345
var IMUFunc = false
var StartupCount = 0 

var sensorData
var BNOPID 

func _ready():
	udp_server.listen(12345)
	set_process(true)

func _physics_process(delta):
	if udp_server.get_available_packet_count() > 0:
		#IMU Function 
		var packet = udp_server.get_packet()
		var data = packet.get_string_from_utf8()
		var data_array = parse_json(data)
		#print(data_array)
		var camera_force = Vector3(data_array[1],data_array[2],data_array[0])
		#add_central_force(camera_force)
		linear_velocity = camera_force
		#print(camera_force)
		print(global_transform.origin)
