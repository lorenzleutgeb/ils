from enum import Enum

class Mode(Enum):
    EXPLORE = 0
    ESCAPE  = 1
    KILL    = 2
    GRAB    = 3

    def __str__(self):
        if self == Mode.EXPLORE:
            return 'explore'
        elif self == Mode.ESCAPE:
            return 'escape'
        elif self == Mode.KILL:
            return 'kill'
        elif self == Mode.GRAB:
            return 'grab'
        else:
            return '?'

    def toSymbol(self):
        if self == Mode.EXPLORE:
            return 'explore'
        elif self == Mode.ESCAPE:
            return 'escape'
        elif self == Mode.KILL:
            return 'kill'
        elif self == Mode.GRAB:
            return 'grab'
        else:
            return '?'
