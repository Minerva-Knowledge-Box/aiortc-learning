# worker.py
import sys
import zmq

name = sys.argv[1] if len(sys.argv) > 1 else "worker"

ctx = zmq.Context()
pull = ctx.socket(zmq.PULL)
pull.connect("tcp://localhost:5555")   # Connect to producer

print(f"[{name}] ready")
while True:
    msg = pull.recv_string()
    print(f"[{name}] got:", msg)
