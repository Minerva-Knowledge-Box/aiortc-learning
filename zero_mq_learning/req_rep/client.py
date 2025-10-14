# ----- Client -----
import zmq                                  # Import ZeroMQ Python bindings
#In ZeroMQ, a context is like the “container” or environment that manages all your sockets, I/O threads, and network resources.
ctx = zmq.Context()                         # Create a ZMQ context
socket = ctx.socket(zmq.REQ)                # Create a REQ (request) socket: must send -> recv -> send -> ... in order

socket.connect("tcp://localhost:5555")      # Connect to the server listening on localhost:5555

while True:
    msg = input("Message (enter to quit): ")
    if msg == "":
        break
    socket.send_string(msg)
    reply = socket.recv_string()
    print("Received reply:", reply)
