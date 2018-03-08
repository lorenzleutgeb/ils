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
    """A k-CNF formulae generator.

    :param n: number of variables in the formula
    :param k: number of literals per clause
    :param l: number of clauses in the formula
    :returns: a list of length l, where each element is a list of k different non-zero elements in the range [-n..n]
    """
    return [[p * -1 if choice([True, False]) else p for p in sample(range(1, n+1), k)] for j in range(l)]

def average(n, k, l):
    """Routine that returns the mean value of the results obtained after running m experiments.

    :param n: number of variables in the formula
    :param k: number of literals per clause
    :param l: number of clauses in the formula
    :returns: a tuple, containing the average satisfiability ('1' for SATISFIABLE/'0' for UNSATISFIABLE),
              the average CPU time for an experiment and the average number of decisions taken by the MiniSat solver
    """
    # r = l / n
    # l = r * n
    return tuple([sum(x) / m for x in zip(*[solve(n, k, l) for i in range(int(m))])])

def dots(r):
    """Routine that provides, for each chosen value in [R[0]..R[1]], the mean values of the samples obtained
    by changing the value of literals per clause and variables considered and running a fixed number of experiments.

    :param r: a floating-point number in the range [R[0]..R[1]]
    :returns: a string, representing a table of records; each record is of the form 'J K L', where
              (J,K,L) = average(n, k, int(r * n)) for some n (number of variables) and k (literals per clause)
    """
    return '{:4.3f}'.format(r) + '\t' + '\t'.join([
        '\t'.join(
            [
                '{:4.3f} {:7.3f} {:7.3f}'.format(*average(n, k, int(r * n))) for n in N
            ]
        ) for k in K
    ]) + '\n'

def decode(result):
    """Routine that returns relevant information about a run of MiniSat.

    :param result: output of the an execution of MiniSat
    :returns: a triple containing the response of MiniSat ('1' for SATISFIABLE/'0' for UNSATISFIABLE), the CPU time and
              the number of decisions taken by MiniSat during its execution
    """
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
    """Routine that solves a k-SAT instance with n variables and l clauses.

    :param n: number of variables in the formula
    :param k: number of literals per clause
    :param l: number of clauses in the formula
    :returns: a triple containing the response of MiniSat ('1' for SATISFIABLE/'0' for UNSATISFIABLE), the CPU time and
              the number of decisions taken by MiniSat during its execution
    """
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

# Entry point of the program.
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
