from inspect    import getfullargspec
from enum import Enum

class AnswerSet:
    def __init__(self, dictionary={}):
        self.dictionary = dictionary

    @classmethod
    def parse(cls, a, interesting):
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
                        if f == None or f == int or issubclass(f, Enum):
                            n = 1
                            mapped.append(f(int(terms[i])))
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
        return cls(result)

    def pretty(self, selection):
        selection = list(selection)
        selection.sort()
        width = max(map(len, selection))
        notes = []
        for predicate in selection:
            result = predicate.ljust(width) + ' = '

            if predicate not in self.dictionary:
                result += '∅'
            else:
                result += '{' + ', '.join(map(lambda y: '\033[3' + str(1 + y[1]) + 'm(' + ','.join(map(str, y[0]))  + ')\033[0m', self.dictionary[predicate].items())) + '}'
            notes.append(result)
        return notes

    def tofun(self, name):
        xs = self.dictionary[name]
        def f(y):
            fy = [x[0][1] for x in xs.items() if x[1] and y == x[0][0]]
            if len(fy) > 1:
                raise ValueError("Not a function since {} yields results {}!".format(y, fy))
            elif len(fy) == 0:
                return None
            else:
                return fy[0]
        return f

    def tobfun(self, name):
        xs = self.dictionary[name]
        def f(y):
            fy = [x[1] for x in xs.items() if y == x[0][0]]
            if len(fy) > 1:
                raise ValueError("Not a function since {} yields results {}!".format(y, fy))
            elif len(fy) == 0:
                return None
            else:
                return fy[0]
        return f

    def __getitem__(self, index):
        return self.dictionary[index]
