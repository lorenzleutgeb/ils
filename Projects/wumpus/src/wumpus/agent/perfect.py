from itertools import product
from sys import exit

import networkx as nx
import matplotlib.pyplot as plt

from ..common import Action, Location, Orientation
from ..simulator import World

class PerfectAgent():
    def __init__(self, world: World):
        self.world = world
        self.location = Location(1, 1)
        self.orientation = Orientation.RIGHT
        self.path = []

        noGold = self.isPit(self.world.gold)

        if noGold:
            return

        mustKill = self.world.wumpus == self.world.gold

        r = range(1, self.world.worldSize + 1)

        g = nx.DiGraph()

        labels = {}

        def otoi(o):
            if o == Orientation.LEFT:
                return 0
            elif o == Orientation.RIGHT:
                return 1
            elif o == Orientation.UP:
                return 2
            elif o == Orientation.DOWN:
                return 3


        def nid(l, o):
            return l.y * 4 * self.world.worldSize + l.x * 4 + otoi(o)

        # Find the shortest path between (1, 1) and the gold.
        for x, y, q in product(r, r, Orientation):
            l = Location(x, y)
            labels[nid(l, q)] = str(l) + ", " + str(q)[len("Orientation."):len("Orientation.")+1]

            # First case: We go in the directoin that we are facing (represented by q):
            a = l.getAdjacent(q, self.world.worldSize)
            if a == None:
                continue

            labels[nid(a, q)] = str(a) + ", " + str(q)[len("Orientation."):len("Orientation.")+1]

            if not self.isPit(a):
                cost = 1
                # If we go there, we have to first shoot the wumpus which costs 9 more.
                if a == self.world.wumpus:
                    cost += 9
                g.add_edge(nid(l, q), nid(a, q), cost=cost)

            for action in {Action.TURNLEFT, Action.TURNRIGHT}:
                o = q.turn(action)
                labels[nid(a, o)] = str(a) + ", " + str(o)[len("Orientation."):len("Orientation.")+1]
                g.add_edge(nid(l, q), nid(l, o), cost=1)

        paths = []
        for o in Orientation:
            try:
                paths += (list(nx.all_shortest_paths(g, nid(self.location, self.orientation), nid(self.world.gold, o))))
            except nx.exception.NetworkXNoPath:
                print("Hmm...")

        for path in paths:
            print([labels[node] for node in path])
            #print(list(map(lambda x: labels[x], path)))

        pos = nx.spring_layout(g, scale=3, k=0.05, iterations=20)
        nx.draw_networkx(g, pos=pos, arrows=True, labels=labels)
        edge_labels = nx.get_edge_attributes(g, 'cost')
        nx.draw_networkx_edge_labels(g, pos, edge_labels = edge_labels)
        plt.draw()
        plt.show()

    def isPit(self, l):
        return any(map(lambda pit: pit == l, self.world.pits))

    def process(self, percept):
        # If we have an empty path we know that we cannot get the gold.
        # Note that the gold cannot be at (1, 1).
        if self.path == []:
            return Action.CLIMB

        while True:
            c = input("Action? {f,l,r,g,s,c} ")[0].lower()
            if c == 'f':
                return Action.GOFORWARD
            elif c == 'l':
                return Action.TURNLEFT
            elif c == 'r':
                return Action.TURNRIGHT
            elif c == 'g':
                return Action.GRAB
            elif c == 's':
                return Action.SHOOT
            elif c == 'c':
                return Action.CLIMB
            else:
                print("Huh?")
