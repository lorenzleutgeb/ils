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

for i in range(1,9):
    s = ""
    for j in range(1,9):
        for k in range(1,9):
            s += "{}{}{} ".format(i*100, j*10, k)
        s += "0"
        f.write(s)

for i in range(1,9):
    for j in range(1,9):
        for k in range(1,9):
            for l in range(k+1,9):
                f.write("-{}{}{} -{}{}{} 0".format(i*100,j*10,k,i*100,j*10,l))

for i in range(1,9):
    for j in range(1,9):
        for k in range(j+1,9):
            for d in range(1,9):
                f.write("-{}{}{} -{}{}{} 0".format(i*100,j*10,d,i*100,k*10,d))

for i in range(1,9):
    for k in range(i+1,9):
        for j in range(1,9):
            for d in range(1,9):
                f.write("-{}{}{} -{}{}{} 0".format(i*100,j*10,d,k*100,j*10,d))

for d in range(1,9):
    for i in range(1,9):
        for j in range(i+1,9):
            for ro in range(3):
                for co in range(3):
                    f.write("-{}{}{} -{}{}{}".format((3*ro + i)/ 3,(3*co + i)%3,d,(3*ro + j)/3,(3*co + j)%3,d))

for i in range(len(sudoku)):
    for j in range(len(sudoku[i])):
        if sudoku[i][j] != 0:
            f.write("{}{}{} 0".format((i+1)*100, (j+1)*10, sudoku[i][j]))

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
