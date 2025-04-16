# viewmodels/informant_viewmodel.py
from PySide6.QtCore import QObject, Signal, Property
from informant_node.models.informant_node import InformantNode

class InformantViewModel(QObject):
    dhtUpdated = Signal()

    def __init__(self):
        super().__init__()
        self.node = InformantNode()
        self.node.run()

    def get_dht(self):
        return self.node.dht

    def update_dht(self):
        self.dhtUpdated.emit()