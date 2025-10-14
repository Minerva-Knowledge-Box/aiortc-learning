import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer

async def main():
    config = RTCConfiguration(
        iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])]
    )
    pc = RTCPeerConnection(configuration=config)

    @pc.on("datachannel")
    def on_datachannel(ch):
        print("[Answer] Data channel received")

        @ch.on("message")
        def on_message(msg):
            print("[Answer] Got:", msg)
            ch.send("Reply from answer side!")

    print("\n--- PASTE the offer JSON here ---\n")
    offer = json.loads(input())
    await pc.setRemoteDescription(RTCSessionDescription(**offer))

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    print("\n--- COPY this answer JSON and paste back into offer.py ---\n")
    print(json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}))
    print("\n[Answer] Waiting for messages... (Ctrl+C to quit)")

    try:
        while True:
            await asyncio.sleep(1)  # keep running
    except KeyboardInterrupt:
        pass
    finally:
        await pc.close()

asyncio.run(main())
