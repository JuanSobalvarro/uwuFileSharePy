# main.py
import os
import sys
import asyncio
import argparse

from uwuFileShare.peer_node.models.peer_node import PeerNode


class MainApp:
    def __init__(self, shared_dir="shared_files"):
        self.node: PeerNode = PeerNode(shared_dir=shared_dir, informants=[("127.0.0.1", 6000)])
        self.gui = None

    def start_cli(self):
        """
        Starts the CLI interface for the Peer Node.
        """
        print("[+] Starting Peer Node in CLI mode...")
        self.menu()

    def start_gui(self):
        """
        Starts the Qt GUI interface for the Peer Node.
        """
        pass

    def menu(self):
        """
        CLI menu for interacting with the Peer Node.
        """
        print("[...] Waiting for server to start...")
        self.node.run()
        print("[+] Server is up and running!")

        try:
            while True:
                print("\n[Peer Node Menu]")
                print("1. Get DHT")
                print("2. List Shared Files")
                print("3. Exit")

                choice = input("Choose an option: ")

                if choice == "1":
                    print("\n[+] DHT Contents:")

                    # Make a request to the Informant node to get the DHT
                    for key, value in self.node.dht.get_all_files().items():
                        print(f"  - Filename: {key}, Host: {value[0]}, Port: {value[1]}")

                elif choice == "2":
                    print("\n[+] Shared Files:")
                    files = self.node.get_shared_files()

                    if files:
                        for file in files:
                            print(f"  - {file}")

                elif choice == "3":
                    print("[+] Shutting down the server...")
                    self.node.stop()
                else:
                    print("[!] Invalid option. Please try again.")

        except KeyboardInterrupt:
            print("[!] Interrupted by user.")

        finally:
            self.node.stop()

    def start(self, cli=True, gui=False):
        """
        Starts the Peer Node.
        """
        if cli:
            self.start_cli()
        elif gui:
            # self.start_gui()
            print("[-] GUI mode not implemented yet.")
        else:
            print("[-] No mode selected. Use --cli or --gui.")


def main():
    """
    Main function to run the Peer Node.
    """
    parser = argparse.ArgumentParser(description="Start the Peer Node.")
    parser.add_argument("--cli", action="store_true", help="Start in CLI mode.")
    parser.add_argument("--gui", action="store_true", help="Start in GUI mode.")
    parser.add_argument("--shared_dir", type=str, default="shared_files", help="Directory to share files from.")

    args = parser.parse_args()

    app = MainApp(shared_dir=args.shared_dir)
    app.start(cli=args.cli, gui=args.gui)

if __name__ == "__main__":
    main()
