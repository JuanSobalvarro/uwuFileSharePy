import socket
import json
import logging

logging.basicConfig(level=logging.INFO)


class PeerNode:
    def __init__(self, host="127.0.0.1", port=6001, informant_host="127.0.0.1", informant_port=6000):
        self.host = host
        self.port = port
        self.informant_host = informant_host
        self.informant_port = informant_port
        self.dht = {}

    def connect_to_informant(self):
        """
        Connect to the Informant Node and register as a peer.
        """
        try:
            with socket.create_connection((self.informant_host, self.informant_port)) as client:
                message = {
                    "type": "REQUEST",
                    "action": "PEER_CONNECT",
                    "peer_info": {"host": self.host, "port": self.port},
                }
                client.sendall(json.dumps(message).encode())
                response = json.loads(client.recv(1024).decode())
                logging.info(f"Connected to Informant Node: {response}")
        except Exception as e:
            logging.error(f"Failed to connect to Informant Node: {e}")

    def send_dht_update(self, filename, details):
        """
        Send a DHT update to the Informant Node.
        """
        try:
            with socket.create_connection((self.informant_host, self.informant_port)) as client:
                message = {
                    "type": "REQUEST",
                    "action": "DHT_UPDATE",
                    "data": {filename: {"providers": {(self.host, self.port): details}}},
                }
                client.sendall(json.dumps(message).encode())
                response = json.loads(client.recv(1024).decode())
                logging.info(f"DHT update response: {response}")
        except Exception as e:
            logging.error(f"Failed to send DHT update: {e}")