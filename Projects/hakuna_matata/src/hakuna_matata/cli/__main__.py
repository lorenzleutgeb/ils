from sys     import argv, exit, stdout
from random  import seed
from os      import urandom
from os.path import join
from glob    import glob
from time    import time

import logging

from ..common import *
from ..simulator import World
from ..agent import *

def generate(size, seedV, base):
    World(size).writeTo(join(base, 'world-{}-{}.txt'.format(size, seedV)))

def play(world, agent):
    while True:
        world.paint()

        percept = world.percept
        action = agent.process(percept)

        if action == None:
            return None

        if not world.execute(action):
            return world.getScore()

def benchmark(bglob):
    for instance in glob(bglob):
        world = World.readFrom(instance)
        agent = PerfectAgent(world)
        stdout.write('{}\t{:2}\t{:2}\t'.format(instance, world.size, len(world.pits)))
        play(world, agent)
        stdout.write('\t{}'.format(world.complexScore()))
        stdout.flush()

        world = World.readFrom(instance)
        agent = ASPAgent()
        start = time()
        play(world, agent)
        end = time()
        result = world.complexScore()
        if result == None:
            result = '! ! ! !     !'

        stdout.write('\t{}\t{}\t{:7.4f}\n'.format(result, agent.getStats(), end - start))
        stdout.flush()

size = 4
seedV = None
worldFile = None
generationMode = False
base = None
bench = None
human = '-human' in argv

for arg, val in zip(argv[1:], argv[2:]):
    if arg == "-size":
        size = max(2, int(val))
    elif arg == "-seed":
        seedV = bytes.fromhex(val)
    elif arg == "-world":
        worldFile = val
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
    benchmark(bench)
elif base != None:
    generate(size, seedV, base)
else:
    logging.basicConfig(level=logging.DEBUG, format='')

    world = None
    if worldFile != None:
        world = World.readFrom(worldFile)
    else:
        print('World ' + seedV)
        world = World(size)
        world.writeTo('last-world.txt')

    play(world, ProxyAgent() if human else ASPAgent())

    print(world.getScore())
