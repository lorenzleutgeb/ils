# Team White

from pyeda.inter import exprvars, And, Implies, Not, OneHot, Or
from itertools   import combinations, product
from sys         import stdin

def parse(pair):
    return tuple(map(lambda x: int(x) - 1, pair[1:-1].split(',')))

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

        a, b = line.split(' ')

        if a == 'size':
            n = int(b)
            continue

        r, c = parse(b)

        if a == '>':
            gt.append(((r, c), (r, c + 1)))
        elif a == '<':
            gt.append(((r, c), (r, c - 1)))
        elif a == '^':
            gt.append(((r, c), (r - 1, c)))
        elif a == 'v':
            gt.append(((r, c), (r + 1, c)))
        else:
            fix.append((r, c, int(a) - 1))

    return n, gt, fix

def solve(n, gt, fix):
    r = (0, n)
    d, f = range(*r), exprvars('f', r, r, r)
    return f, And(
        *[  # Each cell contains a unique value.
            OneHot(*[f[r, c, v] for v in d])
            for r, c in product(d, d)
        ],
        *[  # For each row, all cells have distinct values.
            OneHot(*[f[r, c, v] for c in d])
            for r, v in product(d, d)
        ],
        *[  # Inequalities
            Implies(f[r1,c1,v1], Not(f[r2,c2,v2]))
            for ((r1,c1), (r2,c2)), (v1, v2) in product(gt, combinations(d, 2))
        ],
        *[  # Initial assignment
            f[r, c, v] for r, c, v in fix
        ],
        *[  # For each column, all cells have distinct values.
            OneHot(*[f[r, c, v] for r in d])
            for c, v in product(d, d)
        ]
    ).satisfy_one()

def display(f, model):
    if model == None:
        print('UNSOLVABLE')
        return

    d = range(0, len(f))
    print('\n'.join([
        ' '.join([
            ''.join([
                str(v + 1) if model[f[r, c, v]] else '' for v in d
            ]) for c in d
        ]) for r in d
    ]))

display(*solve(*read(stdin)))
