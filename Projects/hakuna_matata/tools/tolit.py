from sys import stdin

for lno, ln in enumerate(stdin):
    if ln.strip() == '':
        print()
        continue

    if ln.startswith('%'):
        ln = ln[1:-1]
        ln = ln.lstrip()

        x = ln.replace(' ', '')
        t = all(map(lambda x: x == x.upper(), x))
        if t:
            ln = '## ' + ln.title()

        print(ln)
    else:
        print('    ' + ln[:-1])
