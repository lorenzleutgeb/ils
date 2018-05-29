from functools  import reduce
from itertools  import product
from os.path    import dirname, join
from os         import remove
from subprocess import PIPE, STDOUT, run
from tempfile   import mkstemp

import logging

from networkx                                 import DiGraph, NetworkXNoPath
from networkx.algorithms.shortest_paths.astar import astar_path as astar

from .mode       import Mode
from ..asp       import unlite, fact, atom, AnswerSet
from ..common    import Action, Orientation, Location, paint
from ..simulator import World
from ..util      import dlv

logger = logging.getLogger('asp-agent')

plain = {
    # Required to return the desired action to the game.
    'do': (Action,),

    # The next three are needed to implement the autopilot.
    'autopilot': (),
    'goal': (Location,),
    'safe': (Location,),

    # For diagnosing de facto inconsistencies.
    'bad': (int,),

    # This one is needed for painting.
    'size': (int,),
}

interesting = {
    # For debugging, you may add other predicates here.
    # Note that painters are added below.
    'mode': (Mode,),
}

painted = (
    {
        'now': Orientation,
        'h':   int,
    },
    {
        'frontier': 'F',
        'safe':     'S',
        'pit':      'P',
        'next':     'N',
        'goal':     'G',
        'wumpus':   'W',
    }
)

extract = dict(plain)
extract.update(interesting)

extract.update(dict([
    (predicate, (Location,target)) for predicate, target in painted[0].items()
]))

extract.update(dict([
    (predicate, (Location,)) for predicate in painted[1].keys()
]))

class ASPAgent():
    def __init__(self):
        self.dlv = dlv()
        self.actions = []
        self.shot = None
        self.grabbed = None

        # Initially we do not know about stench/breeze/glitter
        # anywhere.
        self.world = {}
        self.position = Location(1, 1)
        self.orientation = Orientation.RIGHT
        self.killed = False
        self.bumped = None
        self.previousAction = None

        # Assume some large world. Will get adjusted once we bump.
        self.size = 0xdeadbeef

        _, self.prog = mkstemp()
        unlite(join(dirname(__file__), 'agent.md'), self.prog)

        # To look at the ASP-Core compliant version, uncomment this.
        #unlite(join(dirname(__file__), 'agent.md'), 'agent.asp')

        with open('agent', 'w') as f: f.truncate()

        # We build a graph that respresents cost for all rooms.
        self.g = DiGraph()
        self.g.add_nodes_from([(self.position, o) for o in Orientation])

    def expand(self):
        for o in Orientation:
            a = self.position.getAdjacent(o, self.size)
            if a == None:
                continue

            self.g.add_edge((self.position, o), (a, o), action=Action.GOFORWARD)

            for action in {Action.TURNLEFT, Action.TURNRIGHT}:
                self.g.add_edge((self.position, o), (self.position, o.turn(action)), action=action)
                self.g.add_edge((self.position, o.mirror()), (self.position, o.turn(action).mirror()), action=action)

    def facts(self):
        # now/3 and killed/0 are certain.
        result = [
            fact(True, 'now', [self.position.x, self.position.y, self.orientation.toSymbol()]),
            fact(self.killed, 'killed'),
        ]

        if self.bumped != None:
            result.append(fact(True, 'bumped', self.bumped))

        if self.shot != None:
            result.append(fact(True, 'shot', [self.shot[0].x, self.shot[0].y, self.shot[1].toSymbol()]))

        if self.grabbed != None:
            result.append(fact(True, 'grabbed', self.grabbed))

        for k, v in self.world.items():
            result += [
                fact(v[i], name, k) for i, name in enumerate(['stench', 'breeze', 'glitter'])
            ] + [
                fact(True, 'explored', k)
            ]

        return result

    def solve(self):
        return run(
            [
                self.dlv,
                '-n=1',
                '-silent',
                '-filter=' + ','.join(extract.keys()),
                self.prog,
                '--'
            ],
            stderr=STDOUT,
            stdout=PIPE,
            input='\n'.join(self.facts()),
            encoding='utf-8'
        )

    def autopilot(self, goal, safe):
        path = min(
            [
                astar(
                    self.g,
                    (self.position, self.orientation),
                    (goal, o),
                    heuristic=heuristic,
                    weight=lambda u, v, d: 1 if safe.get((v[0],), False) else None
                )
                for o in Orientation
                if (goal, o) in self.g
            ],
            key=len
        )
        return [self.g[u][v]['action'] for u, v in zip(path, path[1:])]

    def process(self, percept):
        if percept.scream:
            self.killed = True

        if percept.bump:
            self.size = max(self.position.x, self.position.y)
            if self.bumped != None:
                logger.debug('We appear to be bumping a second time.')
            self.bumped = self.position.getAdjacent(self.orientation, self.size + 1)
            self.g.remove_nodes_from([(self.bumped, o) for o in Orientation])
        elif self.previousAction == Action.GOFORWARD:
            self.position = self.position.getAdjacent(self.orientation, self.size)
        elif self.previousAction in {Action.TURNLEFT, Action.TURNRIGHT}:
            self.orientation = self.orientation.turn(self.previousAction)
        elif self.previousAction == Action.SHOOT:
            if self.shot != None:
                logger.debug('We appear to be shooting a second time.')
            self.shot = (self.position, self.orientation)
        elif self.previousAction == Action.GRAB:
            self.grabbed = self.position

        if self.actions != []:
            self.previousAction = self.actions.pop(0)
            return self.previousAction

        # We need to add all neighboring nodes to the graph to reason about them.
        # Once we explore a new state, we need to add to the graph the possibility
        # to turn here.
        if self.position not in self.world:
            self.expand()

        self.world[self.position] = (percept.stench, percept.breeze, percept.glitter)

        result = self.solve().stdout

        if len(result) == 0:
            logger.debug('ASP program did not return any answer sets! Inconsistency?')
            logger.debug(result)
            return None

        if result.startswith('Best model: {'):
            start, end = result.find('{'), result.find('}')
            result = result[start:end+1]

        if result[0] != '{':
            logger.error('ASP Errors:\n  \033[31m' + result.replace('\n', '\n  ') + '\033[0m')
            return None

        result = AnswerSet.parse(result.strip().split('\n')[0], extract)
        size = next(l for (l,), sign in result['size'].items() if sign)

        paint(
            size,
            [(result.tofun(pred),) for pred, _ in painted[0].items()] +
            [(result.tobfun(pred), symbol) for pred, symbol in painted[1].items()],
            'agent',
            result.pretty(interesting.keys())
        )

        bads = result['bad'].items()
        if len(bads) > 0:
            for (x,), sign in bads:
                prefix = '%{} '.format(x)
                found = False
                with open(self.prog) as f:
                    for ln in f:
                        if ln.startswith(prefix):
                            found = True
                            logger.debug('\033[31mCONSISTENCY ' + str(x) + ': ' + ln[len(prefix):].strip() + '\033[0m')
                    if not found:
                        logger.debug('No comment describing bad({}). Add a line starting with \'%{} \' followed by a description.'.format(x, x))
            return None

        if result['autopilot'][()]:
            goal = next(l for (l,), sign in result['goal'].items() if sign)
            self.actions = self.autopilot(goal, result['safe'])

        if self.actions != []:
            self.previousAction = self.actions.pop(0)
        else:
            self.previousAction = next(a for a, sign in result['do'].items() if sign)[0]

        return self.previousAction

def turns(o1, o2):
    od = abs(int(o1) - int(o2))
    return 1 if od == 3 else od

def routes(a, b):
    result = []

    dx = a.x - b.x
    if dx < 0:
        result.append(Orientation.RIGHT)
    elif dx > 0:
        result.append(Orientation.LEFT)

    dy = a.y - b.y
    if dy < 0:
        result.append(Orientation.UP)
    elif dy > 0:
        result.append(Orientation.DOWN)

    return result

def heuristic(a, b):
    (l1, o1), (l2, o2) = a, b

    if l1 == l2:
        return turns(o1, o2)

    rs = routes(l1, l2)
    penalty = len(rs) > 1
    rs = map(lambda x: turns(o1, x), rs)

    return min(rs) + penalty + taxicab(l1, l2)

def taxicab(a, b):
    if len(a) != len(b):
        return None
    return reduce(lambda s, x: s + abs(x[0] - x[1]), zip(a, b), 0)
