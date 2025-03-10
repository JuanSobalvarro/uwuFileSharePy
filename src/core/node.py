import asyncio
import json
import socket
from typing import Set


class PeerNode:
    def __init__(self, host: str = "0.0.0.0", port: int = 6942):
        self.server: asyncio.Server  = None
        self.peers: Set = set()
        self.host = host
        self.port = port

    async def start_server(self):
        """
        Start peer server (to accept incoming connections)
        :return:
        """
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = self.server.sockets[0].getsockname()
        print(f"[*] PeerNode listening on {addr}:{self.port}")
        async with self.server:
            await self.server.serve_forever()

    async def handle_client(self, reader, writer):
        """
        Handle incoming client connections
        :param reader:
        :param writer:
        :return:
        """
        addr = writer.get_extra_info('peername')
        print(f"[+] Received connection from {addr}")
        self.peers.add(addr)

        try:
            while True:
                data = await reader.read(1024)

                # If no data is received, break the loop
                if not data:
                    print(f"[-] Connection from {addr} closed")
                    break

                message = json.loads(data.decode())
                print(f"[>] Received {message} from {addr}")

                if message["type"] == "ping":
                    response = json.dumps({"type": "pong"}).encode()
                    writer.write(response)
                    await writer.drain()

        except Exception as e:
            print(f"[X] Error: {e}")

        finally:
            print(f"[-] Closing connection from {addr}")
            self.peers.discard(addr)
            writer.close()
            await writer.wait_closed()

    async def connect_to_peer(self, peer_host: str, peer_port: int):
        """
        Connect to a peer node
        :param peer_host:
        :param peer_port:
        :return:
        """
        try:
            reader, writer = await asyncio.open_connection(peer_host, peer_port)
            addr = writer.get_extra_info('peername')
            print(f"[+] Connected to peer {addr}")

            # Handshake message
            message = json.dumps({"type": "ping"}).encode()
            writer.write(message)
            await writer.drain()

            data = await reader.read(1024)
            response = json.loads(data.decode())
            print(f"[<] Received {response} from {addr}")

        except Exception as e:
            print(f"[X] Failed to connect to {peer_host}:{peer_port} - {e}")

        finally:
            print(f"[-] Closing connection to {addr}")
            writer.close()
            await writer.wait_closed()


    def __str__(self):
        return f"{self.host}:{self.port}"
