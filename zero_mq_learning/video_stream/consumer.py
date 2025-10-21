# worker_display.py
# --- Imports
import cv2          # OpenCV for decoding/Display
import numpy as np  # Needed to convert bytes back into an array
import zmq          # ZeroMQ for messaging

# --- Create a ZeroMQ context
ctx = zmq.Context()

# --- Create a PULL socket (we receive frames from the producer)
pull = ctx.socket(zmq.PULL)

# --- Connect to the producer. If running on same machine, localhost is fine.
pull.connect("tcp://localhost:5555")

print("Waiting for frames... Press 'q' in the video window to quit.")

while True:
    # --- Receive one message (bytes). This blocks until a message arrives.
    msg = pull.recv()

    # --- Check for END marker (tells us to stop gracefully)
    if msg == b"END":
        print("Received END. Exiting.")
        break

    # --- Convert raw JPEG bytes back to a NumPy array buffer
    jpg_array = np.frombuffer(msg, dtype=np.uint8)

    # --- Decode the JPEG bytes into an actual image (BGR)
    frame = cv2.imdecode(jpg_array, cv2.IMREAD_COLOR)
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)

    # --- If decoding failed, skip
    if frame is None:
        continue

    # --- Show the frame in a window titled "Stream"
    cv2.imshow("Stream", frame)

    # --- waitKey(1): process window events; also lets us detect 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("User requested quit. Exiting.")
        break

# --- Cleanup windows and sockets
cv2.destroyAllWindows()
pull.close()
ctx.term()
