from enum import Enum

from .action import Action

class Orientation(Enum):
    RIGHT = 0
    UP    = 1
    LEFT  = 2
    DOWN  = 3

    def turn(self, action: Action):
        if action == Action.TURNLEFT:
            if self == Orientation.RIGHT:
                return Orientation.UP
            elif self == Orientation.UP:
                return Orientation.LEFT
            elif self == Orientation.LEFT:
                return Orientation.DOWN
            elif self == Orientation.DOWN:
                return Orientation.RIGHT
        elif action == Action.TURNRIGHT:
            if self == Orientation.RIGHT:
                return Orientation.DOWN
            elif self == Orientation.UP:
                return Orientation.RIGHT
            elif self == Orientation.LEFT:
                return Orientation.UP
            elif self == Orientation.DOWN:
                return Orientation.LEFT
        else:
            return None

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
