# Team White

from copy       import deepcopy
from itertools  import product
from subprocess import DEVNULL, run
from sys        import argv, exit
from tempfile   import mkstemp

# The largest digit to used to fill out the sudoku. The smallest
# is fixed as 1. Also, the size (height and width) of the sudoku.
MAX_DIGIT = 9

# The size (height and width) of one subgrid in the sudoku.
# Usually the square root of the size of the full grid.
SUBGRID_SIZE = 3

SUBGRID_OFFSETS = range(0, MAX_DIGIT, SUBGRID_SIZE)
SUBGRID_INDICES = range(SUBGRID_SIZE)

def parse(f):
    """This routine parses all the sudoku schemas appearing in the input file.

    :param f: a text file.
    :returns: a list of schemas, which in turn are lists of lists.
    """
    result = []
    schema = []

    # lno is current line number
    # raw is the text as read from f without any alterations
    for lno, raw in enumerate(f):
        # Skip comment lines, middle lines, and empty lines.
        if raw.startswith('%') or raw == '---+---+---\n' or raw == '\n':
            continue

        line = []
        try:
            # Strip visual splitting characters away and convert to integers.
            line = list(map(int, raw.strip().replace('|', '').replace('.', '0')))
        except:
            print('Invalid input on line {}!'.format(lno))
            exit(1)

        # Note that MAX_DIGIT is the width of the schema.
        if len(line) != MAX_DIGIT:
            print('Expected {} cells on line {} but got {}'.format(MAX_DIGIT, lno, len(line)))
            exit(1)

        schema.append(line)

        # Note that MAX_DIGIT is the height of the schema.
        if len(schema) == MAX_DIGIT:
            result.append(schema)
            schema = []

    return result

def p(row, col, val):
    """Conversion from (row, col, val) to corresponding propositional variable.

    :returns: Corresponding proposition encoded as integer variable.
    """
    return row * MAX_DIGIT ** 2 + col * MAX_DIGIT + val + 1

def encode(schema):
    """This routine encodes a schema as CNF. Clauses are encoded as lists, so
       the CNF is encoded as a list of lists. Propositional variables
       are encoded as non-negative, non-zero integers.

    :param schema: the initial assignment of a sudoku.
    :returns: CNF encoding of the schema.
    """
    cnf = []

    # Range of numbers that are to be filled in,
    # using a zero-based encoding.
    digits = range(MAX_DIGIT)

    for i, j in product(digits, digits):
        # 1: "All cells contain at least one value".
        cnf.append([p(i, j, k) for k in digits])

        # Encoding of the initial assignment.
        if schema[i][j] != 0:
            # Shift schema[i][j] from one-based (human-readable)
            # to zero-based (CNF encoding).
            cnf.append([p(i, j, schema[i][j] - 1)])

        for d in digits:
            # 2: "All cells contain a unique value".
            #    p(i, j, d) -> -p(i, j, e) ... where e != d
            cnf += [[-p(i, j, d), -p(i, j, e)] for e in digits[d+1:]]

            for l in digits[i+1:]:
                # 3: "All the values in a row are distinct".
                cnf.append([-p(j, i, d), -p(j, l, d)])
                # 4: "All the values in a column are distinct".
                cnf.append([-p(i, j, d), -p(l, j, d)])

    # 5: "All the values in a box are distinct".
    for r0, c0, d in product(SUBGRID_OFFSETS, SUBGRID_OFFSETS, digits):
        for r1, c1 in product(SUBGRID_INDICES, SUBGRID_INDICES):
            for r2, c2 in product(SUBGRID_INDICES, SUBGRID_INDICES):
                if (r1, c1) < (r2, c2):
                    # p(r0 + r1, c0 + c1, d) -> -p(r0 + r2, c0 + r2, d)
                    cnf.append([-p(r0 + r1, c0 + c1, d), -p(r0 + r2, c0 + c2, d)])

    return cnf

def decode(schema, result):
    """This routine translates a MiniSat encoding of a model
       (if any) to a sudoku.

    :param schema: schema of a sudoku as a list of lists.
    :param result: the output of MiniSat, corresponding to the considered schema.
    :returns: if a solution for the schema can be extracted,
              the full sudoku as a list of lists, otherwise None.
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

        # Propositional variables interpreted as false are ignored.
        if p < 0:
            continue

        (x, p) = divmod(p - 1, MAX_DIGIT ** 2)
        (y, v) = divmod(p, MAX_DIGIT)

        # Shift v from zero-based (SAT encoding) to one-based (human-readable).
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

    dimacs = '\n'.join(
        ['c Team White'] +
        ['p cnf {} {}'.format(MAX_DIGIT ** 3, len(cnf))] +
        [' '.join(map(str, clause + [0])) for clause in cnf]
    )

    ifd, ifname = mkstemp()
    ofd, ofname = mkstemp()

    # Write CNF to the input file in DIMACS format.
    with open(ifd, 'w') as f: f.write(dimacs)

    proc = run(['minisat', ifname, ofname], stdout=DEVNULL)

    # Read from the output file and decode.
    with open(ofd, 'r') as f: return decode(schema, f.read())

def stringify(sudoku):
    """This routine renders the sudoku solution in graphical form, if it is solvable;
       otherwise, it returns "UNSOLVABLE".

    :param sudoku: matrix encoding of a sudoku.
    :returns: graphical representation of the sudoku if it is solvable, "UNSOLVABLE" otherwise.
    """
    if sudoku == None:
        return 'UNSOLVABLE\n'

    result = ''
    for i, line in enumerate(sudoku):
        line = list(map(str, line))
        result += '|'.join([''.join(line[i:i+SUBGRID_SIZE]) for i in SUBGRID_OFFSETS]) + '\n'

        if i + 1 in SUBGRID_OFFSETS:
            result += '---+---+---\n'

    return result

# Entry point of the program.
def main():
    if len(argv) != 2:
        print('Need exactly one argument.')
        exit(2)

    with open(argv[1], 'r') as f: [print(stringify(solve(schema))) for schema in parse(f)]

if __name__ == '__main__':
    main()
