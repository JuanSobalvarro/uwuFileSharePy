import socket
import json
import logging
from models.dht import DHT
from services.uwu_protocol.service import UWUService
from services.uwu_protocol.base_handler import UWUHandlerBase

logging.basicConfig(level=logging.INFO)


class InformantNodeHandler(UWUHandlerBase):
    def __init__(self, informant_node):
        self.informant_node = informant_node

    def bind(self):
        """
        Bind actions to handler methods.
        """
        return {
            ("REQUEST", "PEER_CONNECT"): self.handle_peer_connect,
            ("REQUEST", "PEER_DISCOVERY"): self.handle_peer_discovery,
            ("REQUEST", "DHT_UPDATE"): self.handle_dht_update,
        }

    async def handle_peer_connect(self, message, reader, writer):
        """
        Handle a peer connection request.
        """
        peer_info = message.get("peer_info")
        if peer_info:
            peer_address = f"{peer_info['host']}:{peer_info['port']}"
            self.informant_node.add_peer(peer_address)
            logging.info(f"Peer connected: {peer_address}")
            response = {"type": "PEER_CONNECT_ACK", "message": "Peer added successfully"}
            writer.write(json.dumps(response).encode())
            await writer.drain()


    async def handle_peer_discovery(self, message, reader, writer):
        """
        Handle peer discovery request from a peer node.
        """
        logging.info(f"Peer discovery request from {message['peer_info']}")
        response = {"type": "PEER_LIST", "peers": self.informant_node.get_peers()}
        writer.write(json.dumps(response).encode())
        await writer.drain()

    async def handle_dht_update(self, message, reader, writer):
        """
        Handle DHT updates from peers.
        """
        dht_data = message.get("data", {})
        self.informant_node.update_dht(dht_data)
        response = {"type": "DHT_UPDATE_ACK"}
        writer.write(json.dumps(response).encode())
        await writer.drain()


class InformantNode:
    def __init__(self, host="0.0.0.0", port=6000, persistence_file=None):
        self.host = host
        self.port = port
        self.peers = []
        self.dht = DHT(persistence_file=persistence_file)
        self.dht.bind_on_change(self.broadcast_dht)
        self.handler = InformantNodeHandler(self)

    def get_peers(self):
        """
        Get the list of connected peers.
        """
        return self.peers

    def add_peer(self, peer):
        """
        Add a peer to the list of connected peers.
        """
        if peer not in self.peers:
            self.peers.append(peer)
            logging.info(f"Added peer: {peer}")

    def update_dht(self, dht_data):
        """
        Update the DHT with data from a peer.
        """
        for filename, file_data in dht_data.items():
            for provider, details in file_data.get("providers", {}).items():
                host, port = provider
                self.dht.add_file(filename, host, port, details)

    def broadcast_dht(self):
        """
        Broadcast the DHT to all connected peers.
        """
        for peer in self.peers:
            try:
                peer_ip, peer_port = peer.split(":")
                self.send_message(
                    {"type": "REQUEST", "action": "DHT_UPDATE", "data": self.dht.get_all_files()},
                    peer_ip,
                    int(peer_port),
                )
            except Exception as e:
                logging.error(f"Failed to broadcast to peer {peer}: {e}")

    def send_message(self, message, peer_ip, peer_port):
        """
        Send a message to a peer.
        """
        try:
            with socket.create_connection((peer_ip, peer_port)) as client:
                client.sendall(json.dumps(message).encode())
                logging.info(f"Message sent to {peer_ip}:{peer_port}")
        except Exception as e:
            logging.error(f"Failed to send message to {peer_ip}:{peer_port}: {e}")

    def start_informant_node(self):
        """
        Start the informant node service.
        """
        service = UWUService(host=self.host, port=self.port, handler=self.handler)
        service.start_service()
