#!/usr/bin/env python3
# Minimal ZeroMQ → OpenCV consumer with live preview + MJPEG recording (Windows-friendly).
# Message shape: [topic, jpeg] OR [topic, meta_json, jpeg]
import os, json
import cv2, zmq
import numpy as np

CONNECT = "tcp://localhost:5556"
TOPIC = b"stream1"                 # set to b"" to receive all topics (debug)
OUT_PATH = "video/output.avi"      # .avi + MJPG is widely supported on Windows
FPS_DEFAULT = 25.0
FOURCC = cv2.VideoWriter_fourcc(*"MJPG")

def main():
    os.makedirs(os.path.dirname(OUT_PATH) or ".", exist_ok=True)

    # ZMQ subscriber
    ctx = zmq.Context.instance()
    sock = ctx.socket(zmq.SUB)
    sock.connect(CONNECT)
    sock.setsockopt(zmq.SUBSCRIBE, TOPIC)
    print(f"[consumer] listening on {CONNECT} topic={TOPIC!r}")

    writer = None
    w = h = None
    fps = FPS_DEFAULT
    window = "stream1"

    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    try:
        while True:
            try:
                parts = sock.recv_multipart()
            except KeyboardInterrupt:
                break
            if not parts:
                continue

            # Accept [topic, jpeg] or [topic, meta_json, jpeg]
            if len(parts) == 2:
                topic, jpeg_bytes = parts
                meta = {}
            elif len(parts) >= 3:
                topic, meta_json, jpeg_bytes = parts[:3]
                try:
                    meta = json.loads(meta_json.decode("utf-8"))
                except Exception:
                    meta = {}
            else:
                continue

            # Decode JPEG → gray → BGR
            buf = np.frombuffer(jpeg_bytes, dtype=np.uint8)
            gray = cv2.imdecode(buf, cv2.IMREAD_GRAYSCALE)
            if gray is None:
                continue

            fh, fw = gray.shape[:2]
            w = int(meta.get("w", fw) or fw)
            h = int(meta.get("h", fh) or fh)
            fps = float(meta.get("fps", 0) or fps or FPS_DEFAULT)

            if (fw, fh) != (w, h):
                gray = cv2.resize(gray, (w, h), interpolation=cv2.INTER_AREA)
            bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

            # Lazy-open writer once size/fps known
            if writer is None:
                writer = cv2.VideoWriter(OUT_PATH, FOURCC, fps, (w, h), isColor=True)
                if not writer.isOpened():
                    raise SystemExit(f"Could not open writer for {OUT_PATH}")
                print(f"[consumer] writer opened: {OUT_PATH} ({w}x{h}@{fps:.2f}, MJPG)")

            writer.write(bgr)

            # Live preview
            cv2.imshow(window, bgr)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[consumer] 'q' pressed; exiting")
                break

    finally:
        if writer is not None:
            writer.release()
            print(f"[consumer] closed writer: {OUT_PATH}")
        cv2.destroyAllWindows()
        try:
            sock.close(0)
        finally:
            ctx.term()

if __name__ == "__main__":
    main()
