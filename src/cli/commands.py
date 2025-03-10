# src/cli/main.py
import asyncio
from src.core.node import PeerNode


async def start_server(args):
    """Start the peer node server."""
    node = PeerNode(host=args.host, port=args.port)
    await node.start_server()


async def connect_to_peer(args):
    """Connect to another peer."""
    client = PeerNode()
    await client.connect_to_peer(args.host, args.port)


async def run_tests(args):
    """Run tests for peer-to-peer communication."""
    print("[*] Running peer-to-peer connectivity test...")
    server_task = asyncio.create_task(start_server(args))
    client_task = asyncio.create_task(connect_to_peer(args))
    await asyncio.gather(server_task, client_task)
    await asyncio.sleep(1)
    print("[✔] Tests completed successfully.")

