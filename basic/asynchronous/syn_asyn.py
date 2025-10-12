# python 
# python concurrency

# 1. async keyword
# 2. await keyword
# 3. asyncio module

# In Python's asyncio library, the event loop is the central component that manages and executes asynchronous tasks. 
# It acts as a scheduler or orchestrator, determining which piece of code runs when -
# enabling concurrent execution within a single thread.
#Note: Co routine doesn't running until it is awaited. 


# Quick rules of thumb

# If the function is declared async def or returns a Task/Future → await it.

# If it’s I/O-bound and there’s an async library → use that and await.

# If it’s CPU-bound → don’t await directly; offload to process pool.

# If it’s a blocking third-party lib with no async API → to_thread/run_in_executor and await the wrapper.

# Use asyncio.gather(...) or create_task(...) to run multiple awaitables concurrently.

import asyncio

#this is coroutine function
async def main():
    print("Start of main coroutine")
main() #when we call main() it will return coroutine object
#run the main coroutine
asyncio.run(main())





# Define a coroutine that simulates a time-consuming I/O task
async def fetch_data(delay, id): #If the function is declared async def or returns a Task/Future → await it.
    print("Fetching data... id:", id)
    await asyncio.sleep(delay)           # pretend we're waiting on I/O
    print("Data fetched, id:", id)
    return {"data": "Some data", "id": id}

# --- Version A: (awaits sequentially) ---
async def main():
    # Create coroutine objects (not yet running tasks)
    task1 = fetch_data(2, 1)
    task2 = fetch_data(2, 2)

    # Await them one after the other -> ~4 seconds total (2s + 2s)
    result1 = await task1
    print(f"Received result: {result1}")

    result2 = await task2
    print(f"Received result: {result2}")


asyncio.run(main())


# --- Version B: (awaits concurrent) ---

# Define a coroutine that simulates a time-consuming I/O task
async def fetch_data(id, sleep_time):
    print(f"Coroutine {id} starting to fetch data.")
    await asyncio.sleep(sleep_time)
    return {"id": id, "data": f"Sample data from coroutine {id}"}

# Define the main coroutine
async def main():
    # Create tasks for running coroutines concurrently
    task1 = asyncio.create_task(fetch_data(1, 2))
    task2 = asyncio.create_task(fetch_data(2, 3))
    task3 = asyncio.create_task(fetch_data(3, 1))

    # Await results (tasks already running concurrently)
    result1 = await task1
    result2 = await task2
    result3 = await task3

    print(result1, result2, result3)

# Run the event loop
asyncio.run(main())







