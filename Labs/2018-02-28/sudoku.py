import sys
import subprocess

from tempfile import mkdtemp
from os.path import join

sudoku = []
lno = 0

for raw in sys.stdin:
    lno = lno + 1

    if raw[0] == '%':
        continue
    elif raw.startswith('---+---+---'):
        continue
    elif len(raw) == 0:
        continue

    try:
        line = list(raw.strip().replace('|', '').replace('.', '0'))
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

# Solve sudoku!
f = open(ifname, 'w+')
#f.write('p cnf 1 2\n1 0 -1 0')
f.write('p cnf 1 1\n1 0')
f.close()

proc = subprocess.run(['minisat', ifname, ofname])

with open(ofname, 'r') as f:
    result = f.read()
    print(result)

if result.startswith('UNSAT\n'):
    print('Sudoku has no solution.')
    sys.exit(0)

if not result.startswith('SAT\n'):
    print('Error')
    sys.exit(1)

result = result[4:-2]
print(result)
sys.exit(0)

for i, line in enumerate(sudoku):
    raw = list(map(str, line))
    print(''.join(raw[0:3]) + '|' + ''.join(raw[3:6]) + '|' + ''.join(raw[6:9]))

    if (i + 1) % 3 == 0:
        print('---+---+---')
