extends Node3D

var thread = Thread.new()
var udp_server = PacketPeerUDP.new()


#Python Scripts 
var interpreter_path = "PythonFiles/venv/Scripts/python.exe"
var script_path = "PythonFiles/BNO055Read.py"

var sensorData
var BNOPID 

func _ready():
	#THREADING AND SERVER CODE 
	thread.start(Callable(self, "_run_script").bind([interpreter_path,script_path]))
	udp_server.listen(12345) # 4242 is the port number
	set_process(true)

func _process(delta):
	if udp_server.get_available_packet_count() > 0:
		sensorData = _readBNO055()
		#print(sensorData)

func _run_script(args):
	OS.execute(args[0], [args[1]], false)
	await get_tree().create_timer(0.5).timeout  # wait for 0.5 seconds
	while not File.new().file_exists("pid.txt"):
		await get_tree().create_timer(0.1).timeout  # wait for 0.1 seconds
	var file = File.new()
	file.open("pid.txt", File.READ)
	BNOPID = file.get_line().strip()
	file.close()

func _readBNO055():
	var data
	if udp_server.get_available_packet_count() > 0:
		var packet = udp_server.get_packet().get_string_from_utf8()
		var test_json_conv = JSON.new()
		test_json_conv.parse(packet).result
		data = test_json_conv.get_data()
	return data

func _on_exit_request():
	var file = File.new()
	if file.open("PythonFiles/terminate.txt", File.WRITE) == OK:
		file.store_string("terminate")
		file.close()
	thread.free()
		
func _notification(what):
	if what == MainLoop.NOTIFICATION_WM_QUIT_REQUEST:
		_on_exit_request()
