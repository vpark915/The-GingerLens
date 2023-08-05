import threading

def loop():
    while True:
        print("lmao lmao lmao")

t = threading.Thread(target=loop)
t.start()
t.join()

