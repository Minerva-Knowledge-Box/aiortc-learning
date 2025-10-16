import json
import asyncio
import shutil
from pathlib import Path

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

BASE_DIR = Path(__file__).resolve().parents[1]

# >>> Set your file path here (absolute OK) <<<
FILE_TO_STREAM = Path(r"D:\MinervaWorks\aiortc-learning\DjRtcStream\videos\sample.mp4")

PCS = set()

async def wait_for_ice_gathering_complete(pc: RTCPeerConnection, timeout: float = 6.0):
    """Wait until the server finishes gathering ICE candidates (single-shot signaling)."""
    # Poll a few times; break when gathering complete.
    step = 0.05
    tries = int(timeout / step)
    for _ in range(tries):
        if pc.iceGatheringState == "complete":
            break
        await asyncio.sleep(step)

def build_player() -> MediaPlayer:
    """
    Try to open the requested file with ffmpeg.
    If it fails (no video stream or ffmpeg missing), fall back to a test pattern.
    """
    if not shutil.which("ffmpeg"):
        print("[webrtc] ffmpeg not found on PATH — MediaPlayer will fail. Install ffmpeg.")
    if FILE_TO_STREAM.exists():
        print(f"[webrtc] trying to stream: {FILE_TO_STREAM}")
        return MediaPlayer(str(FILE_TO_STREAM))
    else:
        print(f"[webrtc] file not found: {FILE_TO_STREAM}, falling back to testsrc pattern")

    # Test pattern: color bars at 1280x720@30 (lavfi)
    # (Works even if your file path is wrong; ensures pipeline is good.)
    return MediaPlayer("testsrc=size=1280x720:rate=30", format="lavfi")

@csrf_exempt
async def offer(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    try:
        params = json.loads(request.body)
        sdp = params["sdp"]; sdp_type = params["type"]
    except Exception as e:
        return HttpResponseBadRequest(f"Invalid JSON: {e}")

    pc = RTCPeerConnection()
    PCS.add(pc)

    @pc.on("connectionstatechange")
    async def _on_state_change():
        print("[webrtc] pc state:", pc.connectionState)
        if pc.connectionState in ("failed", "closed", "disconnected"):
            await pc.close()
            PCS.discard(pc)

    @pc.on("iceconnectionstatechange")
    async def _on_ice_state():
        print("[webrtc] ice state:", pc.iceConnectionState)

    # Create player (file, or test pattern fallback)
    player = build_player()

    # Add outbound tracks BEFORE answering (no extra transceivers to avoid m-line mismatch)
    sent_any = False
    if getattr(player, "video", None):
        pc.addTrack(player.video)
        print("[webrtc] added VIDEO track from player")
        sent_any = True
    else:
        print("[webrtc] WARNING: player.video is None (no video stream decoded)")

    if getattr(player, "audio", None):
        pc.addTrack(player.audio)
        print("[webrtc] added AUDIO track from player")
        sent_any = True
    else:
        print("[webrtc] (info) player.audio is None")

    if not sent_any:
        return HttpResponseBadRequest("No media tracks available to send.")

    # Handshake
    await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type=sdp_type))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Wait for OUR ICE candidates before replying (since we don't trickle)
    await wait_for_ice_gathering_complete(pc)

    return JsonResponse({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
