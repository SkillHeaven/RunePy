import json
import os

_ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(_ROOT_DIR, "config")
os.makedirs(CONFIG_DIR, exist_ok=True)
DEFAULT_CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
DEFAULT_STATE_PATH = os.path.join(CONFIG_DIR, "state.json")


def load_config(path: str = DEFAULT_CONFIG_PATH) -> dict:
    """Load the configuration file if it exists."""
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def load_key_bindings(path: str = DEFAULT_CONFIG_PATH) -> dict:
    """Return the ``key_bindings`` section of the config file."""
    config = load_config(path)
    bindings = config.get("key_bindings", {})
    if isinstance(bindings, dict):
        return bindings
    return {}


def load_state(path: str = DEFAULT_STATE_PATH) -> dict:
    """Load persistent game state such as camera or character position."""
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_state(state: dict, path: str = DEFAULT_STATE_PATH) -> None:
    """Write ``state`` to ``path`` as JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f)
