# Character.py
import logging

from direct.interval.IntervalGlobal import Func, LerpPosInterval, Sequence
from panda3d.core import Vec3

from runepy.world.region import world_to_region

logger = logging.getLogger(__name__)


class Character:

    def __init__(
        self,
        render,
        loader,
        position: Vec3 | None = None,
        scale=1,
        debug=False,
        world=None,
    ):
        self.debug = debug
        if position is None:
            position = Vec3(0, 0, 0)
        self.model = loader.loadModel("models/smiley")
        self.model.reparentTo(render)
        self.model.setPos(position)
        self.model.setScale(scale)

        # Base movement speed in tiles per second
        self.speed = 1.0
        self.world = world
        if world is not None:
            self._current_region = world_to_region(
                int(position.getX()),
                int(position.getY()),
            )
        else:
            self._current_region = None

        self._active_sequence = None

    def log(self, *args, **kwargs):
        if self.debug:
            logger.debug(*args, **kwargs)

    def move_to(self, target_pos, duration, after_step=None):
        """Create a movement interval toward ``target_pos``
        taking ``duration`` seconds."""
        move_interval = LerpPosInterval(
            self.model,
            duration=duration,
            pos=target_pos,
        )
        if after_step:
            return Sequence(move_interval, Func(after_step), Func(self.stop))
        return Sequence(move_interval, Func(self.stop))

    def get_position(self):
        return self.model.getPos()

    def _check_region_update(self):
        if self.world is None:
            return
        pos = self.model.getPos()
        rx, ry = world_to_region(
            int(pos.getX()),
            int(pos.getY()),
        )
        if (rx, ry) != self._current_region:
            self._current_region = (rx, ry)
            self.world.update_streaming(
                int(pos.getX()),
                int(pos.getY()),
            )

    def stop(self):
        self.log("Movement finished")
        self._check_region_update()

    def cancel_movement(self):
        """Stop the current movement without jumping to the end position."""
        if (
            self._active_sequence is not None
            and not self._active_sequence.isStopped()
        ):
            self._active_sequence.pause()
        self._active_sequence = None

    def start_sequence(self, sequence):
        """Start a new movement sequence, cancelling any existing one."""
        self.cancel_movement()
        self._active_sequence = sequence
        sequence.start()
