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
    e = []

    for lno, ln in enumerate(f):
        ln = list(map(lambda x: x.strip(), ln.split('->')))

        if len(ln) != 2 or not ln[0].isdigit() or not ln[1].isdigit():
            print('Invalid input on line {}'.format(lno))
            exit(1)

        e.append(tuple(map(lambda x: int(x) - 1, ln)))

    return max([max(a, b) for a, b in e]) + 1, e

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
    props, dimacs = expr2dimacscnf(expr.to_cnf())
    dimacs = str(dimacs).split('\n')

    qs = []
    for q, vs in quants:
        vs = list(filter(lambda x: x in props, vs))

        if len(vs) == 0:
            continue

        qs.append('{} {} 0'.format(q, ' '.join(map(lambda x: str(props[x]), vs))))

    return '\n'.join([dimacs[0]] + qs + dimacs[1:])

def solve(quants, expr):
    ifd, ifname = mkstemp()

    with open(ifd, 'w') as f: f.write(to_qdimacs(quants, expr))
    proc = run(['depqbf', '--no-dynamic-nenofex', '--qdo', ifname], stderr=STDOUT, stdout=PIPE)
    remove(ifname)

    return sat(proc.stdout.decode('utf-8'))

def sat(output):
    result = int(output.strip().split('\n')[0].split(' ')[2])

    if result not in {0, 1}:
        print('Indeterminate result!')
        exit(1)

    return result

def main():
    with open(argv[len(argv) - 1], 'r') as f:
        v, e = parse(f)
        s, t, tab, k = totab(v, e)

        if '--table' in argv:
            print('Truth Table of Transition Function (LSBs at 0):')
            print(tab)

        tab = truthtable2expr(tab)

        for d in range(v):
            svs, tvs, ex = diameter(d, tab, s, t, k)
            quants = [
                ('a', [sv[i] for sv, i in product(svs, range(k))]),
                ('e', [tv[i] for tv, i in product(tvs, range(k))])
            ]

            if solve(quants, ex):
                print(d)
                exit(0)

        print('?')
        exit(2)

if __name__ == '__main__':
    main()
