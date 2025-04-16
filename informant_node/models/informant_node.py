"""
Informant Node
"""
import asyncio
import json
import threading
from services.protocol import UWUProtocol
from services.request_handler import RequestFunctions
from .dht_model import DHT


class InformantNode:
    def __init__(self, host="127.0.0.1", port=6000):
        self.host = host
        self.port = port
        self.dht = DHT()
        self.request_handler = RequestFunctions(self)
        self.handlers = self.request_handler.get_handlers()
        self.server = None
        self.server_up = False
        self.loop = None
        self.server_ready = threading.Event()

    async def shutdown_server(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("[+] Server has been shut down.")

    async def start_async_server(self):
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
        self.server_up = True
        print(f"[+] Informant Node running on {self.host}:{self.port}")
        print("[+] Registered functions:")

        for key in self.handlers:
            print(f"  - {key}")

        self.server_ready.set()
        async with self.server:
            await self.server.serve_forever()

    def server_thread_func(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.start_async_server())
        except Exception as e:
            print(f"[ERROR] Server loop exception: {e}")
        finally:
            self.loop.close()

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"[+] Connection from {addr}")
        try:
            data = await reader.read(1024)
            message = json.loads(data.decode())

            if not UWUProtocol.is_valid_request(message):
                raise ValueError("Invalid request format")

            request_type = message["type"]
            handler = self.handlers.get(request_type)

            if handler:
                await handler(message, addr, reader, writer)
            else:
                print(f"[ERROR] No handler for request type: {request_type}")
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON received from {addr}")
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    def shutdown_safely(self):
        if self.server and self.loop:
            asyncio.run_coroutine_threadsafe(self.shutdown_server(), self.loop)

    def run(self):
        threading.Thread(target=self.server_thread_func, daemon=True).start()
