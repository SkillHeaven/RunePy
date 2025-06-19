import json
import os

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


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
