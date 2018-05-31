from os      import stat
from os.path import exists
from stat    import S_ISFIFO
from random  import randint, random

from ..common import *

PIT_PROBABILITY = 0.2

emoji = False

GDSPC = '═' * (2 if emoji else 1) * 3
GSPC = '─' * (2 if emoji else 1) * 3
SPC = ' ' * (2 if emoji else 1)
GOLD = '🏆' if emoji else 'G'
WUMPUS = '👹' if emoji else 'W'
PIT = '⚫' if emoji else 'P'
WUMPUS_DEAD = '✨' if emoji else 'x'
AGENT = '🤖' if emoji else 'A'
ARROW = '🏹' if emoji else 'A'

MAX_ACTIONS = 1000

class World():
    def __init__(self, size=4, wumpus=None, gold=None, pits=None, optimum=None):
        self.shouldPaint = exists('world') and S_ISFIFO(stat('world').st_mode)

        self.agentLocation = Location(1,1)
        self.agentOrientation = Orientation.RIGHT
        self.agentAlive = True
        self.agentHasArrow = True
        self.agentHasGold = False
        self.agentInCave = True
        self.wumpusAlive = True
        self.pits = []
        self.gold = None
        self.optimum = optimum
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
        size, wumpus, gold, optimum, pits = 4, None, None, None, []
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
                elif ln[0] == 'optimum':
                    optimum = int(ln[1])

        # World must contain wumpus and gold!
        if wumpus == None or gold == None:
            return None

        return cls(
            size=size, wumpus=wumpus, gold=gold, pits=pits, optimum=optimum
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

            if (((self.agentOrientation == Orientation.RIGHT) and
                 (self.agentLocation.x < self.wumpus.x) and
                 (self.agentLocation.y == self.wumpus.y)) or
                ((self.agentOrientation == Orientation.UP) and
                 (self.agentLocation.x == self.wumpus.x) and
                 (self.agentLocation.y < self.wumpus.y)) or
                ((self.agentOrientation == Orientation.LEFT) and
                 (self.agentLocation.x > self.wumpus.x) and
                 (self.agentLocation.y == self.wumpus.y)) or
                ((self.agentOrientation == Orientation.DOWN) and
                 (self.agentLocation.x == self.wumpus.x) and
                 (self.agentLocation.y > self.wumpus.y))):
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

        return not self.isGameOver()

    def isGameOver(self):
        return not self.agentInCave or not self.agentAlive or self.numActions >= MAX_ACTIONS

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

    def paint(self):
        if not self.shouldPaint:
            return

        notes = [
            "  Agent has "+ARROW+": " + ('\033[32mYes\033[0m' if self.agentHasArrow else '\033[31mNo\033[0m'),
            "  Agent has "+GOLD+": " + ('\033[32mYes\033[0m' if self.agentHasGold else '\033[31mNo\033[0m'),
            "  Score:      " + SPC + str(self.getScore())
        ]

        def projAgent(l):
            return str(self.agentOrientation) if l == self.agentLocation else None

        paint(self.worldSize, [
            (self.wumpus, 'W' if self.wumpusAlive else 'w'),
            (self.pits, 'P'),
            (projAgent,),
            (self.gold, 'G' if not self.agentHasGold else 'g'),
        ], 'world', notes)

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
