from runepy.ui.common import create_ui
from runepy.ui.layouts import LOADING_SCREEN_LAYOUT


class LoadingScreen:
    """Simple loading screen with a progress bar."""

    def __init__(self, base):
        self.base = base
        self.frame, widgets = create_ui(LOADING_SCREEN_LAYOUT)
        self.container = widgets.get("container")
        self.label = widgets.get("label")
        self.bar = widgets.get("bar")

    def update(self, value, text=None):
        """Update the progress bar and optional text."""
        if text is not None:
            self.label["text"] = text
        self.bar["value"] = value
        # Render a frame so updates appear even before the main loop starts
        self.base.graphicsEngine.renderFrame()

    def destroy(self):
        self.frame.destroy()
        self.frame = None
