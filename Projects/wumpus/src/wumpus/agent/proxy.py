from ..common import Action

class ProxyAgent():
    def process(self, percept):
        while True:
            c = input('Action? {f,l,r,g,s,c} ')[0].lower()
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
                print('Huh?')
