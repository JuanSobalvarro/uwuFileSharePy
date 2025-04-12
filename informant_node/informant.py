import asyncio
import json
import sys
import threading
from enum import Enum


class InformantNode:
    class RequestTypes(Enum):
        """
        Enum that defines the actions a client can request from the informant node.
        """
        REGISTER = "register"
        GET_DHT = "get_dht"
        GET_FILE = "get_file"

    class RequestFunctions:
        def __init__(self, node: "InformantNode"):
            self.request_types = self.build_dict()
            self.node: InformantNode = node

        def build_dict(self):
            request_types = {}

            for request_type in InformantNode.RequestTypes:
                request_types[request_type.value] = getattr(self, f"request_{request_type.value}", None)

            return request_types

        def get_requests(self):
            """
            Returns a dictionary of request types and their corresponding functions.
            """
            return self.request_types

        async def request_register(self, message, addr, reader, writer):
            """
            Handle the register request.
            This function is called when a peer registers its files with the informant.
            """
            for file in message["files"]:

                if file in self.node.dht:
                    print(f"[DHT] File {file} already registered. Updating...")

                self.node.dht[file] = (message["host"], message["port"])

                if self.node.dht[file] != (message["host"], message["port"]):
                    print(f"[ERROR] File is not correctly being registered.")
            print(f"[REGISTER] {addr} registered files: {message['files']}")

        async def request_get_dht(self, message, addr, reader, writer):
            """

            :return:
            """
            response = json.dumps(self.node.dht).encode()
            writer.write(response)
            await writer.drain()
            print(f"[DHT] Sent DHT to {addr}")

        async def request_get_file(self, message, addr, reader, writer):
            """
            Handle the get file request.
            :param message:
            :param addr:
            :param reader:
            :param writer:
            :return:
            """
            pass

    def __init__(self, host="127.0.0.1", port=6000):
        self.host = host
        self.port = port
        self.requests_obj = self.RequestFunctions(self)
        self.requests_functions: dict[str, callable] = self.requests_obj.get_requests()
        self.dht = {}
        self.server = None
        self.server_up = False
        self.loop = None  # Background thread event loop
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
        print("[+] Server ready with this functions:")

        for key, func in self.requests_functions.items():
            print(f"  - {key}")

        self.server_ready.set()  # Notify the main thread
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

            for key in message:
                if key not in ["type", "host", "port", "files"]:
                    print(f"[ERROR] Invalid key in message: {key}")
                    return

            if message["type"] in self.requests_functions:
                func = self.requests_functions[message["type"]]
                if func:
                    await func(message, addr, reader, writer)
                else:
                    print(f"[ERROR] Function not found for type: {message['type']}")
                    return

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
        """
        Run the informant node server.
        :return:
        """
        # Start the server in a separate thread
        threading.Thread(target=self.server_thread_func, daemon=True).start()
