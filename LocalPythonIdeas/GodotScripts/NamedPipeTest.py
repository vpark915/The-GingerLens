newlist = [1,2,3,4,5]
while True:
    with open('my_pipe', 'w') as pipe:
        pipe.write('Hello from Python!')