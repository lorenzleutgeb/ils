# Team White

from pyeda.inter import *
from itertools   import product
from os          import remove
from subprocess  import PIPE, STDOUT, run
from sys         import argv, exit, stdin, stdout
from tempfile    import mkstemp

def totab(v, e):
    k = clog2(v)
    r = range(2 ** k)

    desired = [1 if (a, b) in e else 0 for (a, b) in product(r, r)]

    if sum(desired) != len(e):
        print('Truth table looks off.')

    s, t = exprvars('s', k), exprvars('t', k)

    return s, t, truthtable(t + s, ''.join(map(str, desired))), k

def parse(f):
    E = []

    for lno, row in enumerate(f):
        state = row.split(' ')

        if len(state) != 3 :
            print('Invalid input file')
            exit(1)

        if not (state[0].isdigit() or state[2].isdigit()):
            print('Contains invalid characters')
            exit(1)

        if not (state[1] == '->'):
            print('Not a transion state')
            exit(1)

        E.append((int(state[0]) - 1, int(state[2]) - 1))
        V = max([max(a,b) for (a,b) in E])

    return (V,E)

# True if dst can be reached via src in *exactly* d transitions.
# src and dst should be states using zero-based indexing!
def reachableExactly(d, f, s, t, k, src, dst):
    if d < 0:
        return False

    if d == 0:
        return src == dest

    sv = exprvars('sv', d + 1, k)

    src = num2point(src, sv[0])
    dst = num2point(dst, sv[d])

    return And(
        *[Equal(*it) for it in src.items()],
        *[
            f.compose(dict(list(zip(s, sv[i])) + list(zip(t, sv[i + 1]))))
            for i in range(d)
        ],
        *[Equal(*it) for it in dst.items()]
    )

# True if dst can be reached via src in *at most* d transitions.
# src and dst should be states using zero-based indexing!
def reachableAtMost(d, f, s, t, k, src, dst):
    if d < 0:
        return False

    if d == 0:
        return src == dest

    sv = exprvars('sv', d + 1, k)

    src = num2point(src, sv[0])

    return And(
        *[Equal(*it) for it in src.items()],
        *[
            f.compose(dict(list(zip(s, sv[i])) + list(zip(t, sv[i + 1]))))
            for i in range(d)
        ],
        Or(*[
            And(*[Equal(*it) for it in num2point(dst, sv[i]).items()])
            for i in range(1, d + 1)
        ])
    )

def diameter(d, f, s, t, k):
    sv = exprvars('sv', d + 2, k)
    tv = exprvars('tv', d + 1, k)

    return sv, tv, Implies(
        And(*[
            f.compose(dict(list(zip(s, sv[i])) + list(zip(t, sv[i + 1]))))
            for i in range(d + 1)
        ]),
        And(
            *[Equal(*it) for it in zip(tv[0], sv[0])],
            *[
                f.compose(dict(list(zip(s, tv[i])) + list(zip(t, tv[i + 1]))))
                for i in range(d)
            ],
            Or(*[
                And(*[Equal(*it) for it in zip(tv[i], sv[d + 1])])
                for i in range(d + 1)
            ])
        )
    )

def to_qdimacs(quants, expr):
    result = ''
    props, dimacs = expr2dimacscnf(expr.to_cnf())

    dimacs = str(dimacs).split('\n')

    result = dimacs[0] + '\n'

    for q, vs in quants:
        vs = list(filter(lambda x: x in props, vs))

        if len(vs) == 0:
            continue

        result += '{} {} 0\n'.format(q, ' '.join(map(lambda x: str(props[x]), vs)))

    result += '\n'.join(dimacs[1:])
    print(result)
    return result

def solve(quants, expr):
    ifd, ifname = mkstemp()

    with open(ifd, 'w') as f: f.write(to_qdimacs(quants, expr))
    proc = run(['depqbf', '--no-dynamic-nenofex', '--qdo', ifname], stderr=STDOUT, stdout=PIPE)
    remove(ifname)

    return proc.stdout.decode('utf-8').strip().split('\n')

def main():
    with open(argv[1], 'r') as f:
        v, e = parse(f)

        s, t, tab, k = totab(v, e)
        print('Truth Table of Transition Function (LSBs are at 0):')
        print(tab)

        for d in range(1, 2 ** v):
            svs, tvs, ex = diameter(d, tab, s, t, k)
            quants = [
                ('a', [sv[i] for sv, i in product(svs, range(k))]),
                ('e', [tv[i] for tv, i in product(tvs, range(k))])
            ]

            print(d, solve(quants, ex))

if __name__ == '__main__':
    main()
