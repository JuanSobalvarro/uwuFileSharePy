# viewmodels/informant_viewmodel.py
from PySide6.QtCore import QObject, Signal, Property, QTimer, QAbstractListModel, QModelIndex, Qt, QByteArray
from PySide6.QtQml import ListProperty, QmlElement

from ..models.informant_node import InformantNode


class InformantViewModel(QObject):
    def __init__(self, node):
        super().__init__()
        self._node = node
        self._connected_nodes_model = ConnectedNodesModel(node)

    @Property(QObject)
    def connectedNodesModel(self):
        return self._connected_nodes_model

class ConnectedNodesModel(QAbstractListModel):
    HostRole      = Qt.UserRole + 1
    PortRole      = Qt.UserRole + 2
    FilesCountRole = Qt.UserRole + 3

    def __init__(self, node, parent=None):
        super().__init__(parent)
        self._node = node
        self._entries = []
        self.refresh()

    def rowCount(self, parent=QModelIndex()):
        return len(self._entries)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return None
        entry = self._entries[index.row()]
        if role == self.HostRole:       return entry["host"]
        if role == self.PortRole:       return entry["port"]
        if role == self.FilesCountRole: return entry["files"]
        return None

    def roleNames(self):
        return {
            self.HostRole:       QByteArray(b"host"),
            self.PortRole:       QByteArray(b"port"),
            self.FilesCountRole: QByteArray(b"files")
        }

    def refresh(self):
        """
        Call this whenever `node.nodes_connected` changes.
        """
        new_data = [
            {"host": host, "port": port, "files": len(files)}
            for host, port, files in self._node.nodes_connected
        ]
        self.beginResetModel()
        self._entries = new_data
        self.endResetModel()