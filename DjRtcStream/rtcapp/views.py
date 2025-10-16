import json
from pathlib import Path
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRecorder, MediaRelay

PCS = set()
RECORDINGS_DIR = Path(__file__).resolve().parents[1] / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)

relay = MediaRelay()  # lets us subscribe to the same incoming track safely

@csrf_exempt
async def offer(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    try:
        params = json.loads(request.body)
        sdp = params["sdp"]
        sdp_type = params["type"]
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    pc = RTCPeerConnection()
    PCS.add(pc)

    recorder = MediaRecorder(str(RECORDINGS_DIR / "out.mp4"))

    # Create transceivers BEFORE answering, so our SDP advertises sendrecv
    video_sender = pc.addTransceiver("video", direction="sendrecv").sender
    audio_sender = pc.addTransceiver("audio", direction="sendrecv").sender

    @pc.on("track")
    async def on_track(track):
        # 1) record the incoming track
        await recorder.start()
        recorder.addTrack(track)

        # 2) loop the same track back to the browser
        if track.kind == "video":
            await video_sender.replaceTrack(relay.subscribe(track))
        elif track.kind == "audio":
            await audio_sender.replaceTrack(relay.subscribe(track))

        @track.on("ended")
        async def _on_ended():
            try:
                await recorder.stop()
            except Exception:
                pass
            await video_sender.replaceTrack(None)
            await audio_sender.replaceTrack(None)

    # complete WebRTC handshake
    await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type=sdp_type))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return JsonResponse({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
