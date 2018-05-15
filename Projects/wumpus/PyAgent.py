# PyAgent.py
from tempfile   import mkstemp
import Action
import Orientation

N = 4

# Initially we do not know about stench/breeze/glitter
# anywhere.
world = [[(None, None, None) for i in range(N)] for j in range(N)]

position = (0, 0)

orientation = Orientation.RIGHT

def PyAgent_Constructor ():
    print "PyAgent_Constructor"

def PyAgent_Destructor ():
    print "PyAgent_Destructor"

def PyAgent_Initialize ():
    # Initialize world!
    print "PyAgent_Initialize"

def PyAgent_Process (stench,breeze,glitter,bump,scream):
    if bump == 1:
        print "We bumped. Should never happen."

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
    if (stench == 1):
        perceptStr += "Stench=True,"
    else:
        perceptStr += "Stench=False,"
    if (breeze == 1):
        perceptStr += "Breeze=True,"
    else:
        perceptStr += "Breeze=False,"
    if (glitter == 1):
        perceptStr += "Glitter=True,"
    else:
        perceptStr += "Glitter=False,"
    if (scream == 1):
        perceptStr += "Scream=True"
    else:
        perceptStr += "Scream=False"
    print "PyAgent_Process: " + perceptStr

    return Action.GOFORWARD

def PyAgent_GameOver (score):
    print "PyAgent_GameOver: score = " + str(score)


if __name__ == '__main__':
    PyAgent_Process(0, 1, 0, 0, 0)
