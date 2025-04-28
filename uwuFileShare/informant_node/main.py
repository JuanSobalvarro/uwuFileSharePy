import os
import sys
import asyncio
import argparse

from uwuFileShare.informant_node.models.informant_node import InformantNode
from uwuFileShare.informant_node.viewmodels import ViewModelFactory

from uwuFileShare.shared.views.gui_setup import GUI


class MainApp:
    def __init__(self):
        self.node = InformantNode()
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
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.gui = GUI(
            node=self.node,
            import_path_dirs=[os.path.join(base_dir, "views", "ui", "components")],
            entry_file_path=os.path.join(base_dir, "views", "ui", "main.qml"),
            view_models_dir=os.path.join(base_dir, "viewmodels"),
            view_model_factory=ViewModelFactory,
            resource_kwargs={"resource_dir": os.path.join(base_dir, "assets"),
                             "qrc_path": os.path.join(base_dir, "resources.qrc"),
                             "py_output_path": os.path.join(base_dir, "resources_rc.py")},
        )

    def menu(self):
        """
        CLI menu for interacting with the Informant Node.
        """
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
        Starts the Informant Node in the selected mode.
        :param cli: If True, starts in CLI mode.
        :param gui: If True, starts in GUI mode.
        """
        self.node.run()
        if cli:
            try:
                self.start_cli()
            except KeyboardInterrupt:
                print("\n[+] Keyboard interrupt received. Exiting...")
                self.node.stop()
        elif gui:
            try:
                self.start_gui()
                sys.exit(self.gui.app.exec())
            except KeyboardInterrupt:
                print("\n[+] Keyboard interrupt received. Exiting...")
                self.node.stop()
            # except Exception as e:
            #     print(f"[!] Error in GUI mode: {e}")
            #     self.node.stop()
        else:
            print("Please choose either CLI or GUI mode.")


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--gui",
        action="store_true",
        help="Start the Informant Node in GUI mode.",
    )
    arg_parser.add_argument(
        "--cli",
        action="store_true",
        help="Start the Informant Node in CLI mode.",
    )

    args = arg_parser.parse_args()

    app = MainApp()
    app.start(cli=args.cli, gui=args.gui)


if __name__ == "__main__":
    main()
