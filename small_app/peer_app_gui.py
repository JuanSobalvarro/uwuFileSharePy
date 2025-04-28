from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QLabel, QGroupBox, QComboBox
)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QPalette
import os


class PeerNodeGUI(QMainWindow):
    def __init__(self, peer_node):
        super().__init__()
        self.peer_node = peer_node
        self.current_theme = "light"  # Default theme

        self.setWindowTitle("Peer Node GUI")
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Theme Selector
        theme_layout = QHBoxLayout()
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["light", "dark"])
        self.theme_selector.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(QLabel("Select Theme:"))
        theme_layout.addWidget(self.theme_selector)
        main_layout.addLayout(theme_layout)

        # Shared Directory Section
        dir_layout = QHBoxLayout()
        self.shared_dir_label = QLabel(f"Shared Directory: {self.peer_node.shared_dir}")
        self.change_dir_button = QPushButton("Change Directory")
        self.change_dir_button.clicked.connect(self.change_shared_dir)
        dir_layout.addWidget(self.shared_dir_label)
        dir_layout.addWidget(self.change_dir_button)
        main_layout.addLayout(dir_layout)

        # Shared Files Section
        shared_files_group = QGroupBox("Shared Files (Local)")
        shared_files_layout = QVBoxLayout()
        self.shared_files_table = QTableWidget(0, 2)
        self.shared_files_table.setHorizontalHeaderLabels(["Filename", "Size"])
        shared_files_layout.addWidget(self.shared_files_table)
        shared_files_group.setLayout(shared_files_layout)
        main_layout.addWidget(shared_files_group)

        # DHT Files Section
        dht_files_group = QGroupBox("DHT Files (External)")
        dht_files_layout = QVBoxLayout()
        self.dht_files_table = QTableWidget(0, 4)
        self.dht_files_table.setHorizontalHeaderLabels(["Filename", "Size", "IP", "Port"])
        dht_files_layout.addWidget(self.dht_files_table)
        self.download_button = QPushButton("Download Selected File")
        self.download_button.clicked.connect(self.download_file)
        dht_files_layout.addWidget(self.download_button)
        dht_files_group.setLayout(dht_files_layout)
        main_layout.addWidget(dht_files_group)

        # Timer to refresh both tables
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_tables)
        self.timer.start(5000)  # Refresh every 5 seconds

        self.refresh_tables()
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
                "background": "#f8f9fa",  # Soft light gray
                "text": "#2c2c2c",  # Darker text for better contrast
                "accent": "#d8bfd8",  # Pastel purple for accents
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
        self.shared_files_table.setStyleSheet(table_style)
        self.dht_files_table.setStyleSheet(table_style)

    # Other methods (change_shared_dir, refresh_tables, etc.) remain unchanged

    def change_shared_dir(self):
        """
        Change the shared directory.
        """
        new_dir = QFileDialog.getExistingDirectory(self, "Select Shared Directory")
        if new_dir:
            self.peer_node.shared_dir = new_dir
            self.shared_dir_label.setText(f"Shared Directory: {new_dir}")
            self.refresh_tables()

    def refresh_tables(self):
        """
        Refresh both the shared files and DHT files tables.
        """
        self.refresh_shared_files()
        self.refresh_dht_files()

    def refresh_shared_files(self):
        """
        Refresh the list of files shared by this node.
        """
        self.shared_files_table.setRowCount(0)
        for filename in os.listdir(self.peer_node.shared_dir):
            file_path = os.path.join(self.peer_node.shared_dir, filename)
            if os.path.isfile(file_path):
                row_position = self.shared_files_table.rowCount()
                self.shared_files_table.insertRow(row_position)
                self.shared_files_table.setItem(row_position, 0, QTableWidgetItem(filename))
                self.shared_files_table.setItem(row_position, 1, QTableWidgetItem(str(os.path.getsize(file_path))))

    def refresh_dht_files(self):
        """
        Refresh the list of files available in the DHT (external files).
        """
        self.dht_files_table.setRowCount(0)
        dht_data = self.peer_node.dht  # Use the updated DHT structure
        print(f"[PEER_GUI] DHT to be rendered: ", dht_data)

        for filename, file_info in dht_data.items():
            providers = file_info.get("providers", {})
            for host, ports in providers.items():
                for port, port_data in ports.items():
                    details = port_data.get("details", {})
                    file_size = details.get("size", "Unknown")

                    # Skip files shared by this node
                    if host == self.peer_node.host and int(port) == self.peer_node.port:
                        continue

                    row_position = self.dht_files_table.rowCount()
                    self.dht_files_table.insertRow(row_position)
                    self.dht_files_table.setItem(row_position, 0, QTableWidgetItem(filename))
                    self.dht_files_table.setItem(row_position, 1, QTableWidgetItem(str(file_size)))
                    self.dht_files_table.setItem(row_position, 2, QTableWidgetItem(host))
                    self.dht_files_table.setItem(row_position, 3, QTableWidgetItem(str(port)))

    def download_file(self):
        """
        Download the selected file from the selected peer.
        """
        selected_row = self.dht_files_table.currentRow()
        if selected_row == -1:
            return  # No row selected

        filename = self.dht_files_table.item(selected_row, 0).text()
        host = self.dht_files_table.item(selected_row, 2).text()
        port = int(self.dht_files_table.item(selected_row, 3).text())

        save_path = QFileDialog.getSaveFileName(self, "Save File", filename)[0]
        if save_path:
            self.peer_node.download_file(filename, host, port, save_path)