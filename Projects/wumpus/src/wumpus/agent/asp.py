from inspect    import getfullargspec
from functools  import reduce
from itertools  import product
from os.path    import dirname, join
from os         import remove
from subprocess import PIPE, STDOUT, run
from tempfile   import mkstemp

import logging

import networkx as nx

from networkx.algorithms.shortest_paths.generic import shortest_path

from ..asp       import unlite
from ..common    import Action, Orientation, Location, paint
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
    'goal': (Location,),
    'safe': (Location,),

    'bad': (int,),
    'size': (int,),

    # For debugging, you may add other predicates here.
    'now': (Location,Orientation),
    'mode': (Mode,),
    'possibleWumpus': (Location,),
    'h': (Location,int),
    'wumpus': (Location,),
    'frontier': (Location,),
    'next': (Location,),
    'pit': (Location,),
}

GRAPHICAL = {
    'explored', 'pit', 'safe', 'next', 'goal', 'wumpus', 'h', 'now', 'frontier', 'size', 'bad', 'possibleWumpus', 'autopilot'
}

def tofun(xs):
    def f(y):
        fy = [x[0][1] for x in xs.items() if x[1] and y == x[0][0]]
        if len(fy) > 1:
            raise ValueError("Not a function since {} yields results {}!".format(y, fy))
        elif len(fy) == 0:
            return None
        else:
            return fy[0]
    return f

def tobfun(xs):
    def f(y):
        fy = [x[1] for x in xs.items() if y == x[0][0]]
        if len(fy) > 1:
            raise ValueError("Not a function since {} yields results {}!".format(y, fy))
        elif len(fy) == 0:
            return None
        else:
            return fy[0]
    return f

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
                terms = list(map(int, terms))
                mapped = []
                i = 0
                for f in interesting[predicate]:
                    if i == len(terms):
                        break
                    if f == None or f == int:
                        n = 1
                        mapped.append(terms[i])
                    else:
                        spec = getfullargspec(f)
                        n = len(spec.args)
                        if n > 1 and spec.args[0] == 'self':
                            n -= 1
                        mapped.append(f(*terms[i:i+n]))
                    i += n
                terms = tuple(mapped)
            else:
                terms = tuple(map(int, terms))

        result[predicate][terms] = (not neg)
    return result

def pretty(x, interesting, size, painters):
    width = max(map(len, interesting))
    selection = list([k for k in interesting.keys() if k not in GRAPHICAL])
    selection.sort()
    notes = []
    for predicate in selection:
        result = predicate.ljust(width) + ' = '

        if predicate not in x:
            result += '∅'
        else:
            result += '{' + ', '.join(map(lambda y: '\033[3' + str(1 + y[1]) + 'm(' + ','.join(map(str, y[0]))  + ')\033[0m', x[predicate].items())) + '}'
        notes.append(result)

    paint(size, painters, 'agent', notes)

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

def ntos(n):
    (x, y), o = n
    return "(({}, {}), {})".format(x, y, o)

class ASPAgent():
    def __init__(self, init=None):
        self.dlv = dlv()
        self.actions = []
        self.shot = None

        _, self.prog = mkstemp()
        unlite(join(dirname(__file__), 'agent.md'), self.prog)

        with open('agent', 'w') as f: f.truncate()

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

    def process(self, percept):
        prevAct = self.previousAction()

        # Infer size of the world.
        if percept.bump:
            self.size = max(self.position.x, self.position.y)
            if self.bump != None:
                logger.debug('We appear to be bumping a second time.')
            self.bump = self.position.getAdjacent(self.orientation, self.size + 1)
        elif prevAct == Action.GOFORWARD:
            self.position = self.position.getAdjacent(self.orientation, self.size)
        elif prevAct in {Action.TURNLEFT, Action.TURNRIGHT}:
            self.orientation = self.orientation.turn(prevAct)
        elif prevAct == Action.SHOOT:
            if self.shot != None:
                logger.debug('We appear to be shooting a second time.')
                return None
            self.shot = (self.position, self.orientation)
            if percept.scream:
                self.wumpusDead = True

        here = (self.position, self.orientation)

        explored = self.position not in self.world

        self.world[self.position] = (percept.stench, percept.breeze, percept.glitter)

        # Since we do not set explored to true in case of a bump, this is checked explicitly.
        if explored or percept.bump:
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
                    self.g.add_edge((self.position, o), (self.position, o.turn(action)), action=action)

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

        proc = run(
            [
                self.dlv,
                '-silent',
                '-filter=' + ','.join(INTERESTING),
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
        result = list(map(lambda x: parse(x, INTERESTING), result))

        if len(result) > 1:
            logger.warning('ASP program returned multiple answer sets. Only considering the first!')

        result = result[0]

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

        for (pred, _) in INTERESTING.items():
            if pred not in result:
                result[pred] = {}

        size = next(l for (l,), sign in result['size'].items() if sign)

        pretty(result, INTERESTING, size, [
            (tofun(result['now']),),
            (tobfun(result['frontier']), 'F'),
            (tobfun(result['safe']), 'S'),
            (tobfun(result['pit']), 'P'),
            (tobfun(result['next']), 'N'),
            (tobfun(result['goal']), 'G'),
            (tobfun(result['wumpus']), 'W'),
            (tofun(result['h']),),
        ])

        # TODO: Autopilot is buggy and therefore disabled. Fix it!
        autopilot = result['autopilot'][()] and False
        if autopilot:
            # First, extract safety information and update action graph.
            for l, safe in result['safe'].items():
                for o in Orientation:
                    n = (l, o)
                    if n not in self.g:
                        continue
                    self.g.nodes[n]['safe'] = safe

            # Then extract goal and compute shortest path.
            goal = next(l for (l,), sign in result['goal'].items() if sign)

            for n in self.g:
                self.g.nodes[n]['label'] = ntos(n)

            def safeOnly(u, v, d):
                if self.g.get_edge_data(u, v) == None:
                    print(ntos(u) + " " + ntos(v) + " has no edge attributes")
                    return None
                return 1 if result['safe'][(v[0],)] else None

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

        self.previousActions.append(action)
        return action
