import json
import asyncio
from PySide6.QtCore import QObject, Signal, Slot, Property, QAbstractListModel, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

class QStringListWrapper(QAbstractListModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []

    def rowCount(self, parent=None):
        return len(self._data)

    def data(self, index, role):
        if index.isValid() and role == Qt.DisplayRole:
            return self._data[index.row()]
        return None

    def setStringList(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()


class GuiPeerNode(QObject):
    sharedFilesChanged = Signal()
    dhtFilesChanged = Signal()

    def __init__(self, core_node):
        super().__init__()
        self.core_node = core_node
        self._shared_model = QStringListWrapper(core_node.shared_files)
        self._dht_model = QStringListWrapper()

        # Fill DHT model
        self.updateDhtModel()

    @Slot(str)
    def addFileToShare(self, file_path):
        if file_path:
            self.core_node.shared_files.append(file_path)
            self.sharedFilesChanged.emit()
            self._shared_model.setStringList(self.core_node.shared_files)

    @Slot()
    def refreshDHT(self):
        asyncio.ensure_future(self.core_node.get_dht())
        self.updateDhtModel()

    @Slot(int)
    def downloadFile(self, index):
        dht_files = list(self.core_node.dht.keys())
        if index < 0 or index >= len(dht_files):
            return
        filename = dht_files[index]
        host, port = self.core_node.dht[filename]

        async def download():
            try:
                reader, writer = await asyncio.open_connection(host, port)
                request = {"type": "request_file", "filename": filename}
                writer.write(json.dumps(request).encode())
                await writer.drain()

                data = await reader.read(2048)
                with open(f"downloads/{filename}", "wb") as f:
                    f.write(data)

                print(f"[DOWNLOAD] Saved: downloads/{filename}")
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                print(f"[ERROR] Download failed: {e}")

        asyncio.ensure_future(download())

    def updateDhtModel(self):
        self._dht_model.setStringList(list(self.core_node.dht.keys()))
        self.dhtFilesChanged.emit()

    @Property(QAbstractListModel, notify=sharedFilesChanged)
    def sharedFiles(self):
        return self._shared_model

    @Property(QAbstractListModel, notify=dhtFilesChanged)
    def dhtFiles(self):
        return self._dht_model