from random import randint, random

from ..common import *

PIT_PROBABILITY = 0.2

class World():
    def __init__(self, size=4, wumpus=None, gold=None, pits=None):
        self.agentLocation = Location(1,1)
        self.agentOrientation = Orientation.RIGHT
        self.agentAlive = True
        self.agentHasArrow = True
        self.agentHasGold = False
        self.agentInCave = True
        self.wumpusAlive = True
        self.pits = []
        self.gold = None
        self.wumpus = None
        self.numActions = 0
        self.percept = None

        self.worldSize = size
        self.wumpus = wumpus
        self.gold = gold
        self.pits = pits

        if self.wumpus == None:
            # Choose wumpus location (anywhere except [1,1])
            x, y = 1, 1
            while x == 1 and y == 1:
                x, y = randint(1, size), randint(1, size)

            self.wumpus = Location(x, y)

        if self.gold == None:
            # Choose gold location (anywhere except [1,1])
            x, y = 1, 1
            while x == 1 and y == 1:# or wumpus.isAt(x, y):
                x, y = randint(1, size), randint(1, size)

            self.gold = Location(x, y)

        if self.pits == None:
            # Choose pit locations (anywhere except [1,1]) and location of gold
            self.pits = []
            for x in range(1, size + 1):
                for y in range(1, size + 1):
                    if (x == 1) and (y == 1): # or gold.isAt(x, y) or wumpus.isAt(x, y):
                        continue
                    if random() >= PIT_PROBABILITY:
                        continue
                    self.pits.append(Location(x, y))

        self.percept = Percept(
            ((self.agentLocation.isAdjacent(self.wumpus)) or (self.agentLocation == self.wumpus)),
            any(map(lambda pit: pit.isAdjacent(self.agentLocation), self.pits)),
            ((not self.agentHasGold) and (self.agentLocation == self.gold)),
            False,
            False
        )

    @classmethod
    def readFrom(cls, fname):
        size, wumpus, gold, pits = 4, None, None, []
        with open(fname, 'r') as f:
            for ln in f:
                ln = ln.strip()
                if ln == '' or ln.startswith('#'):
                    continue
                ln = ln.split(' ')
                if ln[0] == 'size':
                    size = int(ln[1])
                elif ln[0] == 'wumpus':
                    wumpus = Location(int(ln[1]), int(ln[2]))
                elif ln[0] == 'gold':
                    gold = Location(int(ln[1]), int(ln[2]))
                elif ln[0] == 'pit':
                    pits.append(Location(int(ln[1]), int(ln[2])))

        # World must contain wumpus and gold!
        if wumpus == None or gold == None:
            return None

        return cls(
            size=size, wumpus=wumpus, gold=gold, pits=pits
        )

    def execute(self, action: Action):
        # We assume the agent is alive and in the cave (i.e., game not over)
        self.numActions += 1
        if action is Action.GOFORWARD:
            newLocation: Location = self.agentLocation.getAdjacent(self.agentOrientation, self.worldSize)
            if newLocation == None:
                self.percept = Percept(
                    self.percept.stench,
                    self.percept.breeze,
                    self.percept.glitter,
                    True,
                    False
                )
            else:
                self.agentLocation = newLocation
                self.percept = Percept(
                    ((self.agentLocation.isAdjacent(self.wumpus)) or (self.agentLocation == self.wumpus)),
                    any(map(lambda pit: pit.isAdjacent(self.agentLocation), self.pits)),
                    ((not self.agentHasGold) and (self.agentLocation == self.gold)),
                    False,
                    False
                )

                fallsIntoPit = any(map(lambda pit: pit == self.agentLocation, self.pits))
                eatenByWumpus = self.wumpusAlive and self.wumpus == self.agentLocation
                self.agentAlive = not (fallsIntoPit or eatenByWumpus)
        elif action in {Action.TURNLEFT, Action.TURNRIGHT}:
            self.agentOrientation = self.agentOrientation.turn(action)
            self.percept = Percept(
                self.percept.stench,
                self.percept.breeze,
                self.percept.glitter,
                False,
                False
            )
        elif action == Action.GRAB:
            if not self.agentHasGold and self.agentLocation == self.gold:
                self.agentHasGold = True
                self.percept = Percept(
                    self.percept.stench,
                    self.percept.breeze,
                    False,
                    False,
                    False
                )
        elif action == Action.SHOOT:
            if not self.agentHasArrow:
                return
            self.agentHasArrow = False
            if not self.wumpusAlive:
                return
            if self.wumpus == self.agentLocation.getAdjacent(self.agentOrientation, self.worldSize):
                self.wumpusAlive = False
                self.percept = Percept(
                    self.percept.stench,
                    self.percept.breeze,
                    self.percept.glitter,
                    False,
                    True
                )
        elif action == Action.CLIMB:
            if self.agentLocation == Location(1, 1):
                self.agentInCave = False
                self.percept = Percept(False, False, False, False, False)

    def isGameOver(self):
        return not self.agentInCave or not self.agentAlive

    def getScore(self):
        # -1 for each action
        score = -self.numActions

        # -10 for shooting the arrow (already lost 1 for the action)
        if not self.agentHasArrow:
            score = score - 9

        # +1000 for leaving the cave with the gold
        if self.agentHasGold and not self.agentInCave:
            score = score + 1000

        # -1000 for dying
        if not self.agentAlive:
            score = score - 1000

        return score

    def printTo(self, ps):
        # Print top line
        ps.write("  ╔")
        for x in range(1, self.worldSize):
            ps.write("═══╤")
        ps.write("═══╗\n")
        # Print each row, starting at top
        for y in list(range(1, self.worldSize + 1))[::-1]:
            # Print wumpus/gold/pit line
            ps.write(str(y) + " ║")
            for x in range(1, self.worldSize + 1):
                if self.wumpus.isAt(x, y):
                    if self.wumpusAlive:
                        ps.write("W")
                    else:
                        ps.write("x")
                else:
                    ps.write(" ")
                if (not self.agentHasGold) and (self.gold.isAt(x, y)):
                    ps.write("G")
                else:
                    ps.write(" ")
                isPit = False
                for pit in self.pits:
                    if pit.isAt(x, y):
                        isPit = True
                        break
                if isPit:
                    ps.write("P")
                else:
                    ps.write(" ")
                if x < self.worldSize:
                    ps.write("│")
                else:
                    ps.write("║")
            ps.write("\n  ║")
            # Print agent line
            for x in range(1, self.worldSize + 1):
                if self.agentAlive and (self.agentLocation.isAt(x, y)):
                    ps.write(" A" + str(self.agentOrientation))
                else:
                    ps.write("   ")

                if x < self.worldSize:
                    ps.write("│")
                else:
                    ps.write("║")
            ps.write("\n")
        # /*
        # # Print empty next line
        # ps.write("|"
        # for (x = 1 x <= worldSize x++)
        # {
        #     ps.write("   |"
        # }
        # ps.write(endl
        # */
            if y == 1:
                continue
            # Print boundary line
            ps.write("  ╟")
            for x in range(1, self.worldSize):
                ps.write("───┼")
            ps.write("───╢\n")

        # Print bottom line
        ps.write("  ╚")
        for x in range(1, self.worldSize):
            ps.write("═══╧")
        ps.write("═══╝\n")

        ps.write("   ")
        for x in range(1, self.worldSize):
            ps.write(" " + str(x) + "  ")
        ps.write(" " + str(self.worldSize) + "\n")

        ps.write("State{hasGold=" + str(self.agentHasGold) + ", hasArrow=" + str(self.agentHasArrow) + ", score=" + str(self.getScore()) + "}\n")
        ps.write(str(self.percept) + "\n")

    def writeTo(self, fname):
        with open(fname, 'w') as f:
            f.write('\n'.join(
                [
                    'size {}'.format(self.worldSize),
                    'wumpus {} {}'.format(self.wumpus.x, self.wumpus.y),
                    'gold {} {}'.format(self.gold.x, self.gold.y)
                ] + [
                    'pit {} {}'.format(pit.x, pit.y) for pit in self.pits
                ] + [
                    ''
                ]
            ))
