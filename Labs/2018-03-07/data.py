# Team White

from subprocess import PIPE, STDOUT, run
from tempfile   import mkstemp
from random     import choice, sample

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# n ... Number of Variables
# k ... Number of Literals per Clause
# l ... Number of Clauses

k = 3
N = [50, 100, 200]

# Number of experiments to run in order to determine p.
m = 50.0

R = (2.0, 6.0, 0.05)

def randomize(n, k, l):
    return [[p * -1 if choice([True, False]) else p for p in sample(range(1, n+1), k)] for j in range(l)]

def decode(result):
    result = result.strip().split('\n')
    time = float(result[-3][len('CPU time              : '):-len(' s')])
    if result[-1] == 'UNSATISFIABLE':
        return (False, time)
    elif result[-1] == 'SATISFIABLE':
        return (True, time)
    else:
        print('Neither satisfiable nor satisfiable!')
        exit(1)

def solve(n, k, l):
    cnf = randomize(n, k, l)

    dimacs = '\n'.join(
        ['c Team White'] +
        ['p cnf {} {}'.format(n, l)] +
        [' '.join(map(str, clause + [0])) for clause in cnf]
    )

    ifd, ifname = mkstemp()

    # Write CNF to the input file in DIMACS format.
    with open(ifd, 'w') as f: f.write(dimacs)
    proc = run(['minisat', '-verb=2', ifname], stderr=STDOUT, stdout=PIPE)
    return decode(proc.stdout.decode('utf-8'))

def p(n, k, l):
    x = 0.0
    totaltime = 0.0
    for i in range(int(m)):
        (satisfiability, time) = solve(n, k, l)
        if satisfiability:
            x += 1.0
        totaltime += time

    return (x / m, totaltime / m)

def main():
    with open('data.dat', 'w+') as f:
        f.write('# r {}\n'.format(N))

        r = R[0]
        while r <= R[1]:
            # r = l / n
            # l = r * n
            f.write('{:4.3f}\t'.format(r) + '\t'.join(['{:4.3f} {:4.3f}'.format(*p(n, k, int(r * n))) for n in N]) + '\n')
            r += R[2] + 0.07 * (r - R[0] - ((R[1] - R[0]) / 2.0)) ** 2.0

if __name__ == '__main__':
    main()
