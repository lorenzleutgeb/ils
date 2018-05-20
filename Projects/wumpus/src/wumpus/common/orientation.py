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

    def __str__(self):
        if self == Orientation.RIGHT:
            return '→'#'R'
        elif self == Orientation.UP:
            return '↑'#'U'
        elif self == Orientation.LEFT:
            return '←'#'L'
        elif self == Orientation.DOWN:
            return '↓'#'D'
        else:
            return '?'

    def __int__(self):
        if self == Orientation.RIGHT:
            return 0
        elif self == Orientation.UP:
            return 1
        elif self == Orientation.LEFT:
            return 2
        elif self == Orientation.DOWN:
            return 3
        else:
            return None

    def toSymbol(self):
        if self == Orientation.RIGHT:
            return 'right'#'R'
        elif self == Orientation.UP:
            return 'up'#'U'
        elif self == Orientation.LEFT:
            return 'left'#'L'
        elif self == Orientation.DOWN:
            return 'down'#'D'
        else:
            return '?'
