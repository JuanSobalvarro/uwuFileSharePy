import argparse
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QListWidget, QLabel, QPushButton, QComboBox
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import QTimer


class InformantNodeGUI(QMainWindow):
    def __init__(self, informant_node):
        super().__init__()
        self.informant_node = informant_node
        self.current_theme = "light"  # Default theme

        self.setWindowTitle("Informant Node GUI")
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Theme Selector
        theme_layout = QVBoxLayout()
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["light", "dark"])
        self.theme_selector.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(QLabel("Select Theme:"))
        theme_layout.addWidget(self.theme_selector)
        main_layout.addLayout(theme_layout)

        # DHT Table
        self.dht_table = QTableWidget(0, 3)
        self.dht_table.setHorizontalHeaderLabels(["Filename", "Host", "Ports"])
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
        self.apply_theme()

    def change_theme(self, theme):
        """
        Change the theme dynamically.
        """
        self.current_theme = theme
        self.apply_theme()

    def apply_theme(self):
        """
        Apply the selected theme to the GUI.
        """
        themes = {
            "light": {
                "background": "#ffffff",
                "text": "#1e1e1e",
                "accent": "#e0e0e0",
            },
            "dark": {
                "background": "#1e1e1e",
                "text": "#f2f2f2",
                "accent": "#2d2d30",
            },
        }

        theme = themes[self.current_theme]
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(theme["background"]))
        palette.setColor(QPalette.WindowText, QColor(theme["text"]))
        self.setPalette(palette)

        # Apply table styles
        table_style = f"""
            QTableWidget {{
                background-color: {theme['background']};
                color: {theme['text']};
                gridline-color: {theme['accent']};
            }}
            QHeaderView::section {{
                background-color: {theme['accent']};
                color: {theme['text']};
            }}
        """
        self.dht_table.setStyleSheet(table_style)

    # Other methods (refresh_data, etc.) remain unchanged

    def refresh_data(self):
        # Refresh DHT Table
        self.dht_table.setRowCount(0)
        dht_data = self.informant_node.dht.get_all_files()
        for filename, file_data in dht_data.items():
            for host, ports in file_data["providers"].items():
                row_position = self.dht_table.rowCount()
                self.dht_table.insertRow(row_position)
                self.dht_table.setItem(row_position, 0, QTableWidgetItem(filename))
                self.dht_table.setItem(row_position, 1, QTableWidgetItem(host))
                self.dht_table.setItem(row_position, 2, QTableWidgetItem(", ".join(ports.keys())))

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
    informant_node.start_informant_node()

    # Start GUI
    app = QApplication(sys.argv)
    gui = InformantNodeGUI(informant_node)
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
