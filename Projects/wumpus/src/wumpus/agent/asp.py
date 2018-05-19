from functools  import reduce
from os.path    import dirname, join
from os         import remove
from subprocess import PIPE, STDOUT, run
from tempfile   import mkstemp

import logging

import networkx as nx

from networkx.algorithms.shortest_paths.generic import shortest_path

# The following two imports are only necessary for plotting,
# if you want them pip install -r plotting-requirements.txt
#import matplotlib.pyplot as plt
#from networkx.drawing.nx_agraph import write_dot

from ..common    import Action, Orientation, Location
from ..simulator import World
from ..util      import dlv
from .mode       import Mode

# For debugging:
#logging.basicConfig(level=logging.DEBUG)
PRINT_KNOWLEDGE=False

logger = logging.getLogger('asp-agent')

def flatten(xs):
    return reduce(lambda x, y: x + [y] if type(y) != list else y + x, xs, [])

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
                terms = list(map(lambda x: x[0](int(x[1])), zip(interesting[predicate], terms)))
            else:
                terms = list(map(int, terms))


        if predicate in result:
            result[predicate].append((not neg, terms))
        else:
            result[predicate] = [(not neg, terms)]
    return result

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
            result += '{' + ', '.join([
                '\033[3' + str(1 + sign) + 'm(' + ','.join(map(str, terms))  + ')\033[0m' for sign, terms in x[predicate]
            ]) + '}'
        result += '\n'

    return result

class ASPAgent():
    def __init__(self, init=None):
        self.dlv = dlv()
        self.actions = []

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
        else:
            logger.debug('We are cheating!')
            self.size = init.worldSize

            self.world = {}
            self.position = Location(1, 1)
            self.orientation = Orientation.RIGHT
            self.previousActions = []
            self.wumpusDead = False
            self.bump = Location(self.size + 1, 1)

        # We build a graph that respresents reachability (with cost) for all cells.
        self.g = nx.DiGraph()
        for o in Orientation:
            self.g.add_node((self.position, o), label='{} {}'.format(self.position, o))

    def previousAction(self):
        return None if self.previousActions == [] else self.previousActions[-1]

    def decodeAction(self, u, v):
        return self.g.get_edge_data(u, v)['action']

    def process(self, percept):
        prevAct = self.previousAction()

        # Infer size of the world.
        if percept.bump:
            self.size = max(self.position.x, self.position.y)
            if self.bump != None:
                logger.debug('We appear to be bumping a second time.')
            self.bump = self.position.getAdjacent(self.orientation, self.size + 1)
            # TODO: Remove unnecessary nodes from self.g.

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

        #print(list(map(str, self.world.keys())))

        # We need to add all neighboring nodes to the graph to reason about them.
        # Once we explore a new state, we need to add to the graph the possibility
        # to turn here.
        if explored:
            for o in Orientation:
                a = self.position.getAdjacent(o, self.size)

                if a == None:
                    continue

                self.g.add_node((a, o), location=a, orientation=o, label='{} {}'.format(a, o))

                self.g.add_edge(
                    (self.position, o),
                    (a, o),
                    cost=1,# if noWumpusThere else 10,
                    action=[Action.GOFORWARD],# if noWumpusThere else [Action.SHOOT, Action.GOFORWARD]
                    label=str(Action.GOFORWARD)
                )

            for action in {Action.TURNLEFT, Action.TURNRIGHT}:
                # Case 2a: We turn once.
                oa = o.turn(action)
                self.g.add_edge((self.position, o), (self.position, oa), cost=1, action=[action], label=str(action))

                # Case 2b: We turn twice.
                ob = oa.turn(action)
                self.g.add_edge((self.position, oa), (self.position, ob), cost=1, action=[action], label=str(action))

                # Case 2b: We turn twice.
                oc = ob.turn(action)
                self.g.add_edge((self.position, ob), (self.position, oc), cost=1, action=[action], label=str(action))

                # Case 2b: We turn twice.
                od = oc.turn(action)
                self.g.add_edge((self.position, oc), (self.position, od), cost=1, action=[action], label=str(action))

        paths = {}
        for n in self.g:
            l, o = n
            #if l in self.world:
            #    continue
            try:
                p = shortest_path(self.g, (self.position, self.orientation), n)#, 'cost'))
                # TODO: For now, just use path length as cost. This
                # WILL cause some trouble later on FOR SURE.
                paths[n] = p
            except nx.exception.NetworkXNoPath:
                logger.warning('There is no path to {}'.format(l))
                continue

        # 1. Add the knowledge that we obtain as percepts to
        #    our model/state of the world. We should
        #    a. not move to dangerous cells (might die).
        #    b. not shoot the arrow if we aren't sure where
        #       the Wumpus is.
        #    c. Once we have the gold, return to where we
        #       started from (easy: reverse the path).

        knowledge = [
            fact(True, 'now', [self.position.x, self.position.y, self.orientation.toSymbol()]),
            fact(self.wumpusDead, 'wumpusDead'),
            fact(Action.GRAB in self.previousActions, 'grabbed'),
            fact(Action.SHOOT not in self.previousActions, 'haveArrow'),
        ]

        if self.bump != None:
            knowledge.append(fact(True, 'bump', [self.bump.x, self.bump.y]))

        for l in self.world:
            stench, breeze, glitter = self.world[l]
            knowledge.append(fact(stench, 'stench', [l.x, l.y]))
            knowledge.append(fact(breeze, 'breeze', [l.x, l.y]))
            knowledge.append(fact(glitter, 'glitter', [l.x, l.y]))
            knowledge.append(fact(True, 'explored', [l.x, l.y]))

        for s in paths:
            (x, y), o = s
            knowledge.append(fact(True, 'pathCost', [x, y, o.toSymbol(), len(paths[s]) - 1]))
            if len(paths[s]) < 2:
                continue
            u = paths[s][0]
            v = paths[s][1]
            a = self.g.get_edge_data(u, v)['action']
            knowledge.append(fact(True, 'towards',  [x, y, o.toSymbol(), a[0].toSymbol()]))

        #for i, a in enumerate(self.previousActions):
        #    knowledge.append("previousAction({},{}).".format(i, a.toSymbol()))

        if PRINT_KNOWLEDGE:
            logger.debug('\n'.join(knowledge))

        # Plot the graph in case we explored something (debugging).
        if explored and False:
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

        with open(kfd, 'w') as f: f.write('\n'.join(knowledge))

        interesting = {
            'goal': (int, int, Orientation, int),
            'do': (Action,),
            'safe': (int, int),
            'bad': (int,),
            'currentMode': (Mode,),
            'autopilot': (),
        }

        # 2. Run solver.
        d = dirname(__file__)
        proc = run(
            [
                self.dlv,
                '-silent',
                #'-det',
                '-filter=' + ','.join(interesting),
                join(d, 'constants.asp'),
                kfname,
                join(d, 'agent.asp'),
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
        result = list(map(lambda x: parse(x, interesting), result))

        if len(result) > 1:
            logger.warning('ASP program returned multiple answer sets. Only considering the first!')

        result = result[0]
        logger.debug(pretty(result, interesting))

        if 'bad' in result:
            for sign, terms in result['bad']:
                prefix = '%' + str(terms[0]) + ' '
                with open(join(d, 'agent.asp'), 'r') as f:
                    found = False
                    for ln in f:
                        if ln.startswith(prefix):
                            found = True
                            logger.debug('\033[31mCONSISTENCY ' + str(terms[0]) + ': ' + ln[len(prefix):] + '\033[0m')
                    if not found:
                        logger.debug('No comment describing bad({}). Add a line starting with \'%{} \' followed by a description.'.format(terms[0], terms[0]))
            return None

        autopilot = False
        # TODO: Autopilot is not aware of pits/wumpus, therefore unsafe to use...
        if 'autopilot' in result and False:
            autopilot = result['autopilot']
            if len(autopilot) == 0:
                autopilot = False
            else:
                autopilot, _ = autopilot[0]

        if autopilot:
            #print('here {} {}'.format(*here))
            goal = next((Location(x, y), o) for sign, [x, y, o, _] in result['goal'] if sign)
            #print('goal {} {}'.format(*goal))
            actions = paths[goal]
            nextCell, _ = actions[1]
            if nextCell not in self.world:
                action = result['do'][0][1][0]
                self.actions = []
            else:
                #for goal in actions:
                    #print('p {} {}'.format(*goal))
                actions = zip(actions, actions[1:])
                actions = list(flatten(map(lambda x: self.decodeAction(*x), actions)))[::-1]
                #for goal in actions:
                    #print('s {}'.format(goal))
                action = actions.pop(0)
                self.actions = actions
        else:
            #print("READING")
            action = result['do'][0][1][0]

        #print(action)
        self.previousActions.append(action)
        logger.debug('=' * 20)
        return action
