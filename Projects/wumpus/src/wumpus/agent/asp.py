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

PRINT_KNOWLEDGE=True
PLOT=False

if PLOT:
    # The following two imports are only necessary for plotting,
    # if you want them pip install -r plotting-requirements.txt
    import matplotlib.pyplot as plt
    from networkx.drawing.nx_agraph import write_dot

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

# TODO: Remove once the autopilot works.
def ntos(n):
    (x, y), o = n
    return "(({}, {}), {})".format(x, y, o)

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
        elif self.previousAction == Action.GOFORWARD:
            self.position = self.position.getAdjacent(self.orientation, self.size)
        elif self.previousAction in {Action.TURNLEFT, Action.TURNRIGHT}:
            self.orientation = self.orientation.turn(self.previousAction)

        here = (self.position, self.orientation)

        explored = self.position not in self.world

        self.world[self.position] = (percept.stench, percept.breeze, percept.glitter)

        # Since we do not set explored to true in case of a bump, this is checked explicitly.
        if explored or percept.bump:
            self.actions = []
        elif self.actions != []:
            action = self.actions.pop(0)
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

        # now/3 and killed/0 are certain.
        knowledge = [
            fact(True, 'now', [self.position.x, self.position.y, self.orientation.toSymbol()]),
            fact(self.killed, 'killed'),
        ]

        if self.bumped != None:
            knowledge.append(fact(True, 'bumped', [self.bumped.x, self.bumped.y]))

        if self.shot != None:
            knowledge.append(fact(True, 'shot', [self.shot[0].x, self.shot[0].y, self.shot[1].toSymbol()]))

        if self.grabbed != None:
            knowledge.append(fact(True, 'grabbed', [self.grabbed.x, self.grabbed.y]))

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
            write_dot(self.g, 'graph.gv')

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

        if action == Action.SHOOT:
            if self.shot != None:
                logger.debug('We appear to be shooting a second time.')
            self.shot = here
        elif action == Action.GRAB:
            self.grabbed = self.position

        self.previousAction = action
        return action
