from os.path    import dirname, join
from subprocess import PIPE, STDOUT, run
from tempfile   import mkstemp

from ..common import Action, Orientation

class ASPAgent():
    def __init__(self, n):
        self.n = n
        # Initially we do not know about stench/breeze/glitter
        # anywhere.
        self.world = [[(None, None, None) for i in range(n)] for j in range(n)]
        self.position = (0, 0)
        self.orientation = Orientation.RIGHT

    def process(self, percept):
        stench = percept.stench
        breeze = percept.breeze
        glitter = percept.glitter
        bump = percept.bump
        scream = percept.scream

        if bump:
            print("We bumped. Should never happen.")

        self.world[self.position[0]][self.position[1]] = (stench == 1, breeze == 1, glitter == 1)

        perception = [
            "#const n = " + str(self.n) + ".",
            "position(" + str(self.position[0]) + "," + str(self.position[1]) + ").",
            "orientation(" + self.orientation.toSymbol() + ")."
        ]

        for i, row in enumerate(self.world):
            for j, (stench, breeze, glitter) in enumerate(row):
                if stench is not None:
                    prefix = "-" if not stench else ""
                    perception.append(prefix + "stench({},{}).".format(i,j))
                if breeze is not None:
                    prefix = "-" if not breeze else ""
                    perception.append(prefix + "breeze({},{}).".format(i,j))
                if glitter is not None:
                    prefix = "-" if not stench else ""
                    perception.append(prefix + "glitter({},{}).".format(i,j))

        d = dirname(__file__)
        proc = run(
            [
                'dlv',
                '-silent',
                join(d, 'constants.asp'),
                join(d, 'agent.asp'),
                '--'
            ],
            stderr=STDOUT,
            stdout=PIPE,
            input="\n".join(perception),
            encoding='utf-8'
        )

        print(proc.stdout)

        # 1. Add the knowledge that we obtain as percepts to
        #    our model/state of the world. We should
        #    a. not move to dangerous cells (might die).
        #    b. not shoot the arrow if we aren't sure where
        #       the Wumpus is.
        #    c. Once we have the gold, return to where we
        #       started from (easy: reverse the path).
        # 2. Run solver.
        # 3. Return action to the game.
        perceptStr = ""
        if stench:
            perceptStr += "Stench=True,"
        else:
            perceptStr += "Stench=False,"
        if breeze:
            perceptStr += "Breeze=True,"
        else:
            perceptStr += "Breeze=False,"
        if glitter:
            perceptStr += "Glitter=True,"
        else:
            perceptStr += "Glitter=False,"
        if scream:
            perceptStr += "Scream=True"
        else:
            perceptStr += "Scream=False"
        print("PyAgent_Process: " + perceptStr)

        return Action.GOFORWARD
