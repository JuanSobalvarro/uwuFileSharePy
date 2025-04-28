import json
import os
from threading import Lock
import logging

PERSISTENCE_DEFAULT_FILE = os.path.join(os.path.dirname(__file__), "data", "dht_persistence.json")


class DHT:
    """
    Distributed Hash Table (DHT) for file sharing.
    """
    def __init__(self, persistence_file=None):
        self._dht = {}
        self._lock = Lock()
        self._node_files = {}  # (host, port) -> set of filenames
        self.persistence_file = persistence_file
        self._on_change = None  # Hook for ViewModel

        logging.basicConfig(level=logging.INFO)

        if self.persistence_file:
            logging.info(f"[DHT] Initializing persistence file: {self.persistence_file}")
            self._load_persistent_data()

    def _load_persistent_data(self):
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, "r") as file:
                    self._dht = json.load(file)
                    logging.info("[DHT] Loaded persistent data.")
                    self._rebuild_node_files()
            except (json.JSONDecodeError, IOError):
                logging.warning("[DHT] Failed to load persistent data. Starting fresh.")

    def _save_persistent_data(self):
        if self.persistence_file:
            try:
                with open(self.persistence_file, "w") as file:
                    json.dump(self._dht, file, indent=4)
                    logging.info("[DHT] Saved persistent data.")
            except IOError as e:
                logging.error(f"[DHT] Failed to save persistent data: {e}")

    def bind_on_change(self, callback):
        self._on_change = callback

    def _notify_change(self):
        logging.info("[DHT] DHT changed, notifying...")
        if self._on_change:
            self._on_change()
        self._save_persistent_data()

    def _rebuild_node_files(self):
        """
        Rebuilds the _node_files index from the current DHT.
        """
        self._node_files.clear()
        for filename, file_data in self._dht.items():
            for host, ports in file_data.get("providers", {}).items():
                for port in ports.keys():
                    self._node_files.setdefault((host, int(port)), set()).add(filename)

    def __create_file_entry(self, filename: str, host: str, port: int, details: dict):
        self._dht[filename] = {
            "providers": {
                host: {
                    str(port): {"details": details}
                }
            }
        }

    def add_file(self, filename: str, host: str, port: int, details: dict):
        with self._lock:
            entry = self._dht.get(filename)

            if entry:
                host_entry = entry["providers"].get(host)
                if host_entry:
                    host_entry[str(port)] = {"details": details}
                else:
                    entry["providers"][host] = {str(port): {"details": details}}
            else:
                self.__create_file_entry(filename, host, port, details)

            self._node_files.setdefault((host, port), set()).add(filename)
            self._notify_change()

    def remove_file(self, filename: str, host: str, port: int):
        with self._lock:
            if filename in self._dht:
                providers = self._dht[filename]["providers"]
                if host in providers and str(port) in providers[host]:
                    del providers[host][str(port)]
                    if not providers[host]:
                        del providers[host]
                if not providers:
                    del self._dht[filename]

                if (host, port) in self._node_files:
                    self._node_files[(host, port)].discard(filename)
                    if not self._node_files[(host, port)]:
                        del self._node_files[(host, port)]

                self._notify_change()

    def remove_all_files_for_node(self, host: str, port: int):
        with self._lock:
            filenames = self._node_files.get((host, port), set()).copy()
            for filename in filenames:
                self.remove_file(filename, host, port)

    def update_node_files(self, host: str, port: int, files: list):
        with self._lock:
            current_filenames = {file["filename"] for file in files}
            old_filenames = self._node_files.get((host, port), set()).copy()

            # Add or update provided files
            for file in files:
                self.add_file(file["filename"], host, port, {"size": file["size"]})

            # Remove stale files
            stale_files = old_filenames - current_filenames
            for filename in stale_files:
                self.remove_file(filename, host, port)

            self._notify_change()

    def get_all_files(self) -> dict:
        with self._lock:
            return self._dht.copy()
