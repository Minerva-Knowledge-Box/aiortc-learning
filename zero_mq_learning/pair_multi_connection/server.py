import zmq
import time
try: # Try to create a new connection
    context = zmq.Context()
    socket = context.socket(zmq.REP) # We create a REP server
    # Here we set a linger period for the socket
    # Linger 0: no waiting period for new messages
    socket.setsockopt(zmq.LINGER, 0)
    socket.bind("tcp://127.0.0.1:5555")
    while True: # Wait for next request from client
        message = socket.recv()
        print("Received request: ", message)
        time.sleep (1)  
        socket.send_string("Hi from Server")
except KeyboardInterrupt: # “ctr+c” to break and close the socket!
    context.destroy()
    socket.close()