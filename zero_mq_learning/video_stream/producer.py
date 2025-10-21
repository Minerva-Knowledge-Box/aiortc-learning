# producer_video.py
# --- Imports we need
import cv2          # OpenCV for reading/encoding video frames
import zmq          # ZeroMQ for messaging
import time         # tiny sleeps (optional) to throttle sending

# --- Create a ZeroMQ context (shared resources for sockets)
ctx = zmq.Context()

# --- Create a PUSH socket (we send frames "downstream")
push = ctx.socket(zmq.PUSH)

# --- Bind the socket so workers can connect to us on TCP port 5555
push.bind("tcp://*:5555")

# --- Path to your video file (put your video under a 'video' folder)
VIDEO_PATH = "video/sample.mp4"

# --- Open the video with OpenCV
cap = cv2.VideoCapture(VIDEO_PATH)

# --- Check that the video opened correctly
if not cap.isOpened():
    print("Could not open video:", VIDEO_PATH)
    exit(1)

# --- Optional: read FPS from file (may be 0 if unknown); fallback to 25
fps = cap.get(cv2.CAP_PROP_FPS) or 25
delay = 1.0 / fps   # delay between frames to roughly match source FPS

print("Streaming frames... Press Ctrl+C to stop.")
try:
    while True:
        # --- Read a frame from the video
        ok, frame = cap.read()
        if not ok:
            # --- No more frames: send an END marker so the worker exits cleanly
            push.send(b"END")
            print("End of video. Sent END.")
            break

        # --- (Optional) resize down to reduce bandwidth
        # frame = cv2.resize(frame, (640, 360))

        # --- Encode the frame as JPEG (compress to bytes for sending)
        ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ok:
            # --- If encoding fails, skip this frame
            continue

        # --- Convert to raw bytes
        jpg_bytes = encoded.tobytes()

        # --- Send the bytes in one message
        push.send(jpg_bytes)

        # --- Sleep a bit so the display looks like video (and not a burst)
        time.sleep(delay)

except KeyboardInterrupt:
    # --- If user stops with Ctrl+C, try to notify the worker
    push.send(b"END")
    print("\nStopped by user. Sent END.")

# --- Cleanup
cap.release()
push.close()
ctx.term()
