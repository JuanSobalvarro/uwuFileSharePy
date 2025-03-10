import argparse
import asyncio
from src.cli.commands import start_server, connect_to_peer, run_tests


def main():
    parser = argparse.ArgumentParser(description="UwU FileShare Peer CLI")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Commands")

    # Start server command
    parser_start = subparsers.add_parser("start-server", help="Start the peer node server")
    parser_start.add_argument("--host", default="localhost", help="Host to bind the server")
    parser_start.add_argument("--port", type=int, default=6942, help="Port to bind the server")
    parser_start.set_defaults(func=start_server)

    # Connect command
    parser_connect = subparsers.add_parser("connect", help="Connect to another peer")
    parser_connect.add_argument("--host", help="Peer IP to connect to")
    parser_connect.add_argument("--port", type=int, help="Peer port to connect to")
    parser_connect.set_defaults(func=connect_to_peer)

    # Test command
    parser_test = subparsers.add_parser("test", help="Run connectivity tests")
    parser_test.set_defaults(func=run_tests)

    args = parser.parse_args()

    # Run the selected function
    asyncio.run(args.func(args))

if __name__ == "__main__":
    main()