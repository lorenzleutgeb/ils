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

read(stdin)
