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
