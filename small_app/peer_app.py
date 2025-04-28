import argparse
from peer_node import PeerNode


def main():
    # Argument parser
    parser = argparse.ArgumentParser(description="Run the Peer Node.")
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="IP address of the Peer Node.")
    parser.add_argument("--port", type=int, default=6001, help="Port of the Peer Node.")
    parser.add_argument("--informant_ip", type=str, default="127.0.0.1", help="IP address of the Informant Node.")
    parser.add_argument("--informant_port", type=int, default=6000, help="Port of the Informant Node.")
    args = parser.parse_args()

    # Create Peer Node
    peer_node = PeerNode(
        host=args.ip,
        port=args.port,
        informant_host=args.informant_ip,
        informant_port=args.informant_port,
    )

    # Connect to Informant Node
    peer_node.connect_to_informant()

    # Example: Send a DHT update
    peer_node.send_dht_update("example_file.txt", "File details")


if __name__ == "__main__":
    main()