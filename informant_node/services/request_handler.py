# services/request_handler.py

import json
from .protocol import UWUProtocol

class RequestFunctions:
    def __init__(self, node: "InformantNode"):
        self.node: "InformantNode" = node
        self.request_map = self._build_map()

    def _build_map(self):
        return {
            UWUProtocol.RequestTypes.REGISTER.value: self.request_register,
            UWUProtocol.RequestTypes.GET_DHT.value: self.request_get_dht,
            UWUProtocol.RequestTypes.GET_FILE.value: self.request_get_file,
        }

    def get_handlers(self):
        return self.request_map

    async def request_register(self, message, addr, reader, writer):
        for file in message.get("files", []):
            if file in self.node.dht:
                print(f"[DHT] File {file} already registered. Updating...")

            response = self.node.dht.add_file(file, message["host"], message["port"])

            if not response:
                print(f"[DHT] File {file} already registered. Skipping...")
                continue

            print(f"[DHT] File {file} registered.")

    async def request_get_dht(self, message, addr, reader, writer):
        response = json.dumps(self.node.dht.get_all_files()).encode()
        writer.write(response)
        await writer.drain()
        print(f"[DHT] Sent DHT to {addr}")

    async def request_get_file(self, message, addr, reader, writer):
        file = self.node.dht.get_file(addr, message["host"], message["port"])

        if file:
            print(f"[DHT] File {file} found.")
            response = UWUProtocol.create_response(UWUProtocol.ResponseTypes.SUCCESS, file=file)
        else:
            print(f"[DHT] File not found.")
            response = UWUProtocol.create_response(UWUProtocol.ResponseTypes.ERROR, message="File not found")

        writer.write(response)
        await writer.drain()
