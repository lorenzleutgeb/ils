from sys        import exit
from os.path    import dirname, join
from os         import remove
from subprocess import PIPE, STDOUT, run
from tempfile   import mkstemp

from ..common    import Action, Orientation, Location
from ..simulator import World

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

class ASPAgent():
    def __init__(self, init=None):
        if init == None:
            # Assume some large world. Will get adjusted once we bump.
            self.size = 4

            # Initially we do not know about stench/breeze/glitter
            # anywhere.
            self.world = [[(None, None, None, False) for i in range(self.size)] for j in range(self.size)]
            self.position = Location(1, 1)
            self.orientation = Orientation.RIGHT
            self.previousActions = []
            self.wumpusDead = False
        else:
            print('We are cheating!')
            self.size = init.worldSize

            self.world = [
                [
                    (None, None, None, True) for i in range(self.size)
                ] for j in range(self.size)
            ]
            self.position = Location(1, 1)
            self.orientation = Orientation.RIGHT
            self.previousActions = []
            self.wumpusDead = False

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

        # If we moved without bump, account for the move!
        elif prevAct == Action.GOFORWARD:
            self.position = self.position.getAdjacent(self.orientation, 0xcaffebabe)

        # If we turned, account for turning!
        if prevAct in {Action.TURNLEFT, Action.TURNRIGHT}:
            self.orientation = self.orienation.turn(prevAct)

        if percept.scream:
            self.wumpusDead = True

        self.world[self.position.x - 1][self.position.y - 1] = (
            percept.stench,
            percept.breeze,
            percept.glitter,
            True
        )

        # 1. Add the knowledge that we obtain as percepts to
        #    our model/state of the world. We should
        #    a. not move to dangerous cells (might die).
        #    b. not shoot the arrow if we aren't sure where
        #       the Wumpus is.
        #    c. Once we have the gold, return to where we
        #       started from (easy: reverse the path).

        knowledge = [
            '#const worldSize = {}.'.format(self.size),
            fact(True, 'now', [self.position.x, self.position.y, self.orientation.toSymbol()]),
            fact(self.wumpusDead, 'wumpusDead')
        ]

        for i, row in enumerate(self.world):
            for j, (stench, breeze, glitter, explored) in enumerate(row):
                knowledge.append(fact(stench, 'stench', [i + 1, j + 1]))
                knowledge.append(fact(breeze, 'breeze', [i + 1, j + 1]))
                knowledge.append(fact(glitter, 'glitter', [i + 1, j + 1]))
                knowledge.append(fact(explored, 'explored', [i + 1, j + 1]))

        for i, a in enumerate(self.previousActions):
            knowledge.append("previousAction({},{}).".format(i, a.toSymbol()))

        print('\n'.join(knowledge))

        kfd, kfname = mkstemp()

        with open(kfd, 'w') as f: f.write('\n'.join(knowledge))

        # 2. Run solver.
        d = dirname(__file__)
        proc = run(
            [
                'dlv',
                '-silent',
                #'-filter=goal',
                #'-filter=do',
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

        print(proc.stdout)

        if len(result) == 0:
            print('ASP program did not return any answer sets! Inconsistency?')

        if result[0] != '{':
            print('ASP Errors:\n  \033[31m' + result.replace('\n', '\n  ') + '\033[0m')
            exit(1)

        result = result.strip().split('\n')

        if len(result) > 1:
            print('WARN: ASP program returned multiple answer sets.')

        # 3. Extract action and save it to a list. Return action to the game.
        try:
            action = Action(int(result[0][8]))
        except:
            print('\033[31mFailed to extract action from answer set:\033[0m')
            print(result[0])
            exit(1)

        print(action)
        self.previousActions.append(action)
        return action
