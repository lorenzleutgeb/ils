from itertools  import product
from math       import ceil
from os         import devnull
from os.path    import join
from subprocess import run
from sys        import argv, exit, stdin
from tempfile   import mkdtemp

def parse(f):
    sudokus = [[]]

    for lno, raw in enumerate(f):
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
            exit(1)

        if len(line) != 9:
            print('Expected 9 cells on line {} but got {}'.format(lno, len(line)))
            exit(1)

        sudokus[-1].append(line)

        if len(sudokus[-1]) == 9:
            sudokus.append([])

    return sudokus[:-1] if sudokus[-1] == [] else sudokus

def encode(sudoku):
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

    return cnf

def decode(sudoku, result):
    if result.startswith('UNSAT\n'):
        return None

    if not result.startswith('SAT\n'):
        print('Error!')
        exit(1)

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
            exit(1)
        else:
            sudoku[x][y] = v

    return sudoku

def solve(sudoku):
    cnf = encode(sudoku)

    tmpdir = mkdtemp()
    ifname = join(tmpdir, 'in')
    ofname = join(tmpdir, 'out')

    with open(ifname, 'w+') as f:
        f.write('p cnf 889 {}\n'.format(len(cnf)))
        for clause in cnf:
            f.write(' '.join(map(str, clause + [0])) + '\n')

    null = open(devnull, 'w')
    proc = run(['minisat', ifname, ofname], stdout=null)

    with open(ofname, 'r') as f:
        result = f.read()

    return decode(sudoku, result)

def stringify(sudoku):
    if sudoku == None:
        return 'UNSOLVABLE'

    result = ''
    for i, line in enumerate(sudoku):
        raw = list(map(str, line))
        result += ''.join(raw[0:3]) + '|' + ''.join(raw[3:6]) + '|' + ''.join(raw[6:9]) + '\n'

        if i == 2 or i == 5:
            result += '---+---+---\n'

    return result

def main():
    if len(argv) != 2:
        print('Need exactly one argument.')
        exit(2)

    with open(argv[1], 'r') as f:
        print('\n'.join([stringify(solve(sudoku)) for sudoku in parse(f)]))

if __name__ == '__main__':
    main()
