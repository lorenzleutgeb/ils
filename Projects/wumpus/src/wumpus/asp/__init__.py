from .lite import unlite
from .answer import AnswerSet

__all__ = ['unlite', 'atom', 'fact', 'AnswerSet']

def unlit(fname):
    with open(fname, 'r') as f:
        return [ln[4:-1] if ln.startswith('    ') else '%' + ln[:-1] for ln in f]

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
