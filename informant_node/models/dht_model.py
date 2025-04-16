import json
import os
from threading import Lock
import logging

class DHT:
    def __init__(self, persistence_file="data/dht_data.json"):
        self._dht = {}
        self._lock = Lock()
        self.persistence_file = persistence_file
        self._load_persistent_data()
        logging.basicConfig(level=logging.INFO)

    def _load_persistent_data(self):
        if os.path.exists(self.persistence_file):
            with open(self.persistence_file, "r") as file:
                self._dht = json.load(file)
                logging.info("[DHT] Loaded persistent data.")

    def _save_persistent_data(self):
        with open(self.persistence_file, "w") as file:
            json.dump(self._dht, file)
            logging.info("[DHT] Saved persistent data.")

    def add_file(self, filename, host, port) -> bool:
        with self._lock:
            if filename in self._dht:
                return False
            self._dht[filename] = (host, port)
            self._save_persistent_data()
            return True

    def get_file(self, filename):
        with self._lock:
            return self._dht.get(filename, None)

    def get_all_files(self):
        with self._lock:
            return dict(self._dht)

    def remove_file(self, filename):
        with self._lock:
            if filename in self._dht:
                del self._dht[filename]
                self._save_persistent_data()
                logging.info(f"[DHT] File {filename} removed from DHT.")
            else:
                logging.warning(f"[DHT] File {filename} not found in DHT.")