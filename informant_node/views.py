import os
import sys
import asyncio

from gui_setup import GUI

from informant import InformantNode


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class InformantView:
    def __init__(self):
        self.node = InformantNode()
        self.view = None
        self.gui = None

    def start_cli(self):
        """
        Starts the CLI interface for the Informant Node.
        """
        print("[+] Starting Informant Node in CLI mode...")
        self.menu()

    def start_gui(self):
        """
        Starts the Qt GUI interface for the Informant Node.
        :return:
        """
        self.gui = GUI(
            import_path_dirs=[os.path.join(BASE_DIR, "components")],
            entry_file_path=os.path.join(BASE_DIR, "ui", "main.qml"),
        )

    def menu(self):
        # Wait until the server thread signals it's ready
        print("[...] Waiting for server to start...")
        self.node.server_ready.wait()
        print("[+] Server is up and running!")

        try:
            while True:
                print("\n[Informant Node Menu]")
                print("1. List DHT")
                print("2. Exit")
                choice = input("Choose an option: ")

                if choice == "1":
                    print("\n[+] DHT Contents:")
                    if not self.node.dht:
                        print("No files registered.")
                    for filename, (host, port) in self.node.dht.items():
                        print(f"File: {filename}, Host: {host}, Port: {port}")
                elif choice == "2":
                    print("[+] Shutting down the server...")
                    if self.node.server and self.node.loop:
                        future = asyncio.run_coroutine_threadsafe(self.node.shutdown_server(), self.node.loop)
                        future.result()  # Wait for shutdown to complete
                    break
                else:
                    print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\n[+] Keyboard interrupt received. Exiting...")
            if self.node.server and self.node.loop:
                asyncio.run_coroutine_threadsafe(self.node.shutdown_server(), self.node.loop)

    def start(self, cli=True, gui=False):
        """
        Starts the Informant Node.
        :param cli: If True, starts in CLI mode.
        :param gui: If True, starts in GUI mode.
        """
        self.node.run()
        if cli:
            try:
                self.start_cli()
            except KeyboardInterrupt:
                print("\n[+] Keyboard interrupt received. Exiting...")
                self.node.shutdown_safely()
        elif gui:
            self.start_gui()
            try:
                sys.exit(self.gui.app.exec())
            except KeyboardInterrupt:
                print("\n[+] Keyboard interrupt received. Exiting...")
                self.node.shutdown_safely()
            except Exception as e:
                print(f"[!] Error in GUI mode: {e}")
                self.node.shutdown_safely()
        else:
            print("Please choose either CLI or GUI mode.")
