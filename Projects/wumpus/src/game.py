from sys import argv, exit, stdout
from random import seed
from os import urandom
from os.path import join
#import binascii import unhexlify, hexlify

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
    generationMode = False
    base = None
    porcelain = '-porcelain' in argv

    for arg, val in zip(argv[1:], argv[2:]):
        if arg == "-size":
            worldSize = max(2, int(val))
        elif arg == "-trials":
            numTrials = int(val)
        elif arg == "-tries":
            numTries = int(val)
        elif arg == "-seed":
            seedV = bytes.fromhex(val)
        elif arg == "-world":
            worldFile = val
        elif arg == "-agent":
            agentName = val
        elif arg == '-generate':
            base = val

    if seedV != None:
        seed(seedV)
    else:
        seedV = urandom(4)
        seed(seedV)

    seedV = seedV.hex()

    if base != None:
        generate(worldSize, seedV, base)
    else:
        if not porcelain:
            print("seed := " + seedV)

        play(
            worldSize,
            worldFile,
            agentName,
            numTrials,
            numTries,
            porcelain
        )

def generate(worldSize, seedV, base):
    fname = join(base, 'world-{}-{}.txt'.format(worldSize, seedV))

    world = World(worldSize)
    world.writeTo(fname)
    agent = PerfectAgent(world)

    moves = 0
    while not world.isGameOver() and moves < MAX_MOVES:
        world.execute(agent.process(world.percept))
        moves += 1

    with open(fname, 'a') as f:
        f.write('optimum {}\n'.format(world.getScore()))

def play(worldSize, worldFile, agentName, numTrials, numTries, porcelain):
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
            agent = ASPAgent()
        elif agentName == 'asp-cheat':
            agent = ASPAgent(wumpusWorld)

        trialScore = 0
        for tries in range(1, numTries + 1):
            #wumpusWorld.Initialize()
            #agent.Initialize()
            numMoves = 0
            if not porcelain:
                print(str(trial) + ":" + str(tries))

            while (not(wumpusWorld.isGameOver())) and (numMoves < MAX_MOVES):
                if not porcelain:
                    wumpusWorld.printTo(stdout)
                percept = wumpusWorld.percept
                action = agent.process(percept)
                wumpusWorld.execute(action)
                numMoves += 1

            score = wumpusWorld.getScore()

            if porcelain:
                print(score)
            else:
                trialScore = trialScore + score
                print("Trial " + str(trial) + ", Try " + str(tries) + " complete: Score = " + str(score))

        if not porcelain:
            averageScore = (trialScore) / (numTries)
            print("Trial " + str(trial) + " complete: Average score for trial = " + str(averageScore))
            totalScore = totalScore + trialScore

    if not porcelain:
        averageScore = (totalScore) / ((numTrials * numTries))
        print("All trials completed: Average score for all trials = " + str(averageScore))

if __name__ == "__main__":
    main()
