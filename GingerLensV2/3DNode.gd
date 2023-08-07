#tool
extends Spatial

var thread = Thread.new()
var udp_server = PacketPeerUDP.new()
var listening_port = 12345


#Python Scripts 
var interpreter_path = "PythonFiles/venv/Scripts/python.exe"
var script_path = "PythonFiles/BNO055Read.py"

var sensorData
var BNOPID 

func _ready():
	#THREADING AND SERVER CODE 
	thread.start(self, "_run_python_script")
	#udp_server.connect_to_host("127.0.0.1",12345) # 4242 is the port number
	udp_server.listen(12345)
	set_process(true)

func _process(delta):
	#print(udp_server.get_available_packet_count())
	if udp_server.get_available_packet_count() > 0:
		var packet = udp_server.get_packet()
		var data = packet.get_string_from_utf8()
		var data_array = parse_json(data)
		#print(data_array)
		var camera_angle = Vector3(data_array[1],data_array[0],data_array[2])
		get_node("Camera").rotation_degrees = camera_angle


func _run_python_script():
	OS.execute(interpreter_path, [script_path], false)


func _on_exit_request():
	var file = File.new()
	if file.open("PythonFiles/terminate.txt", File.WRITE) == OK:
		file.store_line("t")
		file.close()
	if thread.is_active():
		thread.wait_to_finish()
	udp_server.close()
		
func _notification(what):
	if what == MainLoop.NOTIFICATION_WM_QUIT_REQUEST:
		_on_exit_request()
