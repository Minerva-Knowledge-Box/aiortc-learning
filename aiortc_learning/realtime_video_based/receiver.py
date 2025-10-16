# =========================
# receiver.py (simple + commented)
# =========================

import asyncio
import cv2
from aiortc import RTCPeerConnection, RTCSessionDescription  # WebRTC peer + SDP type
from aiortc.contrib.signaling import TcpSocketSignaling     # TCP-based signaling helper
from av import VideoFrame                                   # aiortc/PyAV video frame type

# --- Signaling relay address: must match your running server.py and the sender ---
HOST, PORT = "127.0.0.1", 10001


async def display_frames(track):
    """
    Read frames from the incoming WebRTC video track and show them with OpenCV.
    Press 'q' in the window to quit.
    """
    print("display_frames started")

    while True:
        try:
            # Await the next video frame from the WebRTC pipeline
            frame = await track.recv()

            # aiortc delivers PyAV VideoFrame objects; convert to NumPy (BGR) for OpenCV
            if isinstance(frame, VideoFrame):
                img = frame.to_ndarray(format="bgr24")

                # Show the frame in a window titled "Receiver (press q)"
                cv2.imshow("Receiver (press q)", img)

                # Close when user presses 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("q pressed")
                    break

        except Exception as e:
            # Any error (e.g., connection closed) breaks the loop
            print("display_frames error:", e)
            break

    # Make sure all OpenCV windows are closed when leaving
    cv2.destroyAllWindows()


async def main():
    # 1) Create signaling helper that connects to the TCP relay (server.py)
    signaling = TcpSocketSignaling(HOST, PORT)

    # 2) Create the WebRTC peer connection for the receiver
    pc = RTCPeerConnection()

    # 3) When a media track arrives (from the sender), start showing its frames
    @pc.on("track")
    def on_track(track):
        print("Track received:", track.kind)
        if track.kind == "video":                 # only handle video tracks here
            asyncio.create_task(display_frames(track))

    # 4) Optional: log connection state changes for visibility/debugging
    @pc.on("connectionstatechange")
    async def on_state():
        print("Receiver state:", pc.connectionState)

    # 5) Connect to the relay and wait for the sender's SDP OFFER
    await signaling.connect()
    print("Receiver: Waiting for offer…")
    offer = await signaling.receive()
    print("Receiver: offer received:", isinstance(offer, RTCSessionDescription))

    # 6) Apply the sender's OFFER as our remote description
    await pc.setRemoteDescription(offer)

    # 7) Create our ANSWER, set it locally, and send it back via signaling
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    await signaling.send(pc.localDescription)
    print("Receiver: answer sent")

    # 8) Keep the program alive while the connection is active so frames keep coming
    try:
        while pc.connectionState not in ("failed", "closed"):
            await asyncio.sleep(0.5)
    finally:
        # 9) Clean up when done
        await pc.close()
        print("Receiver closed")


# Standard Python entry point: run the async main() function
if __name__ == "__main__":
    asyncio.run(main())
