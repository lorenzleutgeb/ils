# Team White

from subprocess import PIPE, STDOUT, run
from tempfile   import mkstemp
from random     import random

# n ... Number of Variables
# k ... Number of Literals per Clause
# l ... Number of Clauses

k = 3
N = [50, 100, 200]

# Number of experiments to run in order to determine p.
m = 100.0

R = (1.0, 6.0, 0.01)

def randomize(n, k, l):
    return [[1 + int(n * random()) * (-1) * round(random()) for j in range(k)] for i in range(l)]

def decode(result):
    if result.endswith(b'UNSATISFIABLE\n'):
        return False
    elif result.endswith(b'SATISFIABLE\n'):
        return True
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
    proc = run(['minisat', ifname], stderr=STDOUT, stdout=PIPE)
    return decode(proc.stdout)

def p(n, k, l):
    x = 0.0
    for i in range(int(m)):
        if solve(n, k, l):
            x += 1.0

    return x / m

def main():
    with open('satisfiability.dat', 'w+') as f:
        f.write('# r {}\n'.format(N))

        r = R[0]
        while r <= R[1]:
            # r = l / n
            # l = r * n
            f.write('{:4.3f}\t'.format(r) + '\t'.join(['{:4.3f}'.format(p(n, k, int(r * n))) for n in N]) + '\n')
            r += R[2]

if __name__ == '__main__':
    main()
