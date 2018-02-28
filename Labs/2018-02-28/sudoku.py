import sys
import os
import subprocess
from math import ceil

from itertools import product
from tempfile import mkdtemp
from os.path import join

sudoku = []

# Counts the number of lines being read
lno = 0

for raw in sys.stdin:
    lno = lno + 1

    # Skip comment lines
    if raw[0] == '%':
        continue
    # Skip middle lines
    elif raw.startswith('---+---+---'):
        continue
    # Skip empty lines
    elif len(raw) == 0:
        continue

    line = []
    try:
        # Strip visual splitting characters away
        line = list(raw.strip().replace('|', '').replace('.', '0'))
        # Convert to integers
        line = list(map(int, line))
    except:
        print('Invalid input on line {}!'.format(lno))
        sys.exit(1)

    if len(line) != 9:
        print('Expected 9 cells on line {} but got {}'.format(lno, len(line)))
        sys.exit(1)

    sudoku.append(line)

if len(sudoku) != 9:
    print('Invalid input!')
    sys.exit(1)

tmpdir = mkdtemp()
ifname = join(tmpdir, 'in')
ofname = join(tmpdir, 'out')

clauses = 0
cnf = []

digits = range(1,10)

def p(x, y, v):
    return x * 100 + y * 10 + v - 110

for (i, j) in product(digits, digits):
    # 1 (all cells filled)
    cnf.append([p(i, j, k) for k in digits])

    # (input)
    if sudoku[i - 1][j - 1] != 0:
        cnf.append([p(i, j, sudoku[i - 1][j - 1])])

    for d in digits:
        # 2 (unique)
        cnf += [[-p(i, j, d), -p(i, j, e)] for e in range(d + 1, 10)]

        for l in range(i + 1, 10):
            # 3 (row)
            cnf.append([-p(j, i, d), -p(j, l, d)])
            # 4 (column)
            cnf.append([-p(i, j, d), -p(l, j, d)])

for (br, bc, d) in product(range(3), range(3), digits):
    for (ora, oca) in product(range(1, 4), range(1, 4)):
        for (orb, ocb) in product(range(ora + 1, 4), range(oca + 1, 4)):
            cnf.append([-p(br * 3 + ora, bc * 3 + oca, d), -p(br * 3 + orb, bc * 3 + ocb, d)])

with open(ifname, 'w+') as f:
    f.write('p cnf 889 {}\n'.format(len(cnf)))
    for clause in cnf:
        f.write(' '.join(map(str, clause + [0])) + '\n')

null = open(os.devnull, 'w')
proc = subprocess.run(['minisat', ifname, ofname], stdout=null)

with open(ofname, 'r') as f:
    result = f.read()

if result.startswith('UNSAT\n'):
    print('UNSOLVABLE')
    sys.exit(0)

if not result.startswith('SAT\n'):
    print('Error!')
    sys.exit(1)

result = result[4:-2]

for p in result.split(' '):
    if len(p) == 0:
        continue

    p = int(p)

    if p < 0:
        continue

    p = int(p) + 110
    x = int(p / 100) - 1
    y = int((p % 100) / 10) - 1
    v = p % 10

    if sudoku[x][y] != 0 and sudoku[x][y] != v:
        print('Solution conflicts with input!')
        sys.exit(1)
    else:
        sudoku[x][y] = v

for i, line in enumerate(sudoku):
    raw = list(map(str, line))
    print(''.join(raw[0:3]) + '|' + ''.join(raw[3:6]) + '|' + ''.join(raw[6:9]))

    if i == 2 or i == 5:
        print('---+---+---')
