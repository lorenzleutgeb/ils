from math import ceil, sqrt

from .location import Location

right = ('╟')
up = ('╔', '╤')

# painters should be a list of tuples:
# (filter, t, f)
def paint(n, painters, fname, notes=[]):
    image = []
    height, width = 3, 6
    image.append('    ╔' + '╤'.join(['═' * width for z in range(n)]) + '╗')
    for y in list(range(1, n + 1))[::-1]:
        for i in range(height):
            ln = '  '
            if i == int(height / 2):
                ln += (str(y))
            else:
                ln += (' ')
            ln += (' ║')
            for x in range(1, n + 1):
                l = Location(x, y)
                for j in range(width):
                    idx = i * width + j
                    yp, np = None, None
                    if len(painters) <= idx:
                        ln += (' ')
                        continue
                    if len(painters[idx]) == 3:
                        p, yp, np = painters[idx]
                    elif len(painters[idx]) == 2:
                        p, yp = painters[idx]
                        np = ' '
                    elif len(painters[idx]) == 1:
                        p = painters[idx][0]
                        np = ' '
                    else:
                        raise ValueError('x')

                    if type(p) == dict:
                        if l in p:
                            p = False
                        elif (l,) in p:
                            p = p[(l,)]
                        else:
                            p = False
                    elif type(p) == list:
                        if l in p:
                            p = True
                        else:
                            p = False
                    elif type(p) == Location:
                        p = l == p
                        #p = False
                    elif callable(p):
                        p = p(l)
                        if p == None:
                            p = False
                        elif type(p) == bool:
                            if yp == None:
                                yp = str(p)
                        else:
                            yp = str(p)
                            p = True
                    else:
                        raise ValueError('Unknown painter!')

                    ln += (yp if p else np)
                    p = False
                if x < n:
                    ln += ('│')
                else:
                    ln += ('║')
            image.append(ln)
        if y > 1:
           image.append('    ╟' + '┼'.join(['─' * width for z in range(n)]) + '╢')

    image.append('    ╚' + '╧'.join(['═' * width for z in range(n)]) + '╝')
    image.append('     ' + ' '.join([str(z + 1).ljust(int(width - 1 / 2)).rjust(width) for z in range(n)]))

    imw = max(map(len, image))

    while len(notes) > len(image) - 2:
        image = ['    ' + ' ' * 30 + notes.pop(0)] + image

    for i, note in enumerate(notes):
        image[-(i + 2)] += '    ' + ' ' * (max(0, 30 - imw)) + note

    with open(fname, 'w') as f:
        f.write('\n' * 20)
        f.write('\n'.join(image))
        f.write('\n' * 3)
