from .orientation import Orientation

class Location():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def isAdjacent(self, other):
        x1, y1 = self
        x2, y2 = other

        isBelow = ((x1 == x2) and (y1 == (y2 - 1)))
        isAbove = ((x1 == x2) and (y1 == (y2 + 1)))
        isLeft  = ((x1 == (x2 - 1)) and (y1 == y2))
        isRight = ((x1 == (x2 + 1)) and (y1 == y2))

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

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def __len__(self):
        return 2

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError('')

    def __eq__(self, other):
        if other == None:
            return False

        if type(other) != Location:
            raise ValueError('Cannot compare ' + str(type(other)) + ' to Location!')

        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash(str(self))
