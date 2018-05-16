from tempfile import mkstemp

from ..common import Action, Orientation

class ASPAgent():
    def __init__(self, n):
        # Initially we do not know about stench/breeze/glitter
        # anywhere.
        self.world = [[(None, None, None) for i in range(n)] for j in range(n)]
        self.position = (0, 0)
        self.orientation = Orientation.RIGHT

    def process(percept):
        stench = percept.stench
        breeze = percept.breeze
        glitter = percept.glitter
        bump = percept.bump
        scream = percept.scream

        if bump:
            print("We bumped. Should never happen.")

        world[position[0]][position[1]] = (stench == 1, breeze == 1, glitter == 1)

        perception = [
            "position(" + str(position[0]) + "," + str(position[1]) + ").",
            "orientation(" + str(orientation) + ")."
        ]

        for i, row in enumerate(world):
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

        # make a temp file and add perception there then pass that to dlv

        print("\n".join(perception))

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
