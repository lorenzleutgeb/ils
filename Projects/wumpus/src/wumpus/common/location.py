from .orientation import Orientation

class Location():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def isAdjacent(self, other):
        X1 = self.x
        X2 = other.x
        Y1 = self.y
        Y2 = other.y

        isBelow = ((X1 == X2) and (Y1 == (Y2 - 1)))
        isAbove = ((X1 == X2) and (Y1 == (Y2 + 1)))
        isLeft  = ((X1 == (X2 - 1)) and (Y1 == Y2))
        isRight = ((X1 == (X2 + 1)) and (Y1 == Y2))

        return isAbove or isBelow or isLeft or isRight

    def getAdjacent(self, orientation, n):
        if orientation == Orientation.UP:
            return Location(self.x, self.y + 1) if self.y < n else None
        elif orientation == Orientation.DOWN:
            return Location(self.x, self.y - 1) if self.y > 1 else None
        elif orientation == Orientation.LEFT:
            return Location(self.x - 1, self.y) if self.x > 1 else None
        elif orientation == Orientation.RIGHT:
            return Location(self.x + 1, self.y) if self.x < n else None

    def isAt(self, x, y):
        return self.x == x and self.y == y
