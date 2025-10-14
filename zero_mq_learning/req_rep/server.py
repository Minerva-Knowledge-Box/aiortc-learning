# ----- Server -----
import zmq                         # Import ZeroMQ Python bindings

ctx = zmq.Context()                # Create a process-wide ZMQ context (manages I/O threads and sockets)
socket = ctx.socket(zmq.REP)       # Create a REP (reply) socket: must recv -> send -> recv -> ... in order

socket.bind("tcp://*:5555")        # Listen on TCP port 5555 on all interfaces (0.0.0.0)
print("Server waiting...")         # Log that the server is ready

while True:                           # Keep handling requests
    msg = socket.recv_string()        # Wait for a request
    print("Received:", msg)           # Show what came in

    reply = input("Type reply (enter to echo): ")  # Let server operator type a reply
    if reply == "":                               # If empty, just echo back
        reply = f"Reply: {msg}"

    socket.send_string(reply)          # Send the reply (must follow a recv)
