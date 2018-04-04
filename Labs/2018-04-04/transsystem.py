from sys        import argv, exit
from sys         import stdin

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

        E.append((int(state[0]), int(state[2])))
        V = max([b for (a,b) in E])

    return (V,E)

def main():

    with open(argv[1], 'r') as f:
        print(parse(f))

if __name__ == '__main__':
    main()
