import asyncio
import json
import os
import threading
from enum import Enum


class PeerNode:

    class RequestTypes(Enum):
        """
        Enum that defines the actions a client can request from the peer node.
        """
        REQUEST_FILE = "request_file"
        REGISTER = "register"
        GET_DHT = "get_dht"

    class RequestFunctions:
        def __init__(self, node: "PeerNode"):
            self.request_types = self.build_dict()
            self.peer_node: PeerNode = node

        def build_dict(self):
            request_types = {}

            for request_type in PeerNode.RequestTypes:
                request_types[request_type.value] = getattr(self, f"request_{request_type.value}", None)

            return request_types

        def get_requests(self):
            """
            Returns a dictionary of request types and their corresponding functions.
            """
            return self.request_types

        async def request_register(self, message, addr, reader, writer):
            """
            Handle the register request. Send a register request to all informants.
            :param message:
            :param addr:
            :param reader:
            :param writer:
            :return:
            """
            message = {
                "type": "register",
                "host": self.peer_node.host,
                "port": self.peer_node.port,
                "files": self.peer_node.shared_files,
            }
            for informant_host, informant_port in self.peer_node.informants:
                try:
                    reader, writer = await asyncio.open_connection(informant_host, informant_port)
                    writer.write(json.dumps(message).encode())
                    await writer.drain()
                    writer.close()
                    await writer.wait_closed()
                    print(f"[REGISTER] Registered with {informant_host}:{informant_port}")
                except Exception as e:
                    print(f"[ERROR] Register failed ({informant_host}:{informant_port}): {e}")


        async def request_get_dht(self, message, addr, reader, writer):
            """
            Handle the get dht request. Send a get dht request to all informants.
            :param message:
            :param addr:
            :param reader:
            :param writer:
            :return:
            """
            message = {"type": "get_dht"}
            for informant_host, informant_port in self.peer_node.informants:
                try:
                    reader, writer = await asyncio.open_connection(informant_host, informant_port)
                    writer.write(json.dumps(message).encode())
                    await writer.drain()
                    data = await reader.read(4096)
                    self.peer_node.dht = json.loads(data.decode())
                    print(f"[DHT] Retrieved from {informant_host}:{informant_port}")
                except Exception as e:
                    print(f"[ERROR] Get DHT failed ({informant_host}:{informant_port}): {e}")

        async def request_request_file(self, message, addr, reader, writer):
            pass

    def __init__(self, host="127.0.0.1", port=5000, informants=None, share_dir="."):
        self.host = host
        self.port = port
        self.requests_obj = self.RequestFunctions(self)
        self.requests_functions: dict[str, callable] = self.requests_obj.get_requests()
        self.informants = informants or []
        self.share_dir = share_dir
        self.shared_files = []
        self.dht = {}
        self.server = None
        self.loop = None
        self.server_ready = threading.Event()
        self.register_task = None

        self.load_shared_files()

    def load_shared_files(self):
        if os.path.isdir(self.share_dir):
            self.shared_files = [
                f for f in os.listdir(self.share_dir)
                if os.path.isfile(os.path.join(self.share_dir, f))
            ]
        print(f"[+] Shared files loaded: {self.shared_files}")

    async def start_async_server(self):
        try:
            self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
            print(f"[+] Peer Node running on {self.host}:{self.port}")
            self.server_ready.set()
            async with self.server:
                await self.server.serve_forever()
        except asyncio.CancelledError:
            print("[+] Server cancelled.")
        except Exception as e:
            print(f"[ERROR] Server failed: {e}")

    def start_server_in_thread(self):
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            try:
                self.loop.run_until_complete(self.start_async_server())
            finally:
                self.loop.close()
        threading.Thread(target=run_loop, daemon=True).start()

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info("peername")
        print(f"[+] Connection from {addr}")
        try:
            data = await reader.read(1024)
            message = json.loads(data.decode())
            print(f"[>] Received: {message}")

            if message["type"] == "request_file":
                filename = message["filename"]
                filepath = os.path.join(self.share_dir, filename)
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        writer.write(f.read())
                        await writer.drain()
                else:
                    writer.write(b"File not found")
        except Exception as e:
            print(f"[ERROR] handle_client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def register_periodically(self, interval=60):
        while True:
            await self.requests_functions["register"](None, None, None, None)
            await asyncio.sleep(interval)

    async def get_dht(self):
        if not self.informants:
            print("[WARN] No informants configured.")
            return

        informant_host, informant_port = self.informants[0]
        message = {"type": "get_dht"}
        try:
            reader, writer = await asyncio.open_connection(informant_host, informant_port)
            writer.write(json.dumps(message).encode())
            await writer.drain()
            data = await reader.read(4096)
            self.dht = json.loads(data.decode())
            writer.close()
            await writer.wait_closed()
            print(f"[DHT] Retrieved: {self.dht}")
        except Exception as e:
            print(f"[ERROR] Could not retrieve DHT: {e}")

    def menu(self):
        """
        Run the menu in a blocking thread (so it doesn't block async loop).
        """
        self.server_ready.wait()
        while True:
            print("\n[Peer Node Menu]")
            print("1. List Shared Files")
            print("2. List DHT")
            print("3. Exit")
            choice = input("Choose an option: ")

            if choice == "1":
                print("\n[+] Shared Files:")
                for file in self.shared_files:
                    print(file)
            elif choice == "2":
                print("\n[+] DHT:")
                for filename, (host, port) in self.dht.items():
                    print(f"{filename}: {host}:{port}")
            elif choice == "3":
                print("[+] Exiting...")
                asyncio.run_coroutine_threadsafe(self.shutdown_server(), self.loop).result()
                break
            else:
                print("Invalid choice. Try again.")

    async def shutdown_server(self):
        if self.register_task:
            self.register_task.cancel()
            try:
                await self.register_task
            except asyncio.CancelledError:
                pass

        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("[+] Server shut down.")

    async def run(self, with_menu=True):
        self.start_server_in_thread()
        await asyncio.sleep(1)  # Let the server boot up (alternative to `server_ready.wait()` in async)

        await self.get_dht()
        self.register_task = asyncio.create_task(self.register_periodically(interval=5))

        if with_menu:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self.menu)

    async def stop(self):
        await self.shutdown_server()
        if self.loop:
            self.loop.stop()
            print("[+] Peer Node stopped.")
