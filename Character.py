#Character.py
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import *

class Character:

    def __init__(self, render, loader, position=Vec3(0, 0, 0), scale=1):
        self.model = loader.loadModel("models/smiley")
        self.model.reparentTo(render)
        self.model.setPos(position)
        self.model.setScale(scale)
        self.walking_speed = 1.0

    def move_to(self, target_pos):
        print(f"Inside move_to. Target: {target_pos}")
        start_pos = self.model.getPos()
        distance = (target_pos - start_pos).length()  # Calculate the distance to the target
        duration = distance / self.walking_speed      # Calculate the time it will take

        move_sequence = Sequence(
            LerpPosInterval(self.model, duration=duration, pos=target_pos),
            Func(self.stop)
        )

        return move_sequence

    def get_position(self):
        return self.model.getPos()

    def stop(self):
        pass