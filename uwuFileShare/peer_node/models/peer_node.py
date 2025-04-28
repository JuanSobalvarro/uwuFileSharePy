import asyncio
import json
import os
import threading
import sys
from enum import Enum
from typing import List, Tuple

from uwuFileShare.shared.models.dht import DHT
from uwuFileShare.shared.services.uwu_protocol.service import UWUService

from uwuFileShare.peer_node.services.uwu_protocol.handler import Handler

class PeerNode:
    def __init__(self, host="127.0.0.1", port=5000, informants: List[Tuple[str, int]] = None, shared_dir="shared_files"):
        self.host = host
        self.port = port
        self.dht = DHT()
        self.uwu_service = None
        self.informants = informants if informants else []
        self.shared_dir = shared_dir

    def get_informants(self) -> List[Tuple[str, int]]:
        """
        Returns the informants list
        :return:
        """
        return self.informants

    def get_shared_files(self) -> List[str]:
        """
        Returns the list of shared files
        :return:
        """
        if not os.path.exists(self.shared_dir):
            os.makedirs(self.shared_dir)

        return [f for f in os.listdir(self.shared_dir) if os.path.isfile(os.path.join(self.shared_dir, f))]

    def run(self):
        """
        Starts the Peer Node. Initializes the uwu service
        :return:
        """
        handler = Handler(self)
        self.uwu_service = UWUService(
            host=self.host,
            port=self.port,
            handler=handler,
            periodical_tasks_cbk=(handler.periodical_tasks, 5)
        )

        self.uwu_service.start_service()

    def stop(self):
        """
        Stops the Peer Node. Shuts down the uwu service
        :return:
        """
        if not self.uwu_service.is_running():
            print("[PEER] No service to stop.")
            return

        print("[PEER] Stopping the service...")
        self.uwu_service.stop_service()

        sys.exit(0)
