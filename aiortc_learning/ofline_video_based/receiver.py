# =========================
# receiver.py (fits-on-screen version, fully commented)
# =========================
#
# WHAT THIS DOES
# - Connects to your local signaling relay (server.py) via TcpSocketSignaling.
# - Waits for the sender's SDP offer, returns an answer, then receives video.
# - Shows the incoming video in a window that FITS on your laptop screen.
#   (It preserves aspect ratio and avoids upscaling to keep things sharp.)
#
# HOW TO RUN (order matters)
# 1) python server.py
# 2) python receiver.py
# 3) python sender.py   (or sender_file.py)
#
# REQUIREMENTS
#   pip install aiortc opencv-python av

import asyncio
import cv2
from aiortc import RTCPeerConnection, RTCSessionDescription   # WebRTC peer + SDP container
from aiortc.contrib.signaling import TcpSocketSignaling      # TCP-based signaling helper
from av import VideoFrame                                    # aiortc/PyAV video frame wrapper

# --- Signaling relay address: must match your server.py and sender ---
HOST, PORT = "127.0.0.1", 10001

# --- Max display size for the preview window (in pixels) ---
# Choose something that fits your laptop screen; aspect ratio is preserved.
MAX_DISPLAY_WIDTH  = 960
MAX_DISPLAY_HEIGHT = 540


async def display_frames(track):
    """
    Pull frames from an incoming WebRTC video track and display them.
    We scale frames down to fit within MAX_DISPLAY_WIDTH x MAX_DISPLAY_HEIGHT,
    preserving aspect ratio and avoiding upscaling for better quality.
    Press 'q' in the window to quit.
    """
    print("display_frames started")

    # Make the window resizable and set an initial window size (optional).
    # This affects only the OS window; we still resize the image for quality.
    window_title = "Receiver (press q)"
    cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_title, MAX_DISPLAY_WIDTH, MAX_DISPLAY_HEIGHT)

    while True:
        try:
            # Await the next frame from the WebRTC pipeline.
            frame = await track.recv()

            # Convert PyAV VideoFrame -> NumPy BGR (what OpenCV expects).
            if isinstance(frame, VideoFrame):
                img = frame.to_ndarray(format="bgr24")

                # Current frame size.
                h, w = img.shape[:2]

                # Compute a scale factor that fits within our max display size.
                # min(..., 1.0) ensures we never UPSCALE (keeps things crisp).
                scale = min(
                    MAX_DISPLAY_WIDTH  / w,
                    MAX_DISPLAY_HEIGHT / h,
                    1.0
                )

                # If the frame is bigger than the window, downscale it.
                if scale < 1.0:
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    # INTER_AREA is recommended for downscaling.
                    img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

                # Show the (possibly resized) frame.
                cv2.imshow(window_title, img)

                # Exit cleanly when user presses 'q'.
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("q pressed")
                    break

        except Exception as e:
            # Any exception (e.g., connection closed) -> stop displaying.
            print("display_frames error:", e)
            break

    # Close the OpenCV window(s) when leaving the loop.
    cv2.destroyAllWindows()


async def main():
    # 1) Create the signaling helper that talks to your TCP relay.
    signaling = TcpSocketSignaling(HOST, PORT)

    # 2) Create the WebRTC peer connection (the "receiver" peer).
    pc = RTCPeerConnection()

    # 3) When a media track arrives from the sender, start reading frames.
    @pc.on("track")
    def on_track(track):
        print("Track received:", track.kind)
        if track.kind == "video":
            # Start the frame-reading task (async loop).
            asyncio.create_task(display_frames(track))

    # 4) Optional: log connection state changes for visibility/debugging.
    @pc.on("connectionstatechange")
    async def on_state():
        print("Receiver state:", pc.connectionState)

    # 5) Connect to the relay and wait for the sender's SDP OFFER.
    await signaling.connect()
    print("Receiver: Waiting for offer…")
    offer = await signaling.receive()
    print("Receiver: offer received:", isinstance(offer, RTCSessionDescription))

    # 6) Apply the sender's OFFER, then create/send our ANSWER.
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    await signaling.send(pc.localDescription)
    print("Receiver: answer sent")

    # 7) Keep the program alive while the connection is active so frames keep coming.
    try:
        while pc.connectionState not in ("failed", "closed"):
            await asyncio.sleep(0.5)
    finally:
        # 8) Clean up the WebRTC peer when done.
        await pc.close()
        print("Receiver closed")


# Standard entry point: run the async main() when executed directly.
if __name__ == "__main__":
    asyncio.run(main())
