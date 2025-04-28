import argparse
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QListWidget, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QTimer
import sys


class InformantNodeGUI(QMainWindow):
    def __init__(self, informant_node):
        super().__init__()
        self.informant_node = informant_node

        self.setWindowTitle("Informant Node GUI")
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # DHT Table
        self.dht_table = QTableWidget(0, 3)
        self.dht_table.setHorizontalHeaderLabels(["Filename", "IP Host", "Port"])
        self.dht_table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.dht_table)

        # Nodes List
        nodes_layout = QVBoxLayout()
        self.nodes_list = QListWidget()
        nodes_layout.addWidget(QLabel("Connected Nodes:"))
        nodes_layout.addWidget(self.nodes_list)
        main_layout.addLayout(nodes_layout)

        # Informant Node Info
        info_layout = QVBoxLayout()
        self.node_info_label = QLabel(f"Informant Node: {self.informant_node.host}:{self.informant_node.port}")
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)
        info_layout.addWidget(self.node_info_label)
        info_layout.addWidget(self.refresh_button)
        main_layout.addLayout(info_layout)

        # Timer to auto-refresh data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(5000)  # Refresh every 5 seconds

        self.refresh_data()

    def refresh_data(self):
        # Refresh DHT Table
        self.dht_table.setRowCount(0)
        dht_data = self.informant_node.dht.get_all_files()
        for filename, file_data in dht_data.items():
            for (host, port), details in file_data["providers"].items():
                row_position = self.dht_table.rowCount()
                self.dht_table.insertRow(row_position)
                self.dht_table.setItem(row_position, 0, QTableWidgetItem(filename))
                self.dht_table.setItem(row_position, 1, QTableWidgetItem(host))
                self.dht_table.setItem(row_position, 2, QTableWidgetItem(str(port)))

        # Refresh Nodes List
        self.nodes_list.clear()
        for peer in self.informant_node.get_peers():
            self.nodes_list.addItem(peer)


def main():
    # Argument parser
    parser = argparse.ArgumentParser(description="Run the Informant Node GUI.")
    parser.add_argument("--ip", type=str, default="0.0.0.0", help="IP address to bind the Informant Node.")
    parser.add_argument("--port", type=int, default=6000, help="Port to bind the Informant Node.")
    args = parser.parse_args()

    from informant_node import InformantNode

    # Create Informant Node
    persistence_file = "dht_persistence.json"
    informant_node = InformantNode(host=args.ip, port=args.port, persistence_file=persistence_file)
    informant_node.add_peer("127.0.0.1:6001")
    informant_node.add_peer("127.0.0.1:6002")

    # Start GUI
    app = QApplication(sys.argv)
    gui = InformantNodeGUI(informant_node)
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()