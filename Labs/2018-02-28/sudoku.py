import sys
import os
import subprocess
from math import ceil

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

    try:
        # Strip visual splitting characters away
        line = list(raw.strip().replace('|', '').replace('.', '0'))
        # Convert to integers
        sudoku.append(list(map(int, line)))
    except:
        print('Invalid input on line {}!'.format(lno))
        sys.exit(1)

if len(sudoku) != 9:
    print('Invalid input!')
    sys.exit(1)

tmpdir = mkdtemp()
ifname = join(tmpdir, 'in')
ofname = join(tmpdir, 'out')

nonz = 0
for line in sudoku:
    for cell in line:
        if cell != 0:
            nonz = nonz + 1

clauses = 0
cnf = []

for i in range(1,10):
    for j in range(1,10):
        s = ''
        for k in range(1,10):
            s = s + "{}{}{} ".format(i, j, k)
        cnf.append(s)

for i in range(1,10):
    for j in range(1,10):
        for k in range(1,10):
            for l in range(k+1,10):
                cnf.append("-{}{}{} -{}{}{}".format(i,j,k,i,j,l))

for i in range(1,10):
    for j in range(1,10):
        for k in range(j+1,10):
            for d in range(1,10):
                cnf.append("-{}{}{} -{}{}{}".format(i,j,d,i,k,d))

for i in range(1,10):
    for k in range(i+1,10):
        for j in range(1,10):
            for d in range(1,10):
                cnf.append("-{}{}{} -{}{}{}".format(i,j,d,k,j,d))

for d in range(1, 10):
    for boxRow in range(3):
        for boxCol in range(3):
            for innerRowA in range(1,4):
                for innerColA in range(1,4):
                    for innerRowB in range(innerRowA,4):
                        for innerColB in range(innerColA,4):
                            if innerRowA != innerRowB or innerColA != innerColB:
                                cnf.append("-{}{}{} -{}{}{}".format(boxRow * 3 + innerRowA, boxCol * 3 + innerColA, d, boxRow * 3 + innerRowB, boxCol * 3 + innerColB, d))

for i in range(len(sudoku)):
    for j in range(len(sudoku[i])):
        if sudoku[i][j] != 0:
            cnf.append("{}{}{}".format((i+1), (j+1), sudoku[i][j]))

f = open(ifname, 'w+')
f.write('p cnf 999 {}\n'.format(len(cnf)))
f.write(' 0\n'.join(cnf) + ' 0\n')
f.close()

FNULL = open(os.devnull, 'w')
proc = subprocess.run(['minisat', ifname, ofname], stdout=FNULL)

with open(ofname, 'r') as f:
    result = f.read()

if result.startswith('UNSAT\n'):
    print('Sudoku has no solution.')
    sys.exit(0)

if not result.startswith('SAT\n'):
    print('Error')
    sys.exit(1)

result = result[4:-2]

for atom in result.split(' '):
    if len(atom) == 0:
        continue

    atom = int(atom)
    if atom < 100:
        continue

    x = int(atom / 100)
    y = int((atom % 100) / 10)
    sudoku[x-1][y-1] = atom % 10

for i, line in enumerate(sudoku):
    raw = list(map(str, line))
    print(''.join(raw[0:3]) + '|' + ''.join(raw[3:6]) + '|' + ''.join(raw[6:9]))

    if i == 2 or i == 5:
        print('---+---+---')
