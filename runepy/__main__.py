"""Minimal entry point that enables the debug overlay."""

from direct.showbase.ShowBase import ShowBase

from runepy.debug import get_debug


def main() -> None:
    """Launch a bare :class:`ShowBase` with the debug manager attached."""

    base = ShowBase()  # ShowBase must exist before attaching
    get_debug().attach(base)

    # (rest of your setup would go here)
    base.run()


if __name__ == "__main__":
    main()

