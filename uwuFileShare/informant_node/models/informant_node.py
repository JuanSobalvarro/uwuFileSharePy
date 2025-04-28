# informant_node.py
import asyncio
import threading
from uwuFileShare.shared.services.uwu_protocol.service import UWUService
from uwuFileShare.shared.models.dht import DHT

from uwuFileShare.informant_node.services.uwu_protocol.handler import Handler


class InformantNode:
    def __init__(self, host="127.0.0.1", port=6000):
        self.host = host
        self.port = port
        self.dht = DHT()
        self.uwu_service = None

    @property
    def nodes_connected(self):
        """
        Returns a list of connected nodes, consider a node connected if it has a file in the DHT
        :return: List of connected nodes
        """
        print("[INFORMANT] Getting connected nodes: ", self.dht.get_nodes())
        return self.dht.get_nodes()

    def run(self):
        """
        Starts the Informant Node. Initializes the uwu service
        :return:
        """
        handler = Handler(self)

        self.uwu_service = UWUService(
            host=self.host,
            port=self.port,
            handler=handler
        )
        print("[INFORMANT] Starting the UWU service...")
        self.uwu_service.start_service()

    def stop(self):
        """
        Stops the Informant Node. Shuts down the uwu service
        :return:
        """
        if not self.uwu_service.is_running():
            print("[INFORMANT] No service to stop.")
            return

        print("[INFORMANT] Stopping the service...")
        self.uwu_service.stop_service()
