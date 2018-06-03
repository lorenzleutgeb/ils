from sys     import argv, exit
from random  import seed
from os      import urandom
from os.path import join
from glob    import glob
from time    import time

import logging

from ..common import *
from ..simulator import World
from ..agent import *

def generate(worldSize, seedV, base):
    fname = join(base, 'world-{}-{}.txt'.format(worldSize, seedV))

    world = World(worldSize)
    world.writeTo(fname)
    agent = PerfectAgent(world)

    while world.execute(agent.process(world.percept)):
        ''

    with open(fname, 'a') as f:
        f.write('optimum {}\n'.format(world.getScore()))

def instantiate(agentName, world):
    if agentName == 'proxy':
        return ProxyAgent()
    elif agentName == 'perfect':
        return PerfectAgent(world)
    elif agentName == 'asp':
        return ASPAgent()

def play(world, agentName):
    world.writeTo('last-world.txt')
    agent = instantiate(agentName, world)

    while True:
        world.paint()

        percept = world.percept
        action = agent.process(percept)

        if action == None:
            return None

        if not world.execute(action):
            return world.getScore()

def benchmark(bglob, agentName):
    for instance in glob(bglob):
        wumpusWorld = World.readFrom(instance)
        start = time()
        play(
            wumpusWorld,
            'perfect'
        )
        end = time()
        optimum = wumpusWorld.complexScore()
        optimumElapsed = '{:7.4f}'.format(end - start)


        wumpusWorld = World.readFrom(instance)
        start = time()
        play(
            wumpusWorld,
            agentName
        )
        end = time()
        result = wumpusWorld.complexScore()
        elapsed = '{:7.4f}'.format(end - start)

        if result == None:
            result = '! ! ! !     !'

        size = '{:2}'.format(wumpusWorld.worldSize)
        numPits = '{:2}'.format(len(wumpusWorld.pits))

        print('\t'.join([instance, size, numPits + '\t', optimum, optimumElapsed + '\t', result, elapsed]))

worldSize = 4
seedV = None
worldFile = None
agentName = 'proxy'
generationMode = False
base = None
bench = None

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
    elif arg == '-benchmark':
        bench = val

if seedV != None:
    seed(seedV)
else:
    seedV = urandom(4)
    seed(seedV)

seedV = seedV.hex()

if bench != None:
    benchmark(bench, agentName)
elif base != None:
    generate(worldSize, seedV, base)
else:
    logging.basicConfig(level=logging.DEBUG, format='')

    world = None
    if worldFile != None:
        world = World.readFrom(worldFile)
    else:
        print("World " + seedV)
        world = World(worldSize)

    play(
        world,
        agentName
    )

    print(world.getScore())
