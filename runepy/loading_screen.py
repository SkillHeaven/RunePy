from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectWaitBar


class LoadingScreen:
    """Simple loading screen with a progress bar."""

    def __init__(self, base):
        self.base = base
        # Fullscreen black background frame
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 1), frameSize=(-1, 1, -1, 1)
        )
        # Central container mimicking RuneScape's red rectangle
        self.container = DirectFrame(
            parent=self.frame,
            frameColor=(0.4, 0, 0, 1),
            frameSize=(-0.7, 0.7, -0.15, 0.15),
        )
        self.label = DirectLabel(
            text="Loading...",
            parent=self.container,
            pos=(0, 0, 0.05),
            scale=0.07,
            frameColor=(0, 0, 0, 0),
        )
        self.bar = DirectWaitBar(
            parent=self.container,
            pos=(0, 0, -0.05),
            frameSize=(-0.6, 0.6, -0.05, 0.05),
            frameColor=(0.2, 0, 0, 1),
            barColor=(1, 0, 0, 1),
            range=100,
            value=0,
        )

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
