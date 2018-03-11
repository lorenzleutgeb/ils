
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas.tseries as ts

setups = [
    (2, [20, 50, 100, 200, 500]),
    (3, [50, 100, 200]),
    (5, [50])
]

colors = ['orange', 'black','red', 'green',  'slategrey']
lighter = ['khaki', 'grey','salmon', 'yellowgreen',  'lightgrey']

for setup in setups:
    k, N = setup
    data = np.loadtxt('data-{}.dat'.format(k))
    f = plt.figure()

    df = {'x': data[:,0]}
    for i, n in enumerate(N):
        df['n={}'.format(n)] = data[:,1 + i * 3]

    df = pd.DataFrame(df)

    for i, n in enumerate(N):
        df['n={}'.format(n)] = data[:,1 + i * 3]
        plt.plot('x', 'n={}'.format(n), data=df, marker='o', markerfacecolor=colors[i], markersize=2, color=lighter[i], linewidth=1)

    plt.legend()
    plt.show()
    f.savefig('test-{}.pdf'.format(k))
