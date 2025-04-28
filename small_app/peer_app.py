# File: small_app/peer_app.py

import argparse
from peer_app_gui import PeerNodeGUI
from peer_node import PeerNode
from PySide6.QtWidgets import QApplication


def main():
    # Argument parser
    parser = argparse.ArgumentParser(description="Run the Peer Node GUI.")
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="IP address of the Peer Node.")
    parser.add_argument("--port", type=int, default=6001, help="Port of the Peer Node.")
    parser.add_argument("--informant_ip", type=str, default="127.0.0.1", help="IP address of the Informant Node.")
    parser.add_argument("--informant_port", type=int, default=6942, help="Port of the Informant Node.")
    parser.add_argument("--shared_dir", type=str, default=None, help="Directory to share files from.")
    args = parser.parse_args()

    # Create Peer Node
    peer_node = PeerNode(
        host=args.ip,
        port=args.port,
        informant_host=args.informant_ip,
        informant_port=args.informant_port,
        shared_dir=args.shared_dir,
    )
    peer_node.start_peer_node()


    # Connect to Informant Node
    # peer_node.connect_to_informant()

    # Start GUI
    app = QApplication([])
    gui = PeerNodeGUI(peer_node)
    gui.show()
    app.exec()

if __name__ == "__main__":
    main()
