from itertools  import product
from math       import ceil
from os         import devnull
from os.path    import join
from subprocess import run
from sys        import argv, exit, stdin
from tempfile   import mkdtemp

# This routine parses all the sudoku schemas appearing in the input file.
# 
# input: a text file
# output: a collection of sudokus, in matrix encoding.
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


# This routine encodes a sudoku in DIMACS form.
# 
# input: matrix encoding of the initial assignment of the sudoku.
# output: DIMACS CNF encoding of the sudoku schema.
def encode(sudoku):
    cnf = []
    digits = range(1,10)

    # conversion from (row, col, val) to corresponding variable
    # in DIMACS encoding. Value 110 used as a translational offset
    # (111 first possible variable).
    def p(x, y, v):
        return x * 100 + y * 10 + v - 110

    for (i, j) in product(digits, digits):
        # 1: "All cells contain at least one value".
        cnf.append([p(i, j, k) for k in digits])

        # Encoding of the initial assignment.
        if sudoku[i - 1][j - 1] != 0:
            cnf.append([p(i, j, sudoku[i - 1][j - 1])])

        for d in digits:
            # 2: "All cells contain a unique value".
            cnf += [[-p(i, j, d), -p(i, j, e)] for e in range(d + 1, 10)]

            for l in range(i + 1, 10):
                # 3: "All the values in a row are distinct".
                cnf.append([-p(j, i, d), -p(j, l, d)])
                # 4: "All the values in a column are distinct".
                cnf.append([-p(i, j, d), -p(l, j, d)])

    # 5: "All the values in a box are distinct".
    for (br, bc, d) in product(range(3), range(3), digits):
        for (ora, oca) in product(range(1, 4), range(1, 4)):
            for (orb, ocb) in product(range(ora + 1, 4), range(oca + 1, 4)):
                cnf.append([-p(br * 3 + ora, bc * 3 + oca, d), -p(br * 3 + orb, bc * 3 + ocb, d)])

    return cnf


# This routine translates a DIMACS CNF encoding of the solution (if any) to matrix encoding.
#
# input: DIMACS CNF encoding of the solution
# output: if the schema is satisfiable, an updated version of the matrix encoding is returned.
def decode(sudoku, result):
    if result.startswith('UNSAT\n'):
        return None

    if not result.startswith('SAT\n'):
        print('Error!')
        exit(1)

    # Keeps the part of the output of the solver containing the truth assignment.
    result = result[4:-2]

    for p in result.split(' '):
        if len(p) == 0:
            continue

        p = int(p)

        # If the variable is set to FALSE, the schema is not updated.
        if p < 0:
            continue

        # If the variable is set to TRUE, we update the schema.
        # if p = xyv, the cell (x,y) is set to value v.
        p = int(p) + 110
        x = int(p / 100) - 1
        y = int((p % 100) / 10) - 1
        v = p % 10

        # If a value in the schema is overwritten, an error is returned.
        if sudoku[x][y] != 0 and sudoku[x][y] != v:
            print('Solution conflicts with input!')
            exit(1)
        else:
            sudoku[x][y] = v

    return sudoku

# This routine takes as input the sudoku schema as a matrix, encodes it in DIMACS form,
# then calls the 'minisat' solver and decodes its output.
#
# input: a sudoku in matrix encoding
# output: the solved sudoku.
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

# This routine renders the sudoku solution in graphical form, if it is solvable;
# otherwise, it returns "UNSOLVABLE".
#
# input: matrix encoding of the sudoku.
# output: graphical representation of the sudoku if it is solvable,
#         "UNSOLVABLE" otherwise.
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

# Entry point of the program.
def main():
    if len(argv) != 2:
        print('Need exactly one argument.')
        exit(2)

    with open(argv[1], 'r') as f:
        print('\n'.join([stringify(solve(sudoku)) for sudoku in parse(f)]))

if __name__ == '__main__':
    main()
