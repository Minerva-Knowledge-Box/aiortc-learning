import zmq
import time
# Same as before, initialize a socket
context = zmq.Context()
socket = context.socket(zmq.PAIR) # We create a PAIR server
socket.setsockopt(zmq.LINGER, 0)
# Connect to the IP that we already bind in the server
socket.connect("tcp://127.0.0.1:5555")
# A counter will help us control our connection
# For example connect until you send 10 messages, then disconnect...
count = 0
while count<10:
    msg = socket.recv()
    print(msg)
    socket.send_string("Hello from Client")
    socket.send_string("This is a client message to server")
    print("Counter: ",count)
    count+=1
    time.sleep(1)
# Destroy the context socket and then close the connection
context.destroy()
socket.close()