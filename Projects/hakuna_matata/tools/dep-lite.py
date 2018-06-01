from sys import stdin, stdout
from functools import reduce
from itertools import product
from itertools import combinations

tab = '\t'

# Line feed.
lf = '\n'

cons = ':-'
wcons = ':~'

aggregates = {'#count', '#sum', '#times', '#min', '#max'}

tablen = 8

uninteresting = {
    'bad',
    'breezeHasPossiblePit',
    'pitHasBreeze',
    'doingSomething',
    'inSomeMode',
    'wouldBump',
    'foundGoal',
    '==',
    '!=',
    '>',
    '<',
    '>=',
    '<=',
    '#succ',
    '#int',
    '#prec',
    '#absdiff',
    '#const',
    '#maxint',
    '+',
    '-',
    '~'
}

basic = {
    'breeze',
    'explored',
    'glitter',
    'stench',
    'bumped',
    'grabbed',
    'shot',
    'grabbed',
    'now',
    'killed',
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


print('digraph G {\n\tcompound = true; splines = ortho; pad="0.5"; nodesep="1"; ranksep="2" ; \n')

print('\tnode [fontname="Monospace" shape="box" width=1.5];')
print('\tsubgraph cluster_0 {  fontname = "Monospace"; fontsize=18; margin = 50; style=filled; fillcolor="#228B2266"; color="#228B2299"')

for b in basic:
    print('\t\t"{}" [style="filled" color="white", fontcolor="forestgreen"]'.format(b))

print('\t}')

for b in output:
    print('\t\t"{}" [style="filled" color="#0000ffcc", fontcolor="white"]'.format(b))

print('\t"" [fillcolor="red" color="red" style="filled" width=0.5 height=0.5];'.format(b))

print('\tnode [color="black", fillcolor="#fafafa", style="filled"];')

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

def keepSpaces(s):
    def f(acc, x):
        if x == '' and acc != []:
            acc[-1] += ' '
        else:
            acc.append(x)
        return acc

    return reduce(f, s.split(' '), [])

def ingest(atom, dneg=False):
    ln = keepSpaces(atom.strip())
    xdneg = ln[0] == 'not' and dneg
    ln = ln[xdneg:]
    cneg = ln[0][0] == '-'
    result = (cneg, ln[0][cneg:], ln[1:])
    return (xdneg, *result) if dneg else result

def atomize(s):
    s = keepSpaces(s)
    dneg = s[0] == 'not'
    if len(s) - dneg == 1:
        return ('not ' if dneg else '') + s[dneg]
    return ('not ' if dneg else '') + s[dneg] + '(' + ','.join(s[dneg + 1:]) + ')'

def ignore(ln):
    return len(ln) < 2 or ln[0] != tab

def isBody(ln):
    return len(ln) > 0 and ln[0] == tab

def emit(w, skip, lno, head, body):
    disjunction = len(head) > 1
    weak = False
    for ha in head:
        hneg, hpred, _ = ha
        hpred = hpred.strip()

        if hpred in uninteresting:
            return

        w('\t\t"{}"\n'.format(hpred))

        weak = hpred == '~'
        if weak:
            hpred = ''

        collectedHeads.add(hpred)

        if hpred not in rules[weak][disjunction][hneg]:
            rules[weak][disjunction][hneg][hpred] = {}

        for ba in body:
            _, bdef, bneg, bpred, _ = ba
            bpred = bpred.strip()

            if bpred in uninteresting:
                continue

            collectedBodies.add(bpred)
            if bpred not in rules[weak][disjunction][hneg][hpred]:
                rules[weak][disjunction][hneg][hpred][bpred] = {
                    bdef: {bneg: [lno + 1], (not bneg): []},
                    (not bdef): {bneg: [], (not bneg): []},
                }

            rules[weak][disjunction][hneg][hpred][bpred][bdef][bneg].append(lno + 1)

w = stdout.write

head = []
body = []
skip = False
section = None
hlno = -1

for lno, ln in enumerate(stdin):
    bk = ln
    if ignore(ln):
        emit(w, skip, hlno, head, body)
        head, body = [], []

        if ln.startswith('## '):
            if section != None:
                w('\t}')
            section = ln[3:-1]

            w('\tsubgraph cluster{} {{\n\n\nlabel = "{}"; fontname = "Monospace"; fontsize=18; margin = 50; style=filled; fillcolor="#00000005"; color="grey" \n'.format(lno, section))

        continue

    # Strip first tab.
    ln = ln[1:]

    if isBody(ln):
        ln = ln[1:]

        indentation = 2
        while ln[0] == tab:
            indentation += 1
            ln = ln[1:]

        if indentation > 2:
            #print('Skipping for aggregate!')
            skip = True

        ln = ln.strip()

        # TODO: This breaks for quoted strings (there might be a space in a quoted string).
        #ln = list(filter(len, ln.split(' ')))
        body.append((indentation, *ingest(ln, True)))
    else:
        emit(w, skip, hlno, head, body)

        skip = False
        body = []

        ln = ln.strip()

        # TODO: This breaks for string literals g(there may be a pipe in  a string literal).
        ln = ln.split('|')

        if len(ln) > 1:
            skip = True

        head = list(map(ingest, ln))
        hlno = lno

w('}')

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
            color = '"#0000ff33"'
        elif disjunction:
            color = 'purple'
        else:
            color = 'forestgreen'

        style = 'style = dashed' if bdef else ''

        print('"{}" -> "{}" [{} xlabel="{}" arrowhead = "{}" color = "{}" fontname = "Monospace"];'.format(hpred, bpred, style, lnos, arrow, color))
    except:
        continue

print('}')
