import copy

from direct.gui.DirectGui import (
    DirectButton,
    DirectEntry,
    DirectFrame,
    DirectLabel,
)
from direct.showbase.DirectObject import DirectObject
from panda3d.core import TextNode

from runepy.ui.common import create_ui
from runepy.ui.layouts import OPTIONS_MENU_LAYOUT


class KeyBindingManager(DirectObject):
    """Manage configurable key bindings and apply them to Panda3D events."""

    def __init__(self, base, bindings):
        super().__init__()
        self.base = base
        self.bindings = bindings.copy()
        self.callbacks = {}

    def bind(self, action, press_func, release_func=None):
        """Bind ``action`` to call the given functions."""
        self.callbacks[action] = (press_func, release_func)
        key = self.bindings.get(action)
        if key:
            self._accept(key, press_func, release_func)

    def rebind(self, action, new_key):
        """Change the key associated with ``action``."""
        old = self.bindings.get(action)
        press, release = self.callbacks.get(action, (None, None))
        if old:
            self.base.ignore(old)
            self.base.ignore(f"{old}-up")
        self.bindings[action] = new_key
        if press:
            self._accept(new_key, press, release)

    def _accept(self, key, press, release):
        self.base.accept(key, press)
        if release:
            self.base.accept(f"{key}-up", release)


class OptionsMenu:
    """Simple menu for changing key bindings."""

    def __init__(self, base, manager: KeyBindingManager):
        self.base = base
        self.manager = manager
        self.frame = None
        self.entries = {}
        self.visible = False

    def toggle(self):
        if self.visible:
            self.close()
        else:
            self.open()

    def open(self):
        if self.visible:
            return
        self.visible = True
        layout = copy.deepcopy(OPTIONS_MENU_LAYOUT)
        children = list(layout.get("children", []))
        y = 0.5
        self.entries = {}
        for action, key in self.manager.bindings.items():
            children.append({"type": "label", "text": action, "pos": (-0.6, 0, y), "scale": 0.05, "text_align": TextNode.ALeft})
            children.append({"type": "entry", "name": f"entry_{action}", "initialText": key, "pos": (0.0, 0, y), "scale": 0.05, "width": 10, "numLines": 1, "focus": 0})
            y -= 0.1
        layout["children"] = children
        self.frame, widgets = create_ui(layout, self)
        self.entries = {a: widgets.get(f"entry_{a}") for a in self.manager.bindings}

    def apply(self):
        for action, entry in self.entries.items():
            key = entry.get().strip()
            if key:
                self.manager.rebind(action, key)
        self.close()

    def close(self):
        if self.frame:
            self.frame.destroy()
            self.frame = None
        self.entries = {}
        self.visible = False
