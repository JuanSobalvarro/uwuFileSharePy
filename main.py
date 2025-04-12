# main.py
import sys
import asyncio
import argparse

from p2p.peer import PeerNode
from config import HOST, PORT, SHARED_FOLDER, INFORMANTS


async def run_peer_node(host, port, share_dir, menu):
    peer = PeerNode(host=host, port=port, informants=INFORMANTS, share_dir=share_dir)
    try:
        await peer.run(with_menu=menu)
    except KeyboardInterrupt:
        print("[!] Interrupted by user.")
    finally:
        await peer.stop()


def main():
    parser = argparse.ArgumentParser(description="P2P Peer Node")
    parser.add_argument('--port', type=int, default=PORT, help="Port to listen on")
    parser.add_argument('--share-dir', type=str, default=SHARED_FOLDER, help="Directory to share files from")
    parser.add_argument('--menu', action='store_true', help="Enable interactive menu")
    args = parser.parse_args()

    asyncio.run(run_peer_node(HOST, args.port, args.share_dir, args.menu))


if __name__ == "__main__":
    main()
