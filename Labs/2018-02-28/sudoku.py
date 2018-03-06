from copy       import deepcopy
from itertools  import product
from math       import ceil
from os         import devnull
from os.path    import join
from subprocess import run
from sys        import argv, exit, stdin
from tempfile   import mkdtemp

def parse(f):
    """This routine parses all the sudoku schemas appearing in the input file.

    :param f: a text file.
    :returns: a collection of schemas, in matrix encoding.
    """
    schemas = [[]]

    # lno is current line number
    # raw is the text as read from f without any alterations
    for lno, raw in enumerate(f):
        # Skip comment lines
        if raw.startswith('%'):
            continue
        # Skip middle lines
        elif raw == '---+---+---\n':
            continue
        # Skip empty lines
        elif len(raw) == 0:
            continue

        line = []
        try:
            # Strip visual splitting characters away and convert to integers.
            line = list(map(int, raw.strip().replace('|', '').replace('.', '0')))
        except:
            print('Invalid input on line {}!'.format(lno))
            exit(1)

        if len(line) != 9:
            print('Expected 9 cells on line {} but got {}'.format(lno, len(line)))
            exit(1)

        schemas[-1].append(line)

        if len(schemas[-1]) == 9:
            schemas.append([])

    return schemas[:-1] if schemas[-1] == [] else schemas

def p(row, col, val):
    """Conversion from (row, col, val) to corresponding variable

    :returns: Corresponding proposition encoded as integer.
    """
    return (row - 1) * 81 + (col - 1) * 9 + (val - 1) + 1

def encode(schema):
    """This routine encodes a schema in DIMACS form.

    :param schema: matrix encoding of the initial assignment of a sudoku schema.
    :returns: DIMACS CNF encoding of the schema.
    """
    cnf = []
    digits = range(1,10)

    for (i, j) in product(digits, digits):
        # 1: "All cells contain at least one value".
        cnf.append([p(i, j, k) for k in digits])

        # Encoding of the initial assignment.
        if schema[i - 1][j - 1] != 0:
            cnf.append([p(i, j, schema[i - 1][j - 1])])

        for d in digits:
            # 2: "All cells contain a unique value".
            #    p(i, j, d) -> -p(i, j, e) ... where e != d
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

def decode(schema, result):
    """This routine translates a DIMACS CNF encoding of the solution
       (if any) to matrix encoding.

    :param schema: matrix encoding of a schema.
    :param result: the output of minisat, relative to the considered schema.
    :returns: if the schema is satisfiable, an updated version of the matrix encoding is returned.
    """
    if result.startswith('UNSAT\n'):
        return None

    if not result.startswith('SAT\n'):
        print('Error!')
        exit(1)

    sudoku = deepcopy(schema)

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
        (x, p) = divmod(p - 1, 81)
        (y, v) = divmod(p, 9)
        v += 1

        # If a value in the schema is overwritten, the execution is halted.
        if schema[x][y] != 0 and schema[x][y] != v:
            print('Solution conflicts with input!')
            exit(1)
        else:
            sudoku[x][y] = v

    return sudoku

def solve(schema):
    """This routine takes as input the schema schema as a matrix,
       encodes it in DIMACS form, then calls the 'minisat' solver
       and decodes its output.
    :param schema: matrix encoding of a schema.
    :returns: the matrix encoding of the solved schema.
    """
    cnf = encode(schema)

    tmpdir = mkdtemp()
    ifname = join(tmpdir, 'in')
    ofname = join(tmpdir, 'out')

    with open(ifname, 'w+') as f:
        f.write('p cnf 729 {}\n'.format(len(cnf)))
        for clause in cnf:
            f.write(' '.join(map(str, clause + [0])) + '\n')

    null = open(devnull, 'w')
    proc = run(['minisat', ifname, ofname], stdout=null)

    with open(ofname, 'r') as f:
        result = f.read()

    return decode(schema, result)

def stringify(sudoku):
    """This routine renders the sudoku solution in graphical form, if it is solvable;
       otherwise, it returns "UNSOLVABLE".

    :param sudoku: matrix encoding of a sudoku.
    :returns: graphical representation of the sudoku if it is solvable, "UNSOLVABLE" otherwise.
    """
    if sudoku == None:
        return 'UNSOLVABLE'

    result = ''
    for i, line in enumerate(sudoku):
        raw = list(map(str, line))
        result += '|'.join([''.join(raw[i:i+3]) for i in range(0, 9, 3)]) + '\n'

        if i == 2 or i == 5:
            result += '---+---+---\n'

    return result

# Entry point of the program.
def main():
    if len(argv) != 2:
        print('Need exactly one argument.')
        exit(2)

    with open(argv[1], 'r') as f:
        print('\n'.join([stringify(solve(schema)) for schema in parse(f)]))

if __name__ == '__main__':
    main()
