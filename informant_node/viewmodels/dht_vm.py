from PySide6.QtCore import QObject, Signal, Property
from informant_node.models.dht_model import DHT


class DHTViewModel(QObject):
    dhtUpdated = Signal()

    def __init__(self, dht: DHT):
        super().__init__()
        self._dht = dht

    @Property("QVariant", constant=True)
    def dhtModel(self):
        # Expose the DHT data as a dictionary to QML
        return self._dht.get_all_files()

    def add_file(self, filename, host, port):
        if self._dht.add_file(filename, host, port):
            self.dhtUpdated.emit()

    def remove_file(self, filename):
        self._dht.remove_file(filename)
        self.dhtUpdated.emit()