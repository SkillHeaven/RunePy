#Character.py
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import Func, LerpPosInterval, Sequence

class Character:

    def __init__(self, render, loader, position=Vec3(0, 0, 0), scale=1, debug=False):
        self.debug = debug
        self.model = loader.loadModel("models/smiley")
        self.model.reparentTo(render)
        self.model.setPos(position)
        self.model.setScale(scale)

        # Base movement speed in tiles per second
        self.speed = 1.0

        self._active_sequence = None

    def log(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def move_to(self, target_pos, duration):
        """Create a movement interval towards ``target_pos`` taking ``duration`` seconds."""
        self.log(f"Inside move_to. Target: {target_pos} Duration: {duration}")

        move_interval = LerpPosInterval(self.model, duration=duration, pos=target_pos)
        return Sequence(move_interval, Func(self.stop))

    def get_position(self):
        return self.model.getPos()

    def stop(self):
        self.log("Movement finished")

    def cancel_movement(self):
        """Stop the current movement without jumping to the end position."""
        if self._active_sequence is not None and not self._active_sequence.isStopped():
            self._active_sequence.pause()
        self._active_sequence = None

    def start_sequence(self, sequence):
        """Start a new movement sequence, cancelling any existing one."""
        self.cancel_movement()
        self._active_sequence = sequence
        sequence.start()
