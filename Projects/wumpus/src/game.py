from sys import argv, exit, stdout
from random import seed

from wumpus.common import *
from wumpus.simulator import World
from wumpus.agent import *

MAX_MOVES = 1000

def main():
    worldSize = 4
    numTrials = 1
    numTries = 1
    seedV = None
    worldFile = None
    agentName = 'proxy'

    for arg, val in zip(argv[1:], argv[2:]):
        if arg == "-size":
            worldSize = int(val)
            if worldSize < 2:
                worldSize = 2
        elif arg == "-trials":
            numTrials = int(val)
        elif arg == "-tries":
            numTries = int(val)
        elif arg == "-seed":
            seedV = int(val)
        elif arg == "-world":
            worldFile = val
        elif arg == "-agent":
            agentName = val

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
            wumpusWorld = World.readFrom(worldFile)
        else:
            wumpusWorld = World(worldSize)

        wumpusWorld.writeTo('last-world.txt')

        if agentName == 'proxy':
            agent = ProxyAgent()
        elif agentName == 'perfect':
            agent = PerfectAgent(wumpusWorld)
        elif agentName == 'asp':
            agent = ASPAgent(wumpusWorld.worldSize)

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
