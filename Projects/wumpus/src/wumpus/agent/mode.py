from enum import Enum

class Mode(Enum):
    EXPLORE = 0
    ESCAPE  = 1
    KILL    = 2

    def __str__(self):
        if self == Mode.EXPLORE:
            return 'explore'
        elif self == Mode.ESCAPE:
            return 'escape'
        elif self == Mode.KILL:
            return 'kill'
        else:
            return '?'

    def toSymbol(self):
        if self == Mode.EXPLORE:
            return 'explore'
        elif self == Mode.ESCAPE:
            return 'escape'
        elif self == Mode.KILL:
            return 'kill'
        else:
            return '?'
