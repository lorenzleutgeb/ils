# PyAgent.py

import Action
import Orientation

N = 4

# Initially we do not know about stench/breeze/glitter
# anywhere.
world = [][(None, None, None)] * N] * N

position = (1, 1)

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

    # GOFORWARD
    # TURNLEFT
    # TURNRIGHT
    # GRAB      to pick up the gold  only do that if we are percepting glitter
    # SHOOT     to kill the Wumpus   only do that if we are facing the Wumpus
    # CLIMB     to leave the cave    only do that if we have the gold and are at (1,1)
    return Action.GOFORWARD

def PyAgent_GameOver (score):
    print "PyAgent_GameOver: score = " + str(score)
