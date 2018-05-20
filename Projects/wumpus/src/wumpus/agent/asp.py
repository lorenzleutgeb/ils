from functools  import reduce
from itertools  import product
from os.path    import dirname, join
from os         import remove
from subprocess import PIPE, STDOUT, run
from tempfile   import mkstemp

import logging

import networkx as nx

from networkx.algorithms.shortest_paths.generic import shortest_path

from ..common    import Action, Orientation, Location
from ..simulator import World
from ..util      import dlv
from .mode       import Mode

PRINT_KNOWLEDGE=False
PLOT=False

if PLOT:
    # The following two imports are only necessary for plotting,
    # if you want them pip install -r plotting-requirements.txt
    import matplotlib.pyplot as plt
    from networkx.drawing.nx_agraph import write_dot

logger = logging.getLogger('asp-agent')

INTERESTING = {
    # Required to return the desired action to the game.
    'do': (Action,),

    # The next three are needed to implement the autopilot.
    'autopilot': (),
    'goal': (int, int, int),
    'safe': (int, int),

    # For debugging, you may add other predicates here.
    'bad': (int,),
    'risk': (Orientation,),
    'mode': (Mode,),
    'possiblePit': (int, int, int, int),
    'strange': (int, int, int, int, int, int),
    'possibleWumpus': (int, int),
    'wumpus': (int, int),
    'reachable': (int, int),
    'explored': (int, int),
    'candidate': (int, int, int),
    'next': (int, int, int),
    'ncandidate': (int, int, int),
}

def atom(sign, predicate, terms=[]):
    result = ''
    if sign == None:
        result += 'not '
    elif sign == False:
        result += '-'
    elif sign != True:
        raise ValueError('Sign must be None or boolean!')
    result += predicate
    if len(terms ) == 0:
        return result
    return result + '(' + ','.join(map(str, terms)) + ')'

def fact(sign, predicate, terms=[]):
    return '' if sign == None else atom(sign, predicate, terms) + '.'

def parse(a, interesting):
    if a.startswith('{') and a.endswith('}'):
        a = a[1:-1]
    a = a.split(', ')
    result = {}
    for predicate in interesting:
        result[predicate] = {}
    for e in a:
        neg = e.startswith('-')
        lpar = e.find('(')
        if lpar < 0:
            terms = ()
            predicate = e[neg:]
        else:
            predicate = e[neg:lpar]
            terms = e[lpar + 1:-1].split(',')
            if predicate in interesting:
                terms = tuple(map(lambda x: x[0](int(x[1])), zip(interesting[predicate], terms)))
            else:
                terms = tuple(map(int, terms))

        result[predicate][terms] = (not neg)
    return result

def unlit(fname):
    with open(fname, 'r') as f:
        return [ln[4:-1] if ln.startswith('    ') else '%' + ln[:-1] for ln in f]

def pretty(x, interesting):
    result = '\n'
    width = max(map(len, interesting))
    selection = list(interesting.keys())
    selection.sort()
    for predicate in selection:
        result += predicate.ljust(width) + ' = '

        if predicate not in x:
            result += '∅'
        else:
            result += '{' + ', '.join(map(lambda y: '\033[3' + str(1 + y[1]) + 'm(' + ','.join(map(str, y[0]))  + ')\033[0m', x[predicate].items())) + '}'
        result += '\n'

    return result

def manhattan(a, b):
    (l1, o1), (l2, o2) = a, b

    # Compute difference between two orientations:
    od = abs(int(o1) - int(o2))
    if od == 3:
        od = 1

    return od + taxicab(l1, l2)

def taxicab(a, b):
    if len(a) != len(b):
        return None
    return reduce(lambda s, x: s + abs(x[0] - x[1]), zip(a, b), 0)

class ASPAgent():
    def __init__(self, init=None):
        self.dlv = dlv()
        self.actions = []
        self.shot = None
        self.prog = unlit(join(dirname(__file__), 'agent.md'))

        if init == None:
            # Assume some large world. Will get adjusted once we bump.
            self.size = 0xcaffebabe

            # Initially we do not know about stench/breeze/glitter
            # anywhere.
            self.world = {}
            self.position = Location(1, 1)
            self.orientation = Orientation.RIGHT
            self.previousActions = []
            self.wumpusDead = False
            self.bump = None

            # We build a graph that respresents reachability (with cost) for all cells.
            self.g = nx.DiGraph()
            for o in Orientation:
                self.g.add_node((self.position, o))
        else:
            logger.debug('We are cheating!')
            self.size = init.worldSize
            self.world = {}
            self.g = nx.DiGraph()

            r = range(1, self.size + 1)
            for x, y in product(r, r):
                l = Location(x, y)
                breeze, stench, glitter = False, False, False
                for n in l.neighbors(self.size):
                    if n in init.pits:
                        breeze = True
                    if n == init.wumpus:
                        stench = True
                    if n == init.gold:
                        glitter = True

                self.world[l] = (breeze, stench, glitter)

                for o in Orientation:
                    a = l.getAdjacent(o, self.size)

                    if a == None:
                        continue

                    self.g.add_edge((l, o), (a, o), action=Action.GOFORWARD)

                for action in {Action.TURNLEFT, Action.TURNRIGHT}:
                    oa = o
                    for i in range(3):
                        oa = o.turn(action)
                        self.g.add_edge((l, o), (l, oa), action=action)

            self.position = Location(1, 1)
            self.orientation = Orientation.RIGHT
            self.previousActions = []
            self.wumpusDead = False
            self.bump = Location(self.size + 1, 1)

    def previousAction(self):
        return None if self.previousActions == [] else self.previousActions[-1]

    def decodeAction(self, u, v):
        return self.g.get_edge_data(u, v)['action']

    def process(self, percept):
        prevAct = self.previousAction()

        if prevAct == Action.SHOOT:
            if self.shot != None:
                logger.debug('We appear to be shooting a second time.')
                return None
            self.shot = (self.position, self.orientation)

        # Infer size of the world.
        if percept.bump:
            self.size = max(self.position.x, self.position.y)
            if self.bump != None:
                logger.debug('We appear to be bumping a second time.')
            self.bump = self.position.getAdjacent(self.orientation, self.size + 1)

        # If we moved without bump, account for the move!
        elif prevAct == Action.GOFORWARD:
            self.position = self.position.getAdjacent(self.orientation, self.size)

        # If we turned, account for turning!
        if prevAct in {Action.TURNLEFT, Action.TURNRIGHT}:
            self.orientation = self.orientation.turn(prevAct)

        if percept.scream:
            self.wumpusDead = True

        here = (self.position, self.orientation)

        explored = self.position not in self.world

        self.world[self.position] = (percept.stench, percept.breeze, percept.glitter)

        if explored:
            self.actions = []
        elif self.actions != []:
            action = self.actions.pop(0)
            self.previousActions.append(action)
            logger.debug('Autopilot is active!')
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
                    prev = o
                    for i in range(4):
                        current = prev.turn(action)
                        self.g.add_edge((self.position, prev), (self.position, current), action=action)
                        prev = current

        knowledge = [
            fact(True, 'now', [self.position.x, self.position.y, self.orientation.toSymbol()]),
            fact(self.wumpusDead, 'wumpusDead'),
            fact(Action.GRAB in self.previousActions, 'grabbed'),
            fact(Action.SHOOT not in self.previousActions, 'haveArrow'),
        ]

        if self.bump != None:
            knowledge.append(fact(True, 'bump', [self.bump.x, self.bump.y]))

        if self.shot != None:
            knowledge.append(fact(True, 'shot', [self.shot[0].x, self.shot[0].y, self.shot[1].toSymbol()]))

        for l in self.world:
            stench, breeze, glitter = self.world[l]
            knowledge.append(fact(stench, 'stench', [l.x, l.y]))
            knowledge.append(fact(breeze, 'breeze', [l.x, l.y]))
            knowledge.append(fact(glitter, 'glitter', [l.x, l.y]))
            knowledge.append(fact(True, 'explored', [l.x, l.y]))

        if PRINT_KNOWLEDGE:
            logger.debug('\n'.join(knowledge))

        # Plot the graph in case we explored something (debugging).
        if explored and PLOT:
            # Here is some code to plot the graph for debuging. Use it in
            # combination with labels.
            pos = nx.spring_layout(self.g, scale=3, k=0.05, iterations=20)
            node_labels = nx.get_node_attributes(self.g, 'label')
            nx.draw_networkx(self.g, pos=pos, arrows=True, labels=node_labels)
            edge_labels = nx.get_edge_attributes(self.g, 'label')
            nx.draw_networkx_edge_labels(self.g, pos, edge_labels=edge_labels)
            plt.draw()
            plt.show()
            write_dot(self.g, 'g-{}.gv'.format(len(self.previousActions)))

        kfd, kfname = mkstemp()
        with open(kfd, 'w') as f:
            f.write('\n'.join(self.prog))
            f.write('\n'.join(knowledge))

        proc = run(
            [
                self.dlv,
                '-silent',
                '-filter=' + ','.join(INTERESTING),
                kfname,
            ],
            stderr=STDOUT,
            stdout=PIPE,
            encoding='utf-8'
        )
        remove(kfname)
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
        result = list(map(lambda x: parse(x, INTERESTING), result))

        if len(result) > 1:
            logger.warning('ASP program returned multiple answer sets. Only considering the first!')

        result = result[0]
        logger.debug(pretty(result, INTERESTING))

        bads = result['bad'].items()
        if len(bads) > 0:
            for (x,), sign in bads:
                prefix = '%{} '.format(x)
                with open(join(d, 'agent.asp'), 'r') as f:
                    found = False
                    for ln in f:
                        if ln.startswith(prefix):
                            found = True
                            logger.debug('\033[31mCONSISTENCY ' + str(x) + ': ' + ln[len(prefix):].strip() + '\033[0m')
                    if not found:
                        logger.debug('No comment describing bad({}). Add a line starting with \'%{} \' followed by a description.'.format(x, x))
            return None

        autopilot = result['autopilot'][()]
        if autopilot:
            # First, extract safety information and update action graph.
            for (x, y), safe in result['safe'].items():
                for o in Orientation:
                    n = (Location(x, y), o)
                    if n not in self.g:
                        continue
                    self.g.nodes[n]['safe'] = safe

            # Then extract goal and compute shortest path.
            goal = next(Location(x, y) for (x, y, _), sign in result['goal'].items() if sign)

            safeOnly = lambda u, v, d: 1 if result['safe'][(u[0].x, u[0].y)] else None
            shortestPath = None
            for o in Orientation:
                try:
                    path = shortest_path(self.g, (self.position, self.orientation), (goal, o), weight=safeOnly)
                except nx.NetworkXNoPath:
                    continue
                if shortestPath == None or len(shortestPath) > len(path):
                    shortestPath = path

            if shortestPath == None:
                autopilot = False
            else:
                nextCell, _ = shortestPath[1]
                # Next step will be exploration, do not turn on autopilot.
                if nextCell not in self.world:
                    autopilot = False
                else:
                    actions = zip(path, shortestPath[1:])
                    actions = list(map(lambda x: self.decodeAction(*x), actions))
                    action = actions.pop(0)
                    self.actions = actions

        if not autopilot:
            self.actions = []
            action = next(a for a, sign in result['do'].items() if sign)[0]

        self.previousActions.append(action)
        logger.debug('═' * 80)
        return action
