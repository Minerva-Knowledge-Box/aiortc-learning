# import the library
import zmq
import time
# Initialize a new context that is the way to create a socket
context = zmq.Context()
# We will build a PAIR connection
socket = context.socket(zmq.PAIR) # We create a PAIR server
# Do not worry about this for the moment...
socket.setsockopt(zmq.LINGER, 0) #Sets the socket’s LINGER option to 0 milliseconds.
#When you close the socket (or your process ends), ZeroMQ will not wait to send any queued/outgoing messages. It drops them immediately and closes right away.

# Create a new socket and "bind" it in the following address
# Tells this socket to listen on a network endpoint using TCP at host 127.0.0.1 and port 5555.
socket.bind("tcp://127.0.0.1:5555") # server binds on localhost
# Keep the socket alive for ever...
while True:
    # Send a text message to the client (send_string)
    socket.send_string("Server message to Client")
    # Receive a message, store it in msg and then print it
    msg = socket.recv()
    print(msg)
    # Sleep for 1 second, so when we run it, we can see the results
    time.sleep(1)