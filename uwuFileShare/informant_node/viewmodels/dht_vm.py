from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, QByteArray, QMetaObject, Slot
from uwuFileShare.shared.models.dht import DHT


class DHTViewModel(QAbstractListModel):
    FileNameRole = Qt.UserRole + 1
    HostRole = Qt.UserRole + 2
    PortRole = Qt.UserRole + 3
    DetailsRole = Qt.UserRole + 4

    def __init__(self, dht: DHT):
        super().__init__()
        self._dht: DHT = dht
        self._entries = self._build_entries()
        self._dht.bind_on_change(self.on_dht_changed)

    def _build_entries(self):
        print("[DHT_VM] Building entries: ", self._dht.get_all_files())
        entries = []
        for filename, data in self._dht.get_all_files().items():
            for (host, port), details in data.get("providers", {}).items():
                entries.append({
                    "fileName": filename,
                    "host": host,
                    "port": port,
                    "details": details,
                })
        return entries

    def rowCount(self, parent=QModelIndex()):
        return len(self._entries)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        entry = self._entries[index.row()]
        if role == self.FileNameRole:
            return entry["fileName"]
        if role == self.HostRole:
            return entry["host"]
        if role == self.PortRole:
            return entry["port"]
        if role == self.DetailsRole:
            return entry["details"]
        return None

    def roleNames(self):
        return {
            self.FileNameRole: QByteArray(b"fileName"),
            self.HostRole: QByteArray(b"host"),
            self.PortRole: QByteArray(b"port"),
            self.DetailsRole: QByteArray(b"details"),
        }

    def on_dht_changed(self):
        print("[DHT_VM] DHT change received, scheduling GUI update from asyncio...")
        QMetaObject.invokeMethod(self, "_refresh_model", Qt.QueuedConnection)

    @Slot()
    def _refresh_model(self):
        print("[DHT_VM] Refreshing model in Qt thread...")
        self.beginResetModel()
        self._entries = self._build_entries()
        self.endResetModel()
