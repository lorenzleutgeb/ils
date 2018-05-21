from sys import argv, exit
from random import seed
from os import urandom
from os.path import join
import logging
#import binascii import unhexlify, hexlify

from wumpus.common import *
from wumpus.simulator import World
from wumpus.agent import *

MAX_MOVES = 1000

def main():
    worldSize = 4
    seedV = None
    worldFile = None
    agentName = 'proxy'
    generationMode = False
    base = None
    porcelain = '-porcelain' in argv
    debug = '-debug' in argv

    if debug:
        logging.basicConfig(level=logging.DEBUG, format='')

    for arg, val in zip(argv[1:], argv[2:]):
        if arg == "-size":
            worldSize = max(2, int(val))
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
            print("World " + seedV)

        play(
            worldSize,
            worldFile,
            agentName,
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

def play(worldSize, worldFile, agentName, porcelain):
    wumpusWorld: World = None
    agent = None
    percept: Percept = None
    action: Action = None
    numMoves = 0

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

    numMoves = 0

    aborted = False
    while (not(wumpusWorld.isGameOver())) and (numMoves < MAX_MOVES):
        wumpusWorld.printTo()
        percept = wumpusWorld.percept
        action = agent.process(percept)
        if action == None:
            aborted = True
            break
        wumpusWorld.execute(action)
        numMoves += 1

    score = -MAX_MOVES if aborted else wumpusWorld.getScore()

    print(score if not aborted else '!')

if __name__ == "__main__":
    main()
