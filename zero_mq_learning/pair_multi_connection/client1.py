import zmq
import time
context = zmq.Context()
socket = context.socket(zmq.REQ) # We create a REQ client (REQUEST)
socket.setsockopt(zmq.LINGER, 0)
socket.connect("tcp://127.0.0.1:5555")
for request in range (1,10):
    print("Sending request Client 1 ", request,"...")
    socket.send_string("Hello from client 1")
    message = socket.recv()
    print("Received reply ", request, "[", message, "]")
socket.close()
context.destroy()