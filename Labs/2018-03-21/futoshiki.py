import pyeda

from sys import stdin

def parse(pair):
    return tuple(map(int, pair[1:-1].split(',')))

def read(stream):
    gt = []
    fix = []
    n = -1

    for lno, line in enumerate(stream):
        idx = line.find('%')

        if idx == 0:
            continue
        if idx > 0:
            line = line[:idx]

        line = line.strip()
        if line == '':
            continue

        tk = line.split(' ')

        if tk[0] == '>':
            r, c = parse(tk[1])
            gt.append(((r, c), (r, c+1)))
        elif tk[0] == '<':
            r, c = parse(tk[1])
            gt.append(((r, c), (r, c-1)))
        elif tk[0] == '^':
            r, c = parse(tk[1])
            gt.append(((r-1, c), (r, c)))
        elif tk[0] == 'v':
            r, c = parse(tk[1])
            gt.append(((r+1, c), (r, c)))
        elif tk[0] == 'size':
            n = int(tk[1])
        else:
            r, c = parse(tk[1])
            fix.append((r, c, int(tk[0])))

    return (n, gt, fix)

def encode(gt,fix,n):
    futo = exprvars('x', (1,n), (1,n), (1,n))
    # Each cell on the board contains a unique value.
    vals = And(*[
             And(*[
                 OneHot(*[futo[row,col,val]
                     for val in range(1,n)])
                 for col in range(1,n)])
             for row in range(1,n)])
    # For each row, all cells have distinct values.
    rows = And(*[
             And(*[
                 OneHot(*[futo[row,col,val]
                     for col in range(1,n)])
                 for val in range(1,n)])
             for row in range(1,n)])
    # For each column, all cells have distinct values.
    cols = And(*[
             And(*[
                 OneHot(*[futo[row,col,val]
                     for row in range(1,n)])
                 for val in range(1,n)])
             for col in range(1,n)])
    ineqs = And(*[
              Or(*[
                Or(*[
                    And(futo[r1,c1,i],futo[r2,c2,j])
                    for i in range(j+1,n)])
                for j in range(1,n)])
              for ((r1,c1),(r2,c2)) in gt])
    fixes = And(*[futo(row,col,val) for (row,col,val) in fix])

    # Conjunction of constraints.
    sol = And(vals,rows,cols,ineqs,fixes)i

    return sol

def solve(grid):
    return grid.satisfy_one()

def decode(point, row, col, n):
    digits=range(1,n+1)
    for val in digits:
        if point[X[row,col,val]]:
            return str(digits[val-1])
    return "X"

def display(point,n):
    digits=range(1,n+1)
    chars = list()
    for row in digits:
        for col in digits:
            chars.append(decode(point, r, c))
        chars.append('\n')

    print("".join(chars))
    

read(stdin)
