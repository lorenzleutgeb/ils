from functools import reduce
from sys       import stdin, stdout
from itertools import combinations

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
