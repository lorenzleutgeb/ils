from collections import deque
from functools   import reduce
from itertools   import product
from os.path     import exists, dirname, join
from os          import remove, stat
from stat        import S_ISFIFO
from subprocess  import PIPE, STDOUT, run
from tempfile    import mkstemp

import logging

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

        # Initially we do not know about stench/breeze/glitter anywhere.
        self.world = {}
        self.position = Location(1, 1)
        self.orientation = Orientation.RIGHT
        self.killed = False
        self.bumped = None
        self.previousAction = None
        self.size = 2

        _, self.prog = mkstemp()
        unlite(join(dirname(__file__), 'agent.md'), self.prog)

        # To look at the ASP-Core compliant version, uncomment this.
        #unlite(join(dirname(__file__), 'agent.md'), 'agent.asp')

        self.paint = exists('agent') and S_ISFIFO(stat('agent').st_mode)

    def facts(self):
        # now/3 and killed/0 are certain.
        result = [
            fact(True, 'now', [*self.position, int(self.orientation)]),
            fact(self.killed, 'killed'),
        ]

        if self.bumped != None:
            result.append(fact(True, 'bumped', self.bumped))

        if self.shot != None:
            result.append(fact(True, 'shot', [*self.shot[0], int(self.shot[1])]))

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

    def bfs(self, safe, target):
        source = (self.position, self.orientation)
        visited = {source: None}
        queue = deque([source])
        while queue:
            node = queue.popleft()
            if node[0] == target:
                path = []
                while node is not None:
                    v = visited[node]
                    if v == None:
                        break
                    act, node = v
                    path.append(act)
                return path[::-1]

            (l, o) = node
            neighbours = [(a, (l, o.turn(a))) for a in {Action.TURNLEFT, Action.TURNRIGHT}]

            adj = l.getAdjacent(o, self.size)
            if adj != None and (safe.get((adj,), False) or adj == target):
                neighbours.append((Action.GOFORWARD, (adj, o)))

            for act, neighbour in neighbours:
                if neighbour not in visited:
                    visited[neighbour] = (act, node)
                    queue.append(neighbour)

        return None

    def process(self, percept):
        if percept.scream:
            self.killed = True
        if percept.bump:
            self.bumped = self.position.getAdjacent(self.orientation, self.size + 1)
        elif self.previousAction == Action.GOFORWARD:
            self.position = self.position.getAdjacent(self.orientation, self.size)
        elif self.previousAction in {Action.TURNLEFT, Action.TURNRIGHT}:
            self.orientation = self.orientation.turn(self.previousAction)
        elif self.previousAction == Action.SHOOT:
            self.shot = (self.position, self.orientation)
        elif self.previousAction == Action.GRAB:
            self.grabbed = self.position
        if self.actions != []:
            self.previousAction = self.actions.pop(0)
            return self.previousAction

        self.world[self.position] = (percept.stench, percept.breeze, percept.glitter)

        result = self.solve().stdout

        if len(result) == 0:
            logger.debug('ASP program did not return any answer sets! Inconsistency?')
            return None

        if result.startswith('Best model: {'):
            start, end = result.find('{'), result.find('}')
            result = result[start:end+1]

        if result[0] != '{':
            logger.error('ASP Errors:\n  \033[31m' + result.replace('\n', '\n  ') + '\033[0m')
            return None

        result = AnswerSet.parse(result.strip().split('\n')[0], extract)

        self.size = result.singleton('size')

        if self.paint:
            paint(
                self.size,
                [(result.tofun(pred),) for pred, _ in painted[0].items()] +
                [(result.tobfun(pred), symbol) for pred, symbol in painted[1].items()],
                'agent',
                result.pretty(interesting.keys())
            )

        bads = result.true('bad')
        if len(bads) > 0:
            for (x,) in bads:
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

        if not result.proposition('autopilot'):
            self.previousAction = result.singleton('do')
            return self.previousAction

        goal = result.singleton('goal')
        self.actions = self.bfs(result['safe'], goal)

        mode = result.singleton('mode')
        if mode == Mode.ESCAPE and goal == Location(1, 1) and len(self.actions) > 0:
            self.actions.append(Action.CLIMB)

        self.previousAction = self.actions.pop(0)
        return self.previousAction
