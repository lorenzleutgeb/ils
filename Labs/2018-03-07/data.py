# Team White

from os         import remove
from subprocess import PIPE, STDOUT, run
from sys        import stdout
from tempfile   import mkstemp
from random     import choice, sample, getrandbits

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas.tseries as ts

# List to choose k from.
setups = [
    #k   r_min r_max   n
    (3, (    3,  5.5), [20, 30]),
    (5, (   19, 25  ), [50, 100     ])
]

# Number of experiments to run in order to smoothen result.
m = 50.0

# K-SAT:
# n ... Number of Variables
# k ... Number of Literals per Clause
# l ... Number of Clauses
def randomize_fixed(n, k, l):
    """A k-CNF formulae generator.

    :param n: number of variables in the formula
    :param k: number of literals per clause
    :param l: number of clauses in the formula
    :returns: a list of length l, where each element is a list of k different non-zero elements in the range [-n..n]
    """
    return [[-p if choice([True, False]) else p for p in sample(range(1, n+1), k)] for j in range(l)]

# P-SAT:
# n ... Number of Variables
# p ... Probability of Inclusion
# l ... Number of Clauses
def randomize_density(n, p, l):
    cnf = []
    for j in range(l):
        clause = []
        for i in range(n):
            # Choose i with probability p.
            if random() >= p:
                continue

            # Negate with probability 0.5.
            clause.append(-i if choice([True, False]) else i)

        # Skip empty clause and unit clauses.
        if len(clause) > 1:
            cnf.append(clause)
    return cnf

# Runs m experiments and averages the results.
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
    return tuple([sum(x) / m for x in zip(*[experiment(n, k, l) for i in range(int(m))])])

def dots(r, k, N):
    """Routine that provides, for each chosen value in [R[0]..R[1]], the mean values of the samples obtained
    by changing the value of literals per clause and variables considered and running a fixed number of experiments.

    :param r: a floating-point number in the range [R[0]..R[1]]
    :returns: a string, representing a table of records; each record is of the form 'P T L', where
              (P,T,L) = average(n, k, int(r * n)) for some n (number of variables) and k (literals per clause)
    """
    return (r, [average(n, k, int(r * n)) for n in N])

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
    satisfiability = 'SATISFIABLE' == result[-1]

    return (satisfiability, time, decisions)

def experiment(n, k, l):
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
        [' '.join(map(str, clause + [0])) for clause in randomize_fixed(n, k, l)]
    ))

    proc = run(['minisat', '-verb=2', '-cpu-lim=30', ifname], stderr=STDOUT, stdout=PIPE)

    # Clean up once we are done. Otherwise we *will* run out of space.
    remove(ifname)

    return decode(proc.stdout.decode('utf-8'))

# Entry point of the program.
def main():

    for setup in setups:
        k, (rmin, rmax), N = setup
        dump = 'data-{}-{:x}.dat'.format(k, getrandbits(16))
        with open(dump, 'w+') as f:
            rvalues = []
            pvalues = []
            print('Running for k = {} from {} to {} using {}.'.format(k, rmin, rmax, dump))
            r = rmin
            while r <= rmax:
                line = dots(r, k, N)
            #    rvalues.append(r)
                p = line[1][0][0]
            #    pvalues.append(p)
            #    stdout.write(line)
            #    f.write(line)
                # For static delta:
                r += 0.1

                # For dynamic delta with "focal point" in the middle of the range:
                #r += 0.1 + 0.2 * (r - R[0] - ((R[1] - R[0]) / 2.0)) ** 2.0

            data=np.loadtxt('data-5.dat')
            df = pd.DataFrame(data[:,1],data[:,0])

            #x=data[:,1]
            #y=data[:,2]

            #plt.plot(x,y,':ro')
            #plt.show()

        #df = pd.DataFrame(rvalues, pvalues)

        plt.figure()
        df.plot().get_figure().savefig('test12.pdf')

        return


if __name__ == '__main__':
    main()
