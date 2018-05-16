from sys import argv, exit, stdout
from random import seed

from wumpus.common import *
from wumpus.simulator import World
from wumpus.agent import ProxyAgent
from wumpus.agent import PerfectAgent

MAX_MOVES = 1000

def main():
    worldSize = 4
    numTrials = 1
    numTries = 1
    seedV = None
    worldFile = None

    for arg in argv[1:]:
        if arg == "-size":
            worldSize = int(arg)
            if worldSize < 2:
                worldSize = 2
        elif arg == "-trials":
            numTrials = int(arg)
        elif arg == "-tries":
            numTries = int(arg)
        elif arg == "-seed":
            seedV = int(arg)
        elif arg == "-world":
            worldFile = arg
        else:
            print("Ignoring unknown option " + arg)
            #exit(1)

    if seedV != None:
        seed(seedV)

    # Run trials
    wumpusWorld: World = None
    agent = None
    percept: Percept = None
    action: Action = None
    score = 0
    trialScore = 0
    totalScore = 0
    averageScore = 0
    numMoves = 0

    for trial in range(1, numTrials + 1):
        if worldFile != None:
            print("Reading a world file is not implemented, sorry.")
            exit(1)
            #wumpusWorld = World.read(Paths.get(worldFile))
        else:
            wumpusWorld = World(worldSize)

        #print("World size = " + str(worldSize) + "x" + str(worldSize))
        #wumpusWorld.Write (".world")

        #agent = ProxyAgent()
        agent = PerfectAgent(wumpusWorld)

        trialScore = 0
        for tries in range(1, numTries + 1):
            #wumpusWorld.Initialize()
            #agent.Initialize()
            numMoves = 0
            print(str(trial) + ":" + str(tries))
            while (not(wumpusWorld.isGameOver())) and (numMoves < MAX_MOVES):
                wumpusWorld.printTo(stdout)
                percept = wumpusWorld.percept
                action = agent.process(percept)
                wumpusWorld.execute(action)
                numMoves += 1

            score = wumpusWorld.getScore()
            #agent.gameOver(score)
            trialScore = trialScore + score
            print("Trial " + str(trial) + ", Try " + str(tries) + " complete: Score = " + str(score))

        averageScore = (trialScore) / (numTries)
        print("Trial " + str(trial) + " complete: Average score for trial = " + str(averageScore))
        totalScore = totalScore + trialScore

    averageScore = (totalScore) / ((numTrials * numTries))
    print("All trials completed: Average score for all trials = " + str(averageScore))

if __name__ == "__main__":
    main()
