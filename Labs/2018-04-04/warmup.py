# Team White

from pyeda.boolalg.expr import *

# Create the variables needed.
vs = ['r1', 'b2', 'r3', 'b4']
vs = list(map(exprvar, vs))
r1, b2, r3, b4 = vs

# Declare how variables are to be quantified.
qs = {
    r1: 'e',
    b2: 'a',
    r3: 'e',
    b4: 'a'
}

# Structure of the formula.
f = ITE(r1, ITE(b2, True, ITE(r3, False, b4)), ITE(b2, ITE(r3, b4, True),r3))

# Compute CNF and get DIMACS format.
props, dimacs = expr2dimacscnf(f.to_cnf())
dimacs = str(dimacs).split('\n')

# Massage DIMACS into QDIMACS.
print('\n'.join(
    ['c Team White'] +
    ['c {} {}'.format(props[v], v) for v in vs] +
    [dimacs[0]] +
    ['{} {} 0'.format(qs[v], props[v]) for v in vs] +
    dimacs[1:]
))
