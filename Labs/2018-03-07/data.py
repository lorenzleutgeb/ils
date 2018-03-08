# Team White

from os         import remove
from subprocess import PIPE, STDOUT, run
from tempfile   import mkstemp
from random     import choice, sample

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# n ... Number of Variables
# k ... Number of Literals per Clause
# l ... Number of Clauses

# List to choose k from.
K = [2, 3, 5]

# List to choose n from.
N = [20, 50, 100, 200, 500]

# Number of experiments to run in order to determine p.
m = 200.0

# Range parameters for r: (min, max, delta)
R = (2.0, 6.0, 0.01)

def randomize(n, k, l):
    return [[p * -1 if choice([True, False]) else p for p in sample(range(1, n+1), k)] for j in range(l)]

def average(n, k, l):
    # r = l / n
    # l = r * n
    return tuple([sum(x) / m for x in zip(*[solve(n, k, l) for i in range(int(m))])])

def dots(r):
    return '{:4.3f}'.format(r) + '\t' + '\t'.join([
        '\t'.join(
            [
                '{:4.3f} {:7.3f} {:7.3f}'.format(*average(n, k, int(r * n))) for n in N
            ]
        ) for k in K
    ]) + '\n'

def decode(result):
    result = result.strip().split('\n')

    # MiniSat output is in a two-column style, this is the offset
    # of the second column which holds the data.
    off = 24

    # Extract number of decisions made by MiniSat.
    decisions = int(result[-7][off:off+12].strip())

    # Extract excution time as reported by MiniSat.
    time = float(result[-3][off:-2])

    # Extract whether the formula is satisfiable or not.
    satisfiability = ['UNSATISFIABLE', 'SATISFIABLE'].index(result[-1])

    return (satisfiability, time, decisions)

def solve(n, k, l):
    ifd, ifname = mkstemp()

    # Write CNF to the input file in DIMACS format.
    with open(ifd, 'w') as f: f.write('\n'.join(
        ['c Team White'] +
        ['p cnf {} {}'.format(n, l)] +
        [' '.join(map(str, clause + [0])) for clause in randomize(n, k, l)]
    ))
    
    proc = run(['minisat', '-verb=2', ifname], stderr=STDOUT, stdout=PIPE)

    # Clean up once we are done. Otherwise we *will* run out of space.
    remove(ifname)

    return decode(proc.stdout.decode('utf-8'))

def main():
    with open('data-huge.dat', 'w+') as f:
        r = R[0]
        while r <= R[1]:
            f.write(dots(r))
            # For static delta:
            r += R[2]
            # For dynamic delta with "focal point" in the middle of the range:
            #r += R[2] + 0.07 * (r - R[0] - ((R[1] - R[0]) / 2.0)) ** 2.0

if __name__ == '__main__':
    main()
