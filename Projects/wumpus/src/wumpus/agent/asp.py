from sys        import exit
from os.path    import dirname, join
from os         import remove
from subprocess import PIPE, STDOUT, run
from tempfile   import mkstemp

import networkx as nx

from networkx.algorithms.shortest_paths.generic import shortest_path

# The following two imports are only necessary for plotting,
# if you want them pip install -r plotting-requirements.txt
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import write_dot

from ..common    import Action, Orientation, Location
from ..simulator import World
from ..util      import dlv

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

def parse(a):
    if a.startswith('{') and a.endswith('}'):
        a = a[1:-1]
    a = a.split(', ')
    result = {}
    for e in a:
        neg = e.startswith('-')
        lpar = e.find('(')
        predicate = e[neg:lpar]
        terms = tuple(map(int, e[lpar + 1:-1].split(',')))
        if predicate in result:
            result[predicate].append((not neg, terms))
        else:
            result[predicate] = [(not neg, terms)]
    return result

class ASPAgent():
    def __init__(self, init=None):
        self.dlv = dlv()

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
        else:
            print('We are cheating!')
            self.size = init.worldSize

            self.world = {}
            self.position = Location(1, 1)
            self.orientation = Orientation.RIGHT
            self.previousActions = []
            self.wumpusDead = False

        # We build a graph that respresents reachability (with cost) for all cells.
        self.g = nx.DiGraph()
        for o in Orientation:
            self.g.add_node((self.position, o), label=str(self.position) + ' ' + str(o))

        # TODO: Check whether DLV is on path. If not, download it.
        #       Set some variable that points at the DLV binary to
        #       be used in the process function.

    def previousAction(self):
        return None if self.previousActions == [] else self.previousActions[-1]

    def process(self, percept):
        prevAct = self.previousAction()

        # Infer size of the world.
        if percept.bump:
            self.size = max(self.position.x, self.position.y)
            # TODO: Remove unnecessary nodes from self.g.

        # If we moved without bump, account for the move!
        elif prevAct == Action.GOFORWARD:
            self.position = self.position.getAdjacent(self.orientation, self.size)

        # If we turned, account for turning!
        if prevAct in {Action.TURNLEFT, Action.TURNRIGHT}:
            self.orientation = self.orienation.turn(prevAct)

        if percept.scream:
            self.wumpusDead = True

        explored = self.position not in self.world

        self.world[self.position] = (percept.stench, percept.breeze, percept.glitter)

        # We need to add all neighboring nodes to the graph to reason about them.
        # Once we explore a new state, we need to add to the graph the possibility
        # to turn here.
        if explored:
            for o in Orientation:
                a = self.position.getAdjacent(o, self.size)

                if a == None:
                    continue

                la = label=' '.join(map(str,
                    #(['G'] if lo == world.gold else []) +
                    #(['W'] if lo == world.wumpus else []) +
                    [a, o]
                ))
                self.g.add_node((a, o), location=a, orientation=o, label=la)

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

        # Plot the graph in case we explored something (debugging).
        if explored:
            # Here is some code to plot the graph for debuging. Use it in
            # combination with labels.
            pos = nx.spring_layout(self.g, scale=3, k=0.05, iterations=20)
            node_labels = nx.get_node_attributes(self.g, 'label')
            nx.draw_networkx(self.g, pos=pos, arrows=True, labels=node_labels)
            edge_labels = nx.get_edge_attributes(self.g, 'label')
            nx.draw_networkx_edge_labels(self.g, pos, edge_labels=edge_labels)
            plt.draw()
            plt.show()


        paths = {}
        for n in self.g:
            l, o = n
            if l in self.world:
                continue
            try:
                p = shortest_path(self.g, (self.position, self.orientation), n)#, 'cost'))
                # TODO: For now, just use path length as cost. This
                # WILL cause some trouble later on FOR SURE.
                paths[n] = len(p)
            except nx.exception.NetworkXNoPath:
                continue

        # 1. Add the knowledge that we obtain as percepts to
        #    our model/state of the world. We should
        #    a. not move to dangerous cells (might die).
        #    b. not shoot the arrow if we aren't sure where
        #       the Wumpus is.
        #    c. Once we have the gold, return to where we
        #       started from (easy: reverse the path).

        knowledge = [
            '#const worldSize = {}.'.format(min(self.size, 6)),
            fact(True, 'now', [self.position.x, self.position.y, self.orientation.toSymbol()]),
            fact(self.wumpusDead, 'wumpusDead')
        ]

        for l in self.world:
            stench, breeze, glitter = self.world[l]
            knowledge.append(fact(stench, 'stench', [l.x, l.y]))
            knowledge.append(fact(breeze, 'breeze', [l.x, l.y]))
            knowledge.append(fact(glitter, 'glitter', [l.x, l.y]))

        for l, o in self.g:
            knowledge.append(fact(l in self.world, 'explored', [l.x, l.y]))

        for s in paths:
            (x, y), o = s
            knowledge.append(fact(True, 'pathCost', [x, y, o.toSymbol(), paths[s]]))

        for i, a in enumerate(self.previousActions):
            knowledge.append("previousAction({},{}).".format(i, a.toSymbol()))

        print('\n'.join(knowledge))

        kfd, kfname = mkstemp()

        with open(kfd, 'w') as f: f.write('\n'.join(knowledge))

        # 2. Run solver.
        d = dirname(__file__)
        proc = run(
            [
                self.dlv,
                '-silent',
                '-filter=goal,candidate,do',
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
            print('ASP program did not return any answer sets! Inconsistency?')

        if result[0] != '{':
            print('ASP Errors:\n  \033[31m' + result.replace('\n', '\n  ') + '\033[0m')
            exit(1)

        result = result.strip().split('\n')

        if len(result) > 1:
            print('WARN: ASP program returned multiple answer sets.')

        result = list(map(parse, result))

        for r in result:
            print(r)

        todo = None
        # 3. Extract action and save it to a list. Return action to the game.
        try:
            # TODO: Fix this for do/1. Maybe parse the AS.
            todo = result[0]['do']
        except:
            print('\033[31mFailed to extract action from answer set:\033[0m')
            print(result[0])
            exit(1)

        if len(todo) > 1:
            print('\033[31mAnswer set contains multuple true \'do\' atoms!\033[0m')

        action = Action(todo[0][1][0])
        print(action)
        self.previousActions.append(action)
        return action
