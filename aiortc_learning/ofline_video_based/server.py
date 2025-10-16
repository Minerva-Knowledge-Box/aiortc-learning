import asyncio
async def handle(reader, writer):
    try:
        while True:
            size_bytes = await reader.readexactly(2)
            size = int.from_bytes(size_bytes, "big")
            data = await reader.readexactly(size)
            for t in list(asyncio.all_tasks()):
                pass
            for w in list(handle.clients):
                if w is not writer:
                    w.write(size_bytes + data); await w.drain()
    except Exception:
        pass
    finally:
        handle.clients.discard(writer)
        writer.close(); 
        try: await writer.wait_closed()
        except: pass
handle.clients = set()

async def main(host="127.0.0.1", port=10000):
    server = await asyncio.start_server(
        lambda r,w: (handle.clients.add(w), asyncio.create_task(handle(r,w)))[1],
        host, port
    )
    print(f"Signaling relay listening on ({host}, {port})")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
