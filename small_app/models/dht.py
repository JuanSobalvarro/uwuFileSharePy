import json
import os
from threading import Lock
import logging

PERSISTENCE_DEFAULT_FILE = os.path.join(os.path.dirname(__file__), "data", "dht_persistence.json")

class DHT:
    """
    This class represents a Distributed Hash Table (DHT) for file sharing. This DHT has this structure:
    {
        "filename": {
            "providers": {
                "host": {
                    "port": { "details": "details" },
                    ...
                }
            }
        }
    }
    """
    def __init__(self, persistence_file=None):
        self._dht = {}
        self._lock = Lock()
        self.persistence_file = persistence_file
        self._on_change = None  # Hook for ViewModel

        logging.basicConfig(level=logging.INFO)

        if self.persistence_file:
            print(f"[INFO] Initializing persistence file: {self.persistence_file}")
            self._load_persistent_data()

    def _load_persistent_data(self):
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, "r") as file:
                    self._dht = json.load(file)
                    logging.info("[DHT] Loaded persistent data.")
            except (json.JSONDecodeError, IOError):
                logging.warning("[DHT] Failed to load persistent data. Starting fresh.")
                self._dht = {}

    def _save_persistent_data(self):
        try:
            with open(self.persistence_file, "w") as file:
                json.dump(self._dht, file, indent=4)
                logging.info("[DHT] Saved persistent data.")
        except IOError as e:
            logging.error(f"[DHT] Failed to save persistent data: {e}")

    def bind_on_change(self, callback):
        self._on_change = callback

    def _notify_change(self):
        print("[DHT] DHT changed, notifying...")
        if self._on_change:
            self._on_change()

    def __create_file_entry(self, filename: str, host: str, port: int, details: str = None):
        """
        Creates a new file entry in the DHT.
        """
        self._dht[filename] = {
            "providers": {
                host: {
                    str(port): details
                }
            }
        }

    def add_file(self, filename: str, host: str, port: int, details: str = None):
        with self._lock:
            entry = self._dht.get(filename)

            if entry:
                host_entry = entry["providers"].get(host)
                if host_entry:
                    # Update or add the port entry
                    host_entry[str(port)] = details
                else:
                    # Add a new host entry
                    entry["providers"][host] = {str(port): details}
            else:
                self.__create_file_entry(filename, host, port, details)

            self._notify_change()

    def remove_file(self, filename, host, port):
        with self._lock:
            if filename in self._dht:
                # Check if the host exists in the providers
                host_entry = self._dht[filename]["providers"].get(host)
                if host_entry and str(port) in host_entry:
                    del host_entry[str(port)]
                    # Remove the host if no ports remain
                    if not host_entry:
                        del self._dht[filename]["providers"][host]

                if self.persistence_file:
                    self._save_persistent_data()

                logging.info(f"[DHT] File '{filename}' removed from DHT.")
                self._notify_change()

    def update_node_files(self, files: list[tuple[str, str]], host: str, port: int):
        with self._lock:
            filenames = [filename for filename, _ in files]
            detail_of_filename = {filename: detail for filename, detail in files}

            # First, add or update files
            for filename in filenames:
                if filename not in self._dht.keys():
                    self.__create_file_entry(filename, host, port, detail_of_filename[filename])
                    continue
                self._dht[filename]["providers"].setdefault(host, {})[str(port)] = detail_of_filename[filename]

            # Then, prepare to remove old files
            to_remove = []
            for filename, value in self._dht.items():
                if host in value["providers"] and str(port) in value["providers"][host]:
                    if filename not in filenames:
                        to_remove.append(filename)

            for filename in to_remove:
                if len(self._dht[filename]["providers"][host]) == 1:
                    del self._dht[filename]["providers"][host]
                else:
                    del self._dht[filename]["providers"][host][str(port)]

                if not self._dht[filename]["providers"]:
                    del self._dht[filename]

            if self.persistence_file:
                self._save_persistent_data()

            self._notify_change()

    def get_all_files(self) -> dict:
        """
        Returns all files in the DHT.
        """
        with self._lock:
            print(f"[DHT] Getting all files: {self._dht}")
            return self._dht.copy()

    def get_nodes(self):
        """
        Retrieve all nodes in the DHT.
        """
        with self._lock:
            nodes = set()
            for filename, data in self._dht.items():
                for host, ports in data.get("providers", {}).items():
                    for port in ports:
                        nodes.add((host, int(port)))

            print(f"[DHT] Getting nodes: {nodes}")
            return list(nodes)