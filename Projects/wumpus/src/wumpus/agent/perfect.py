from functools import reduce
from itertools import product
from sys       import exit
from time      import sleep

import networkx as nx

# The following two imports are only necessary for plotting:
#import matplotlib.pyplot as plt
#from networkx.drawing.nx_agraph import write_dot

from ..common    import Action, Location, Orientation
from ..simulator import World

class PerfectAgent():
    def __init__(self, world: World):
        if world.gold in world.pits:
            self.plan = [Action.CLIMB]
            return

        # NOTE: In the following, all code that generates human-readable
        # labels is commented out to save memory. In case you want to
        # debug and/or print the graph, you should un-comment these lines.

        r = range(1, world.worldSize + 1)

        # We build a graph that respresents reachability (with cost) for all cells.
        g = nx.DiGraph()

        for x, y, o in product(r, r, Orientation):
            lo = Location(x, y)
            #la = label=' '.join(map(str,
            #    (['G'] if lo == world.gold else []) +
            #    (['W'] if lo == world.wumpus else []) +
            #    [lo, o]
            #))

            g.add_node((lo, o), location=lo, orientation=o)#, label=la)

            # Case 1: We go in the direction that we are facing (represented by o):
            a = lo.getAdjacent(o, world.worldSize)

            # Avoid bumping and falling down into a pit.
            if a != None and a not in world.pits:
                cost = 1
                act = [Action.GOFORWARD]

                # If we go there, we have to first shoot
                # the wumpus which costs 9 more.
                if a == world.wumpus:
                    cost += 9
                    act = [Action.SHOOT, Action.GOFORWARD]

                g.add_edge((lo, o), (a, o), cost=cost, action=act)#, label=str(cost) + " G " + ("S" if a == world.wumpus else ""))

            # Case 2: We turn ourselves.
            for action in {Action.TURNLEFT, Action.TURNRIGHT}:
                # Case 2a: We turn once.
                oa = o.turn(action)
                g.add_edge((lo, o), (lo, oa), cost=1, action=[action])#, label="1 " + str(action))

                # Case 2b: We turn twice.
                ob = oa.turn(action)
                g.add_edge((lo, oa), (lo, ob), cost=1, action=[action])#, label="1 " + str(action))

        # Here is some code to plot the graph for debuging. Use it in
        # combination with labels.
        #pos = nx.spring_layout(g, scale=3, k=0.05, iterations=20)
        #nx.draw_networkx(g, pos=pos, arrows=True, labels=labels)
        #edge_labels = nx.get_edge_attributes(g, 'label')
        #nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
        #plt.draw()
        #plt.show()
        #write_dot(g, 'perfect.gv')

        paths = []
        for o in Orientation:
            try:
                paths += list(nx.all_shortest_paths(g, (Location(1, 1), Orientation.RIGHT), (world.gold, o), weight='cost'))
            except nx.exception.NetworkXNoPath:
                # This means that the gold is actually not rechable.
                self.plan = [Action.CLIMB]
                return

        # Handy function to compute the cost of a whole path.
        def costs(path):
            return reduce(lambda c, e: c + g.get_edge_data(*e)['cost'], zip(path, path[1:]), 0)

        # Handy function to derive a list of actions from a path.
        def actions(path):
            return reduce(lambda c, e: c + g.get_edge_data(*e)['action'], zip(path, path[1:]), [])

        goThere = actions(min(map(lambda x: (x, costs(x)), paths), key=lambda x: x[1])[0])
        pickUpThatShiny = [Action.GRAB]
        turnAround = [Action.TURNLEFT, Action.TURNLEFT]
        comeBack = list(map(lambda x: x.mirror(), filter(lambda x: x != Action.SHOOT, goThere[::-1])))

        # This is to avoid a useless turn as the last move coming back.
        if comeBack[-1] == Action.TURNRIGHT:
            comeBack = comeBack[:-1]

        climbOut = [Action.CLIMB]

        self.plan = goThere + pickUpThatShiny + turnAround + comeBack + climbOut

    def process(self, percept):
        return self.plan.pop(0)
