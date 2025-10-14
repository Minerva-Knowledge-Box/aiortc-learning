import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer

async def main():
    config = RTCConfiguration(
        iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])]
    )
    pc = RTCPeerConnection(configuration=config)
    channel = pc.createDataChannel("chat")

    @channel.on("open")
    def on_open():
        print("[Offer] Channel open — ready to chat")
        channel.send("Hello from offer side!")

    @channel.on("message")
    def on_message(msg):
        print("[Offer] Got:", msg)

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    print("\n--- COPY this offer JSON and paste into answer.py ---\n")
    print(json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}))
    print("\n--- THEN paste the answer JSON below ---\n")

    answer = json.loads(input())
    await pc.setRemoteDescription(RTCSessionDescription(**answer))
    print("[Offer] Connection established! Type messages (Ctrl+C to quit).")

    try:
        while True:
            msg = input("You: ")
            if channel.readyState == "open":
                channel.send(msg)
            else:
                print("[Offer] Channel closed — cannot send")
                break
            await asyncio.sleep(0.1)  # small delay keeps event loop alive
    except KeyboardInterrupt:
        pass
    finally:
        await pc.close()

asyncio.run(main())
