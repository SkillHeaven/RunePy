from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData
from runepy.loading_screen import LoadingScreen


class BaseApp(ShowBase):
    """Application base that shows a loading screen and defers setup."""

    def __init__(self):
        # Set a consistent default window size before ShowBase initializes
        loadPrcFileData("", "win-size 800 600")
        super().__init__()
        self.loading_screen = LoadingScreen(self)
        self.loading_screen.update(0, "Initializing")
        self.taskMgr.doMethodLater(0, self._init_app, "initApp")

    def _init_app(self, task):
        self.disableMouse()
        self.initialize()
        self.loading_screen.update(100, "Done")
        self.taskMgr.doMethodLater(1.0, self._remove_loading_screen, "hideLoading")
        return task.done

    def initialize(self):
        """Subclasses should override this to perform their setup."""
        raise NotImplementedError

    def _remove_loading_screen(self, task):
        if hasattr(self, "loading_screen") and self.loading_screen:
            self.loading_screen.destroy()
            self.loading_screen = None
        return task.done
