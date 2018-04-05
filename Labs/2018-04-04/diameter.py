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

    return s, t, truthtable(t + s, ''.join(map(str, desired)))

def parse(f):
    e = []

    for lno, ln in enumerate(f):
        ln = list(map(lambda x: x.strip(), ln.split('->')))

        if len(ln) != 2 or not ln[0].isdigit() or not ln[1].isdigit():
            print('Invalid input on line {}'.format(lno))
            exit(1)

        e.append(tuple(map(lambda x: int(x) - 1, ln)))

    return max([max(a, b) for a, b in e]) + 1, e

def diameter(d, f, s, t):
    k = len(s)

    sv = exprvars('sv', d + 2, k)
    tv = exprvars('tv', d + 1, k)

    qs = [
        ('a', [xs[i] for xs, i in product(sv, range(k))]),
        ('e', [xt[i] for xt, i in product(tv, range(k))])
    ]

    def transition(src, dst):
        return f.compose(dict(list(zip(s, src)) + list(zip(t, dst))))

    def same(a, b):
        return And(*[Equal(*it) for it in zip(a, b)])

    return sv, qs, Implies(
        And(*[transition(sv[i], sv[i + 1]) for i in range(d + 1)]),
        And(
            same(tv[0], sv[0]),
            *[transition(tv[i], tv[i + 1]) for i in range(d)],
            Or(*[same(tv[i], sv[d + 1]) for i in range(d + 1)])
        )
    )

def to_qdimacs(props, dimacs, quants):
    dimacs = str(dimacs).split('\n')

    qs = []
    for q, vs in quants:
        vs = list(filter(lambda x: x in props, vs))

        if len(vs) == 0:
            continue

        qs.append('{} {} 0'.format(q, ' '.join(map(lambda x: str(props[x]), vs))))

    return '\n'.join([dimacs[0]] + qs + dimacs[1:])

def solve(svs, quants, expr):
    props, dimacs = expr2dimacscnf(expr.to_cnf())

    ifd, ifname = mkstemp()

    with open(ifd, 'w') as f: f.write(to_qdimacs(props, dimacs, quants))
    proc = run(['depqbf', '--no-dynamic-nenofex', '--qdo', ifname], stderr=STDOUT, stdout=PIPE)
    remove(ifname)

    satisfiable, witness = sat(proc.stdout.decode('utf-8'))

    if not satisfiable and witness != {}:
        return [sum([2 ** i if witness[props[sv[i]]] else 0 for i in range(len(svs[0]))]) for sv in svs]
    else:
        return None

def sat(output):
    answer = None
    witness = {}
    for lno, ln in enumerate(output.strip().split('\n')):
        # Skip empty lines and comments.
        if len(ln) == 0 or ln[0] == 'c':
            continue

        ln = ln.split(' ')

        if len(ln) == 5 and ln[0] == 's' and ln[1] == 'cnf':
            answer = int(ln[2])

        if len(ln) > 1 and ln[0] == 'V':
            literal = int(ln[1])
            witness[abs(literal)] = literal > 0

    if answer not in {0, 1}:
        print('Indeterminate result!')
        exit(1)

    return bool(answer), witness

def main():
    with open(argv[len(argv) - 1], 'r') as f:
        s, t, tab = totab(*parse(f))

        if '--table' in argv:
            print('Truth Table of Transition Function (LSBs at 0):')
            print(tab)

        tab = truthtable2expr(tab)

        path = []
        for d in range(v):
            witness = solve(*diameter(d, tab, s, t))

            if witness:
                path = witness
            else:
                print(' '.join(map(lambda x: str(x + 1), path)) if '--path' in argv else len(path))
                exit(0)

        print('?')
        exit(2)

if __name__ == '__main__':
    main()
