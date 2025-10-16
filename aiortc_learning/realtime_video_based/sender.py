import asyncio, cv2
# asyncio: for async/await; cv2: OpenCV for camera access

from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
# RTCPeerConnection = the WebRTC peer
# RTCSessionDescription = offer/answer objects
# VideoStreamTrack = base class to send video frames

from aiortc.contrib.signaling import TcpSocketSignaling
# TcpSocketSignaling = helper to send/receive offer/answer over a TCP relay

from av import VideoFrame
# VideoFrame = wrapper type aiortc uses for video frames

from datetime import datetime
# datetime = to draw a timestamp on frames

HOST, PORT = "127.0.0.1", 10001
# Address/port of your signaling relay (server). Must match server/receiver.

CAMERA_ID = 0
# Which camera to open. Try 0, then 1 or 2 if 0 doesn’t work.

LOCAL_PREVIEW = False  # set True to see your own camera in a window
# If True, show a local OpenCV preview window in the sender.

class CameraTrack(VideoStreamTrack):
    kind = "video"
    # This class produces video frames for WebRTC.

    def __init__(self, camera_id=0):
        super().__init__()
        # Call parent constructor.

        # CAP_DSHOW helps on Windows; fall back if needed
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        # Try to open the camera with DirectShow backend (Windows friendly).

        if not cap.isOpened():
            cap = cv2.VideoCapture(camera_id)
            # If that failed, try again with default backend.

        self.cap = cap
        print("cap.isOpened():", self.cap.isOpened())
        # Print whether the camera actually opened.

        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {camera_id}")
            # If still not opened, stop with an error.

    async def recv(self):
        # Called repeatedly by aiortc to get the next frame to send.

        pts, time_base = await self.next_timestamp()
        # Get the next presentation timestamp & time base (proper pacing).

        ok, frame = self.cap.read()
        # Grab a frame from the webcam (BGR image).

        if not ok:
            raise RuntimeError("Camera read failed")
            # If reading failed, stop with an error.

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        # Create a text timestamp like "2025-10-16 12:34:56.789".

        cv2.putText(frame, ts, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        # Draw the timestamp onto the BGR frame (top-left corner).

        if LOCAL_PREVIEW:
            cv2.imshow("Sender preview (press q)", frame)
            # Optionally show your own camera in a window.

            if cv2.waitKey(1) & 0xFF == ord('q'):
                raise RuntimeError("Sender preview quit")
                # If you press 'q', stop the track (raises to exit).

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert OpenCV's BGR image to RGB (PyAV/aiortc expect RGB here).

        vf = VideoFrame.from_ndarray(frame_rgb, format="rgb24")
        # Wrap the numpy array as a VideoFrame (24-bit RGB).

        vf.pts, vf.time_base = pts, time_base
        # Attach the timestamp info so the receiver plays it smoothly.

        return vf
        # Return the frame to aiortc; it will send it over the WebRTC connection.

    async def stop(self):
        # Called when the track is being stopped/cleaned up.
        if self.cap: self.cap.release()
        # Release the camera device.

        cv2.destroyAllWindows()
        # Close any local preview window if it was open.

        await super().stop()
        # Let the parent do its cleanup too.

async def main():
    signaling = TcpSocketSignaling(HOST, PORT)
    # Create a signaling helper that connects to your TCP relay.

    pc = RTCPeerConnection()
    # Create the WebRTC peer connection (your “sender” peer).

    pc.addTrack(CameraTrack(CAMERA_ID))
    # Add your camera stream as an outgoing video track.

    @pc.on("connectionstatechange")
    async def on_state():
        print("Sender state:", pc.connectionState)
        # Print changes like 'connecting', 'connected', 'disconnected', etc.

    await signaling.connect()
    # Connect to the TCP relay (server). This does NOT “bind”; it connects.

    print("Sender: creating offer")
    offer = await pc.createOffer()
    # Ask WebRTC to create an SDP offer describing our media and ICE info.

    await pc.setLocalDescription(offer)
    # Set that offer as our local description.

    await signaling.send(pc.localDescription)
    # Send the offer to the other side via the relay.

    print("Sender: offer sent, waiting for answer…")

    while True:
        obj = await signaling.receive()
        # Wait for the receiver’s reply via the relay.

        print("Sender: signaling received:", type(obj).__name__)
        # Log what we got (e.g., RTCSessionDescription).

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            # Set the receiver’s ANSWER as our remote description.

            print("Sender: answer set; streaming…")
            break

        if obj is None:
            print("Sender: signaling ended"); break
            # If signaling closed unexpectedly, exit.

    while pc.connectionState not in ("failed", "closed"):
        await asyncio.sleep(0.5)
        # Keep the program alive while the connection is up.

    await pc.close(); print("Sender closed")
    # Cleanly close when the connection ends.

if __name__ == "__main__":
    asyncio.run(main())
    # Run the async main() when you execute this file directly.
