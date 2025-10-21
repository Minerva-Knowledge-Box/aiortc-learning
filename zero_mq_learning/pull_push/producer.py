# producer.py
import zmq
import time

ctx = zmq.Context()
push = ctx.socket(zmq.PUSH)
push.bind("tcp://*:5555")   # Workers will connect here

for i in range(1, 13):
    msg = str(i)
    print("[PRODUCER] send:", msg)
    push.send_string(msg)
    time.sleep(1)        # small pause to watch distribution

print("[PRODUCER] done")

