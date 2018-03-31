# Team White

from itertools   import permutations, product
from pyeda.inter import expr2bdd, exprvar, exprvars, And, Equal, Not, Nor, Or
from subprocess  import Popen, PIPE
from sys         import exit

def size(bdd):
    return len(list(bdd.bfs()))

def render(o, name, format='svg'):
    with open(name + '.' + format, 'w+') as f:
        dot = Popen(['dot', '-T' + format], stdin=PIPE, stdout=f, stderr=PIPE)
        stdoutdata, stderrdata = dot.communicate(o.to_dot(name).encode('utf-8'))
        status = dot.wait()

        if status != 0:
            print(stderrdata.decode('utf-8'))
            exit(status)

# Generate the variables we need for 4a as
# a list and extract bindings.
vs = list(map(
    exprvar,
    map(
        lambda x: '{0:s}{1:d}'.format(*x),
        product(
            ['a', 'b'],
            [1, 2, 3]
        )
    )
))

a1, a2, a3, b1, b2, b3 = vs

f4a = And(
    Equal(a1, b1),
    Equal(a2, b2),
    Equal(a3, b3)
)

bdd = expr2bdd(f4a)
render(bdd, 'f4a')

# Generate an independent list of variables
# of the form v0, v1, ..., vn where n + 1 is the
# number of variables in vs.
other = exprvars('v', len(vs))

best = (size(bdd), bdd, {})
for p in permutations(list(other)):
    rbdd = expr2bdd(f4a.compose(dict(zip(vs, p))))
    rsize = size(rbdd)

    if rsize < best[0]:
        best = (rsize, rbdd, p)

render(best[1], 'f4a_reordered')
print('Best variable ordering for 4a:', list(map(lambda x: vs[x.indices[0]], best[2])))

# For 4b and 4c we need four variables.
a, b, c, d = map(exprvar, ['a', 'b', 'c', 'd'])

f4b = And(
    Or(
        And(a, b),
        Nor(a, b)
    ),
    Or(
        And(c, d),
        Nor(c, d)
    )
)

render(expr2bdd(f4b), 'f4b')

f4c = Or(
    Or(
        Or(
            Or(
                And(
                    And(
                        And(
                            a,
                            d
                        ),
                        c
                    ),
                    b
                ),
                And(
                    And(
                        And(
                            c,
                            d
                        ),
                        Not(
                            a
                        )
                    ),
                    Not(
                        b
                    )
                )
            )
        ),
        And(
            And(
                And(
                    a,
                    b
                ),
                Not(
                    c
                )
            ),
            d
        )
    ),
    And(
        And(
            And(
                Not(
                    c
                ),
                Not(
                    a
                )
            ),
            Not(
                b
            )
        ),
        d
    )
)

render(expr2bdd(f4c), 'f4c')

print('f4a {} f4b'.format('===' if f4a.equivalent(f4b) else '!=='))

# For 5 we are looking at a digraph.
vs = range(1, 8)
es = [
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5),
    (2, 3),
    (2, 4),
    (2, 6),
    (3, 4),
    (4, 5),
    (4, 6),
    (4, 7),
    (5, 7),
]
