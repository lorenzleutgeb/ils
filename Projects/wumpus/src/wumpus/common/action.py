from enum import Enum

class Action(Enum):
    GOFORWARD = 0
    TURNLEFT  = 1
    TURNRIGHT = 2
    GRAB      = 3
    SHOOT     = 4
    CLIMB     = 5

    def __str__(self):
        if self == Action.GOFORWARD:
            return 'F'
        elif self == Action.TURNLEFT:
            return 'L'
        elif self == Action.TURNRIGHT:
            return 'R'
        elif self == Action.GRAB:
            return 'G'
        elif self == Action.SHOOT:
            return 'S'
        elif self == Action.CLIMB:
            return 'C'
        else:
            return '?'

    def toSymbol(self):
        if self == Action.GOFORWARD:
            return 'goforward'
        elif self == Action.TURNLEFT:
            return 'turnleft'
        elif self == Action.TURNRIGHT:
            return 'turnright'
        elif self == Action.GRAB:
            return 'grab'
        elif self == Action.SHOOT:
            return 'shoot'
        elif self == Action.CLIMB:
            return 'climb'
        else:
            return '?'

    def mirror(self):
        if self == Action.TURNLEFT:
            return Action.TURNRIGHT
        elif self == Action.TURNRIGHT:
            return Action.TURNLEFT
        else:
            return self
