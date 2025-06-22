import argparse
from runepy.client import Client
from runepy.editor_window import EditorWindow

from runepy.debug import get_debug

def main():
    parser = argparse.ArgumentParser(description="RunePy client")
    parser.add_argument(
        "--mode",
        choices=["game", "editor"],
        default="game",
        help="Start in regular game mode or map editor",
    )
    args = parser.parse_args()

    if args.mode == "editor":
        app = EditorWindow()
    else:
        app = Client()
    from direct.showbase.ShowBaseGlobal import base
    get_debug().attach(base)
    app.run()


if __name__ == "__main__":
    main()

