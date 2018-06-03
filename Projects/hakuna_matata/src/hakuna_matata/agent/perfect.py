from heapq     import heappush, heappop
from itertools import count

from ..common    import Action, Location, Orientation
from ..simulator import World

class PerfectAgent():
    def __init__(self, world: World):
        if world.gold in world.pits:
            self.plan = [Action.CLIMB]
            return

        source, target = (Location(1, 1), Orientation.RIGHT), None
        paths, dist, seen, c = {source: []}, {}, {source: 0}, count()
        fringe = [(0, next(c), source)]

        while fringe:
            (d, _, v) = heappop(fringe)
            if v in dist:
                continue

            dist[v] = d
            if v[0] == world.gold:
                target = v
                break

            l, o = v
            neighbours = [([a], (l, o.turn(a)), 1) for a in {Action.TURNLEFT, Action.TURNRIGHT}]

            adj = l.getAdjacent(o, world.worldSize)
            if adj != None and adj not in world.pits:
                shoot = adj == world.wumpus
                actions = [Action.SHOOT] if shoot else []
                actions += [Action.GOFORWARD]
                neighbours.append((actions, (adj, o), 1 if not shoot else 10))

            for actions, u, cost in neighbours:
                vu_dist = dist[v] + cost
                # Cut off paths that are too costly.
                if vu_dist > 500:
                    continue
                if u not in seen or vu_dist < seen[u]:
                    seen[u] = vu_dist
                    heappush(fringe, (vu_dist, next(c), u))
                    paths[u] = paths[v] + actions

        # Gold not reachable.
        if target == None:
                 self.plan = [Action.CLIMB]
                 return

        goThere = paths[target]
        pickUpThatShiny = [Action.GRAB]
        turnAround = [Action.TURNLEFT, Action.TURNLEFT]
        comeBack = list(map(lambda x: x.mirror(), filter(lambda x: x != Action.SHOOT, goThere[::-1])))
        climbOut = [Action.CLIMB]

        # This is to avoid a useless turn as the last move coming back.
        if comeBack[-1] == Action.TURNRIGHT:
            comeBack = comeBack[:-1]

        self.plan = goThere + pickUpThatShiny + turnAround + comeBack + climbOut

    def process(self, percept):
        return self.plan.pop(0)
