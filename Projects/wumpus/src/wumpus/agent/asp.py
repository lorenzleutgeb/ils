from functools  import reduce
from itertools  import product
from os.path    import dirname, join
from os         import remove
from subprocess import PIPE, STDOUT, run
from tempfile   import mkstemp

import logging

import networkx as nx

from networkx.algorithms.shortest_paths.generic import shortest_path

from ..asp       import unlite, fact, atom, AnswerSet
from ..common    import Action, Orientation, Location, paint
from ..simulator import World
from ..util      import dlv
from .mode       import Mode

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
        #unlite(join(dirname(__file__), 'agent.md'), 'agent.asp')

        with open('agent', 'w') as f: f.truncate()

        # We build a graph that respresents reachability (with cost) for all cells.
        self.g = nx.DiGraph()
        for o in Orientation:
            self.g.add_node((self.position, o))

    def process(self, percept):
        if percept.scream:
            self.killed = True

        if percept.bump:
            self.size = max(self.position.x, self.position.y)
            if self.bumped != None:
                logger.debug('We appear to be bumping a second time.')
            self.bumped = self.position.getAdjacent(self.orientation, self.size + 1)

            for o in Orientation:
                n = (self.bumped, o)
                if n in self.g:
                    self.g.remove_node(n)

        elif self.previousAction == Action.GOFORWARD:
            self.position = self.position.getAdjacent(self.orientation, self.size)
        elif self.previousAction in {Action.TURNLEFT, Action.TURNRIGHT}:
            self.orientation = self.orientation.turn(self.previousAction)

        explored = self.position not in self.world

        self.world[self.position] = (percept.stench, percept.breeze, percept.glitter)

        # Since we do not set explored to true in case of a bump, this is checked explicitly.
        if explored or percept.bump:
            self.actions = []
        elif self.actions != []:
            action = self.actions.pop(0)
            self.previousAction = action
            return action

        # We need to add all neighboring nodes to the graph to reason about them.
        # Once we explore a new state, we need to add to the graph the possibility
        # to turn here.
        if explored:
            for o in Orientation:
                a = self.position.getAdjacent(o, self.size)
                if a == None:
                    continue

                self.g.add_edge((self.position, o), (a, o), action=Action.GOFORWARD)

                for action in {Action.TURNLEFT, Action.TURNRIGHT}:
                    self.g.add_edge((self.position, o), (self.position, o.turn(action)), action=action)

        # now/3 and killed/0 are certain.
        knowledge = [
            fact(True, 'now', [self.position.x, self.position.y, self.orientation.toSymbol()]),
            fact(self.killed, 'killed'),
        ]

        if self.bumped != None:
            knowledge.append(fact(True, 'bumped', self.bumped))

        if self.shot != None:
            knowledge.append(fact(True, 'shot', [self.shot[0].x, self.shot[0].y, self.shot[1].toSymbol()]))

        if self.grabbed != None:
            knowledge.append(fact(True, 'grabbed', self.grabbed))

        for k, v in self.world.items():
            knowledge += [
                fact(v[i], name, k) for i, name in enumerate(['stench', 'breeze', 'glitter'])
            ] + [
                fact(True, 'explored', k)
            ]

        proc = run(
            [
                self.dlv,
                '-silent',
                '-filter=' + ','.join(extract.keys()),
                self.prog,
                '--'
            ],
            stderr=STDOUT,
            stdout=PIPE,
            input='\n'.join(knowledge),
            encoding='utf-8'
        )

        result = proc.stdout

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

        result = result.strip().split('\n')
        result = list(map(lambda x: AnswerSet.parse(x, extract), result))

        if len(result) > 1:
            logger.warning('ASP program returned multiple answer sets. Only considering the first!')

        result = result[0]

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

        autopilot = result['autopilot'][()]
        if autopilot:
            goal = next(l for (l,), sign in result['goal'].items() if sign)

            def safeOnly(u, v, d):
                return 1 if result['safe'].get((v[0],), False) else None

            shortestPath = None
            for o in Orientation:
                try:
                    path = shortest_path(self.g, (self.position, self.orientation), (goal, o), weight=safeOnly)
                    if shortestPath == None or len(shortestPath) > len(path):
                        shortestPath = path
                except nx.NetworkXNoPath:
                    #print('{} to {} is impossible!'.format(ntos((self.position, self.orientation)), ntos((goal, o))))
                    continue

            if shortestPath == None:
                autopilot = False
            else:
                nextCell, _ = shortestPath[1]
                # Next step will be exploration, do not turn on autopilot.
                if nextCell not in self.world:
                    autopilot = False
                else:
                    actions = []
                    for i in range(len(shortestPath) - 1):
                        u = shortestPath[i]
                        v = shortestPath[i + 1]
                        actions.append(self.g[u][v]['action'])
                    action = actions.pop(0)
                    self.actions = actions

        if not autopilot:
            self.actions = []
            action = next(a for a, sign in result['do'].items() if sign)[0]

        if action == Action.SHOOT:
            if self.shot != None:
                logger.debug('We appear to be shooting a second time.')
            self.shot = (self.position, self.orientation)
        elif action == Action.GRAB:
            self.grabbed = self.position

        self.previousAction = action
        return action
