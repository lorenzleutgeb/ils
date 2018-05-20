from sys import stdin
from functools import reduce
from itertools import product

uninteresting = {
    'bad',
    'breezeHasPossiblePit',
    'pitHasBreeze',
    'doingSomething',
    'inSomeMode',
    'wouldBump',
    'foundGoal'
}

basic = {
    'breeze',
    'explored',
    'glitter',
    'stench',
    'pathCost',
    'bump',
    'grabbed',
    'wumpusDead',
    'towards',
    'shot',
    'haveArrow',
    'grabbed'
}

output = {
    'do',
    'goal',
    'safe',
    'autopilot'
}

def stripall(xs):
    return list(map(lambda x: x.strip("."), xs))

def flatten(xs):
    return reduce(lambda x, y: x + [y] if type(y) != list else y + x, xs, [])

def compress(acc, x):
    if acc == []:
        return [(x, x)]

    lmin, lmax = acc[-1]

    if x == lmax:
        return acc
    if x == lmax + 1:
        return acc[:-1] + [(lmin, x)]
    else:
        return acc + [(x, x)]

def human(x):
    lmin, lmax = x
    if lmin == lmax:
        return str(lmin)
    else:
        return '{} - {}'.format(lmin, lmax)


print('digraph G {\n')

print('node [fontname="Monospace" shape="box" width=1.5];')

for b in basic:
    print('"{}" [style="filled" color="forestgreen", fontcolor="white"]'.format(b))

for b in output:
    print('"{}" [style="filled" color="blue", fontcolor="white"]'.format(b))

print('"" [fillcolor="red" color="red" style="filled" width=0.5 height=0.5];'.format(b))

print('node [color="black", fillcolor="#fafafa", style="filled"];')

rules = {
    True: {
        True: {
            True: {},
            False: {},
        },
        False: {
            True: {},
            False: {},
        },
    },
    False: {
        True: {
            True: {},
            False: {},
        },
        False: {
            True: {},
            False: {},
        },
    },
}

collectedHeads = set()
collectedBodies = set()

for lno, ln in enumerate(stdin):
    ln = ln.strip()

    if ln.startswith('#'):
        continue
    if ln.startswith('%'):
        continue

    comment = ln.find('%')

    if comment >= 0:
        ln = ln[:comment]

    if len(ln) == 0:
        continue

    weak = False

    weight, level = None, None
    if ':~' in ln:
        weak = True
        lsqp, rsqp = ln.find('['), ln.find(']')
        if lsqp >= 0 and rsqp > lsqp:
            wdef = ln[lsqp:rsqp]
            #print(wdef)

    ln = ln.replace(':~', ':-')
    hasHead = ':-' in ln
    ln = ln.strip()
    parts = ln.split(':-')

    head, body = '', ''

    if len(parts) == 1:
        body = parts[0]
    elif len(parts) == 2:
        head, body = parts
    else:
        raise ValueError('Strange rule.')

    head = head.strip()
    body = body.strip()

    if body.endswith(').'):
        body = body[:-2]

    bodyAtoms = body.split('), ')
    bodyAtoms = stripall(bodyAtoms)

    for i, ba in enumerate(bodyAtoms):
        lpar = ba.find('(')
        if lpar >= 0:
            bodyAtoms[i] = ba[:lpar]

    bodyAtoms = list(map(lambda x: x.split(','), bodyAtoms))
    bodyAtoms = flatten(bodyAtoms)
    bodyAtoms = stripall(bodyAtoms)

    for i, ba in enumerate(bodyAtoms):
        for builtin in {'#int', '=', '!=', '<', '>', '#count', '#min'}:
            if builtin in ba:
                bodyAtoms[i] = None
                break
        if bodyAtoms[i] == None:
            continue
        ba = ba.strip()
        defNeg = ba.startswith('not ')
        neg = ba[defNeg*4:].startswith('-')
        predicate = ba[defNeg*4+neg:]
        bodyAtoms[i] = (defNeg, neg, predicate.strip())

    bodyAtoms = list(filter(lambda x: x != None, bodyAtoms))

    for ba in bodyAtoms:
        collectedBodies.add(ba[2])

    if not hasHead:
        headAtoms = []
    else:
        headAtoms = head.split('v')
        headAtoms = stripall(headAtoms)

    disjunction = len(headAtoms) > 1

    for i, ha in enumerate(headAtoms):
        lpar = ha.find('(')
        if lpar >= 0:
            ha = ha[:lpar]
        ha = ha.strip()
        neg = ha.startswith('-')
        predicate = ha[neg:]
        headAtoms[i] = (neg, predicate.strip())
        collectedHeads.add(headAtoms[i][1])

    for ha in headAtoms:
        hneg, hpred = ha

        if hpred not in rules[weak][disjunction][hneg]:
            rules[weak][disjunction][hneg][hpred] = {}

        for ba in bodyAtoms:
            bdef, bneg, bpred = ba
            if bpred not in rules[weak][disjunction][hneg][hpred]:
                rules[weak][disjunction][hneg][hpred][bpred] = {
                    bdef: {bneg: [lno + 1], (not bneg): []},
                    (not bdef): {bneg: [], (not bneg): []},
                }

            rules[weak][disjunction][hneg][hpred][bpred][bdef][bneg].append(lno + 1)

bs = [True, False]

for weak, disjunction, hneg, hpred, bpred, bdef, bneg in product(bs, bs, bs, collectedHeads, collectedBodies, bs, bs):
    if hpred in uninteresting or bpred in uninteresting:
        continue

    try:
        lnos = rules[weak][disjunction][hneg][hpred][bpred][bdef][bneg]

        if lnos == []:
            continue

        lnos.sort()

        lnos = ', '.join(map(human, reduce(compress, lnos, [])))

        arrow = 'invodot' if hneg else 'inv'

        if bneg:
            color = 'red'
        elif weak:
            color = 'blue'
        elif disjunction:
            color = 'purple'
        else:
            color = 'forestgreen'

        style = 'style = dashed' if bdef else ''

        print('"{}" -> "{}" [{} label="{}" arrowhead = "{}" color = "{}"];'.format(hpred, bpred, style, lnos, arrow, color))
    except:
        continue

print('}')
