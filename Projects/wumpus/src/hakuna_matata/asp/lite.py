from functools import reduce
from sys       import stdin, stdout
from itertools import combinations

import networkx as nx
from networkx.algorithms.dag import lexicographical_topological_sort

tab = '\t'

# Line feed.
lf = '\n'

cons = ':-'
wcons = ':~'

aggregates = {'#count', '#sum', '#times', '#min', '#max'}

tablen = 8

def keepSpaces(s):
    def f(acc, x):
        if x == '' and acc != []:
            acc[-1] += ' '
        else:
            acc.append(x)
        return acc

    return reduce(f, s.split(' '), [])

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

def unlite(src, dst):
    with open(src, 'r') as srcf:
        with open(dst, 'w') as dstf:
            _unlite(srcf, dstf)

def _unlite(src, dst):
    w = dst.write

    def unindent(previously, now):
        if previously == now and now == 0:
            return

        if previously < now:
            return

        if previously == now and now == 1:
            w('.' + lf)
            return

        final = now <= 1
        w('}' * (previously - now - final - 1) + ('.' if final else '') + lf)

    # Indicates that we are currently reading bodies.
    bodyMode = False
    prevIndentation = 0

    for ln in src:
        # If the first line is not a tab, or the line is empty, just pass it on.
        if ignore(ln):
            indentation = 0
            # if prevIndentation > indentation and prevIndentation > 2:
            #     w('}' * (prevIndentation - indentation))
            # prevIndentation = indentation
            # if bodyMode:
            #     w('.' + lf)
            unindent(prevIndentation, indentation)
            prevIndentation = indentation
            w('%' + ln)
            bodyMode = False
            continue

        if '"' in ln or "'" in ln:
            raise ValueError('String literals are not supported yet.')

        # Strip away the first tab.
        ln = ln[1:]
        readBody = isBody(ln)

        # We recognized a body, now strip away the next tab.
        if readBody:
            ln = ln[1:]

        if not readBody:
            ln = ln.lstrip()

            # Preprocessor rules (constants).
            if ln[0] == '#':
                w(ln)
                continue

            # Since we are in head mode we can strip away (no need to read any further indentation).
            ln = ln.lstrip()

            # We were in body mode, so terminate the previous body.
            # if bodyMode:
            #     w('.')
            unindent(prevIndentation, 1)
            prevIndentation = 1
            bodyMode = False

            # Check for a hard constraint.
            if len(ln) == 2 and ln[0] == cons[1]:
                w(cons + lf)
                continue

            # Check for a weak constraint.
            if len(ln) == 2 and ln[0] == wcons[1]:
                w(wcons + lf)
                continue

            # TODO: This breaks for string literals (there may be a pipe in  a string literal).
            ln = ln.split('|')

            # Special case: Facts over fixed integer ranges.
            # TODO: This breaks for string literals (there might be two dots inside a string literal).
            if len(ln) == 1 and '..' in ln[0]:
                w(atomize(ln[0].strip()) + '.' + lf)
                # Since this fact auto-terminates, we fake prevIndentation.
                prevIndentation = 0
                continue

            w(tab + ' v '.join(map(lambda x: atomize(x.strip()), ln)) + ' ' + cons + ' ')
            continue

        # We are treating bodies from here on.
        if not bodyMode:
            w(lf)

        indentation = 2
        while ln[0] == tab:
            indentation += 1
            ln = ln[1:]

        # Strip away trailing newline and other stuff...
        ln = ln.strip()

        isAggregate = False
        for aggregate in aggregates:
            if ln.startswith(aggregate):
                isAggregate = True

        # We first handle the easier case of non-aggregates.
        if not isAggregate:
            unindent(prevIndentation, indentation)

            if bodyMode and prevIndentation >= indentation:
                w(',')

            w(tab * indentation + atomize(ln))
            prevIndentation = indentation
            bodyMode = True
            continue

        ln = keepSpaces(ln)
        if bodyMode:
            w(lf + ',')

        w(tab * indentation + ln[1] + ' = ' + ln[0] + '{' + (','.join(ln[2:]) if len(ln) > 3 else ln[2]) + ': ' + lf)
        bodyMode = True

    if bodyMode:
        w('.')

def uniq(xs):
    prio = {}
    res = []
    for x in xs:
        if x not in prio:
            res.append(x)
            prio[x] = len(res) + 1
    return (res, prio)

def flatten(xs):
    return reduce(lambda x, y: x + [y] if type(y) != list else x + y, xs, [])

def project(i, xs):
    return list(map(lambda x: x[i], xs))

def bare(xs):
    return list(map(lambda x: x.strip(), xs))

def plain(w, head, body):
    if head != []:
        w(tab + ' | '.join([('-' if cneg else '') + pred + ('' if terms == [] else ' ' + ' '.join(terms)) for (cneg, pred, terms) in head]) + lf)
    if body != []:
        w(lf.join([
                tab * indent +
                ('not ' if dneg else '') +
                ('-' if cneg else '') +
                predicate +
                ('' if terms == [] else ' ' + ' '.join(terms))
            for (indent, dneg, cneg, predicate, terms) in body
        ]))

def emit(w, skip, head, body):
    if not(not skip and len(body) > 1):
        plain(w, head, body)
        return

    mkDneg = ' ' * len('not ') if not skip and any(project(1, body)) else ''
    mkCneg = ' ' * len('-') if not skip and any(project(2, body)) else ''
    body = list(map(lambda x: (x[0], x[1], x[2], x[3].strip(), bare(x[4])), body))
    offset = max(map(len, project(3, body)))

    g = nx.DiGraph()

    prio = []
    head = list(head)
    if head != []:
        lastHead = head[-1]
        prio = [bare(lastHead[2])]
        offset = max(offset, len(lastHead[1]) - tablen)
        g.add_edges_from(zip(lastHead[2], lastHead[2][1:]))

    # Establish some order for incomparable sets.
    lex, prio = uniq(flatten(prio + list(sorted(map(bare, project(4, body)), key=len, reverse=True))))

    for _, _, _, _, terms in body:
        if len(terms) == 1:
            g.add_node(terms[0])
        else:
            g.add_edges_from(zip(terms, terms[1:]))

    def foo(x):
        if not x in prio:
            return None
        return prio[x]

    if len(lex) > 1:
        try:
            lex = list(lexicographical_topological_sort(g))#, key=prio.get))
        except nx.exception.NetworkXUnfeasible:
            # we're fine with that...
            print('DANGER')
            ''

    print(tab + tab + ' ' + ' ' * offset + ' '.join(lex))

    g = nx.DiGraph()

    # Generate nodes for all sets of variables.
    for atom in body:
        bareVars = map(lambda y: y.strip(), atom[4])
        ts = list(set(list(bareVars)[:]))
        # Attention, we destroy the order of the terms here!
        ts.sort()
        ts = tuple(ts)
        if ts in g:
            g.node[ts]['atoms'].append(atom)
        else:
            g.add_node(ts, atoms=[atom])

    for u, v in combinations(g, 2):
        # If u is a superset of v, then u should come earlier in the topo.
        if set(v).issubset(set(u)):
            g.add_edge(u, v)

    if head != []:
        w(tab + ' | '.join([('-' if cneg else '') + pred + ('' if terms == [] else ' ' + ' '.join(terms)) for (cneg, pred, terms) in head]) + lf)

    atoms = nx.get_node_attributes(g, 'atoms')
    for v in lexicographical_topological_sort(g, key=lambda x: lex.index(x[0]) if len(x) > 0 else 0):
        for (indent, dneg, cneg, predicate, terms) in atoms[v]:
            w(
                tab * indent +
                ('not ' if dneg else mkDneg) +
                ('-' if cneg else mkCneg) +
                predicate.ljust(offset,' ') +
                ('' if terms == [] else ' ' + ' '.join(terms)) +
                lf
            )

def ingest(atom, dneg=False):
    ln = keepSpaces(atom.strip())
    xdneg = ln[0] == 'not' and dneg
    ln = ln[xdneg:]
    cneg = ln[0][0] == '-'
    result = (cneg, ln[0][cneg:], ln[1:])
    return (xdneg, *result) if dneg else result

def _format(src, dst):
    w = dst.write

    head = []
    body = []
    skip = False

    for ln in src:
        bk = ln
        if ignore(ln):
            emit(w, skip, head, body)
            if body != []:
                w(lf)

            head, body = [], []

            w(ln)
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
            emit(w, skip, head, body)

            skip = False
            body = []

            ln = ln.strip()

            # TODO: This breaks for string literals g(there may be a pipe in  a string literal).
            ln = ln.split('|')

            if len(ln) > 1:
                skip = True

            head = map(ingest, ln)

if __name__ == '__main__':
    _format(stdin, stdout)
