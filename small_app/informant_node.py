import socket
import json
import logging
import asyncio
from models.dht import DHT
from services.uwu_protocol.service import UWUService
from services.uwu_protocol.base_handler import UWUHandlerBase
from services.uwu_protocol.enums import MessageType, RequestAction, ResponseAction
from services.uwu_protocol.protocol import UWUProtocol

logging.basicConfig(level=logging.INFO)


class InformantNodeHandler(UWUHandlerBase):
    def __init__(self, informant_node):
        self.informant_node = informant_node

    def bind(self):
        """
        Bind actions to handler methods.
        """
        return {
            (MessageType.REQUEST, RequestAction.REGISTER): self.handle_register,
            (MessageType.REQUEST, RequestAction.GET_DHT): self.handle_get_dht,
        }

    async def handle_register(self, message, reader, writer):
        """
        Handle file registration requests from peers.
        """
        try:
            peer_info = message.get("peer_info")
            files = message.get("data", {}).get("files", [])
            if peer_info and files:
                for file in files:
                    self.informant_node.dht.add_file(
                        filename=file["filename"],
                        host=peer_info["host"],
                        port=peer_info["port"],
                        details={"size": file["size"]}
                    )
                logging.info(f"Files registered by peer {peer_info['host']}:{peer_info['port']}")
                response = UWUProtocol.create_message(MessageType.RESPONSE, ResponseAction.REGISTER_ACK, peer_info, {"data": "Files registered successfully"})
                writer.write(response)
                await writer.drain()
            else:
                logging.warning("Invalid REGISTER request received")
        except Exception as e:
            logging.error(f"Error handling REGISTER request: {e}")
            response = UWUProtocol.create_message(
                MessageType.ERROR,
                ResponseAction.REGISTER_ACK,
                {},
                {"message": "Failed to register files"}
            )
            writer.write(response)
            await writer.drain()

    async def handle_dht_update(self, message, reader, writer):
        """
        Handle DHT updates from peers.
        """
        dht_data = message.get("data", {})
        self.informant_node.update_dht(dht_data)
        response = {"type": MessageType.RESPONSE.value, "action": ResponseAction.DHT_UPDATE_ACK.value, "message": "DHT updated successfully"}
        writer.write(json.dumps(response).encode())
        await writer.drain()

    async def handle_get_dht(self, message, reader, writer):
        """
        Handle requests to retrieve the current DHT.
        """
        try:
            logging.info(f"DHT request from {message['peer_info']}")
            response = UWUProtocol.create_message(
                msg_type=MessageType.RESPONSE,
                action=ResponseAction.GET_DHT_RESPONSE,
                peer_info=message["peer_info"],
                data={"dht": self.informant_node.dht.get_all_files()}
            )
            new_reader, new_writer = await asyncio.open_connection(message["peer_info"]["host"], message["peer_info"]["port"])
            new_writer.write(response)
            await new_writer.drain()
            logging.info(f"Sending DHT response: {response.decode()}")
        except Exception as e:
            logging.error(f"Error handling GET_DHT request: {e}")
            self.send_error_from_exception(writer, e)
        finally:
            writer.close()
            await writer.wait_closed()

    def send_error_from_exception(self, writer, exception):
        """
        Send an error message in response to an exception.
        """
        error_response = UWUProtocol.create_message(
            MessageType.ERROR,
            ResponseAction.ERROR,
            {},
            {"message": str(exception) if exception else "Unknown error"}
        )
        writer.write(error_response)


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

    def get_connected_nodes(self):
        """
        Get a list of tuples (host, port) for connected nodes.
        """
        connected_nodes = []
        # The connected nodes is all the nodes present on the DHT
        for filename, file_data in self.dht.get_all_files().items():
            for host, ports in file_data["providers"].items():
                for port in ports.keys():
                    connected_nodes.append((host, int(port)))
        # remove duplicates
        connected_nodes = list(set(connected_nodes))

        return connected_nodes

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
