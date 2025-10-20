#!/usr/bin/env python3
# Minimal ZeroMQ producer: reads video/sample.mp4, converts frames to grayscale,
# and publishes JPEG frames on tcp://*:5556 under topic "stream1".
import time, json
import cv2, zmq

VIDEO_PATH = "video/sample.mp4"   # <- put your input here
BIND = "tcp://*:5556"
TOPIC = b"stream1"

def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        raise SystemExit(f"Could not open input video: {VIDEO_PATH}")
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS) or 30.0

    ctx = zmq.Context.instance()
    sock = ctx.socket(zmq.PUB)
    sock.bind(BIND)

    print(f"[producer] grayscale streaming from {VIDEO_PATH} {width}x{height}@{fps:.2f} -> {BIND} topic=stream1")

    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            print("[producer] end of file")
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ok, buf = cv2.imencode(".jpg", gray, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ok:
            continue

        meta = {
            "ts": int(time.perf_counter_ns()),
            "w": width, "h": height, "fps": float(fps),
            "fmt": "jpeg", "cs": "gray", "i": frame_idx,
        }
        # Multipart: [topic, metadata_json, jpeg_bytes]
        sock.send_multipart([TOPIC, json.dumps(meta).encode("utf-8"), buf.tobytes()])
        frame_idx += 1

    cap.release()
    sock.close(0)
    ctx.term()

if __name__ == "__main__":
    main()
