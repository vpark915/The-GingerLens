extends Node

var pipe_name = "PythonFiles/my_pipe" #Pipeline Name
var interpreter_path = "PythonFiles/venv/Scripts/python.exe" #Python Details
var script_path = "PythonFiles/NamedPipeTest.py" #Python Script to execute

func _ready():
	#Create a new thread 
	var pythread = Thread.new()
	#Run the display function 
	pythread.start(self,"run_python")
	
func _process(delta):
	#OPEN THE PYTHON PIPE 
	var file = File.new()
	
	if file.open(pipe_name, File.READ) == OK:
		var data = []
		
		while not file.eof_reached():
			var line = file.get_line()
			if line != "":
				data.append(line)
		
		file.close()
		
		print(data) # Should print the list ["Hello", "from", "Python"]
	else:
		print("Failed to open the pipe.")

func run_python():
	#EXECUTE THE PYTHON INTERPRETER
	OS.execute(interpreter_path, [script_path], true)
