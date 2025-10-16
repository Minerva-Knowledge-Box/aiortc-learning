# sender_file.py — stream out.mp4 using MediaPlayer (video + audio if present)
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling
from aiortc.contrib.media import MediaPlayer

HOST, PORT = "127.0.0.1", 10001
VIDEO_PATH = "sample.mp4"

async def main():
    signaling = TcpSocketSignaling(HOST, PORT)
    pc = RTCPeerConnection()

    # Create the MediaPlayer. Some aiortc versions don't support "loop".
    # We try with loop=True, and if that arg isn't supported, we retry without it.
    try:
        player = MediaPlayer(VIDEO_PATH, loop=True)   # modern aiortc
    except TypeError:
        player = MediaPlayer(VIDEO_PATH)              # older aiortc (no loop)

    # Add video track if present
    if player.video:
        pc.addTrack(player.video)
        print("Added video track from file")

    # Add audio track if present
    if player.audio:
        pc.addTrack(player.audio)
        print("Added audio track from file")

    @pc.on("connectionstatechange")
    async def on_state_change():
        print("Sender(state):", pc.connectionState)

    await signaling.connect()
    print("Creating offer…")
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    await signaling.send(pc.localDescription)
    print("Offer sent; waiting for answer…")

    # Wait for receiver's answer
    while True:
        obj = await signaling.receive()
        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            print("Answer received; streaming file…")
            break
        if obj is None:
            print("Signaling ended.")
            break

    # Keep the process alive while connected
    try:
        while pc.connectionState not in ("failed", "closed"):
            await asyncio.sleep(0.5)
    finally:
        await pc.close()
        print("Sender closed")

if __name__ == "__main__":
    asyncio.run(main())
