from views import InformantView

import sys
import argparse

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

    view = InformantView()
    view.start(cli=args.cli, gui=args.gui)

if __name__ == "__main__":
    main()