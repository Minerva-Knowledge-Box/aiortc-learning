\# Synchronous vs Asynchronous Programming



\## 📝 What is Synchronous Programming?

\- In \*\*synchronous programming\*\*, tasks run \*\*one at a time\*\* in the order they are written.

\- Each task \*\*blocks\*\* the next one until it finishes.

\- Example: 

&nbsp; - If you read a file that takes 5 seconds, your whole program pauses for 5 seconds.



\### ✅ When to Use

\- For \*\*simple scripts\*\* where tasks are small and predictable.

\- When you don't care about waiting (e.g., math calculations, sequential workflows).

\- Good for quick prototypes or CPU-heavy tasks that must run in order.



---



\## 📝 What is Asynchronous Programming?

\- In \*\*asynchronous programming\*\*, tasks can \*\*start and then pause\*\* while waiting.

\- While one task is waiting (like fetching data from a server), other tasks can continue.

\- This makes programs \*\*non-blocking\*\* and efficient.



\### ✅ When to Use

\- For \*\*I/O-bound tasks\*\*:

&nbsp; - Network requests (APIs, WebRTC, database queries)

&nbsp; - File read/write

&nbsp; - User input/output

\- For applications needing \*\*high concurrency\*\*:

&nbsp; - Chat apps

&nbsp; - Video streaming

&nbsp; - Real-time dashboards



---



\## 🔑 Key Differences



| Feature                | Synchronous               | Asynchronous            |

|-------------------------|---------------------------|--------------------------|

| Execution Order         | One by one (blocking)     | Overlapping (non-blocking) |

| Efficiency              | Wastes time while waiting | Utilizes waiting time better |

| Best for                | Simple, sequential tasks  | Network-heavy or real-time apps |



---



\## 🚀 Example in Python



\### Synchronous

```python

import time



def task(name, seconds):

&nbsp;   print(f"Start {name}")

&nbsp;   time.sleep(seconds)

&nbsp;   print(f"End {name}")



task("A", 2)

task("B", 2)





\### asynchronous

```python


import asyncio



async def task(name, seconds):

&nbsp;   print(f"Start {name}")

&nbsp;   await asyncio.sleep(seconds)

&nbsp;   print(f"End {name}")



async def main():

&nbsp;   await asyncio.gather(

&nbsp;       task("A", 2),

&nbsp;       task("B", 2),

&nbsp;   )



asyncio.run(main())



