from enum import Enum

from .action import Action

class Orientation(Enum):
    RIGHT = 0
    UP    = 1
    LEFT  = 2
    DOWN  = 3

    def turn(self, action: Action):
        return {
            Action.TURNLEFT: {
                Orientation.RIGHT: Orientation.UP,
                Orientation.UP   : Orientation.LEFT,
                Orientation.LEFT : Orientation.DOWN,
                Orientation.DOWN : Orientation.RIGHT,
            },
            Action.TURNRIGHT: {
                Orientation.RIGHT: Orientation.DOWN,
                Orientation.UP   : Orientation.RIGHT,
                Orientation.LEFT : Orientation.UP,
                Orientation.DOWN : Orientation.LEFT,
            },
        }[action][self]
