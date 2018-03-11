
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas.tseries as ts
from matplotlib.ticker import NullFormatter

setups = [
    (2, [20, 50, 100, 200, 500]),
    (3, [50, 100, 200]),
    (5, [50])
]

colors = ['orange', 'dimgray','red', 'green',  'slategrey']
lighter = ['khaki', 'grey','salmon', 'yellowgreen',  'lightgrey']
decisionColors =['darkgoldenrod', 'black', 'darkred', 'darkolivegreen', 'lightslategray']


for setup in setups:
    k, N = setup
    data = np.loadtxt('data-{}.dat'.format(k))
    f = plt.figure()

#    df = {'x': data[:,0]}
#    for i, n in enumerate(N):
#        df['n={}'.format(n)] = data[:,1 + i * 3]

#    df = pd.DataFrame(df)

#    for i, n in enumerate(N):
#        plt.plot('x', 'n={}'.format(n), data=df, marker='o', markerfacecolor=colors[i], markersize=2, color=lighter[i], linewidth=1)
#        plt.axhline(0.5, color='skyblue', linestyle='dashed', linewidth=1)

#time plots
    f1 = plt.figure()
    ax1 = f1.add_subplot(111)
    dftime = {'x': data[:,0]}
    for i, n in enumerate(N):
      dftime['n={}'.format(n)] = data[:,2 + i * 3]

    dftime = pd.DataFrame(dftime)

    for i, n in enumerate(N):
        ax1.plot('x', 'n={}'.format(n), data=dftime, marker='o', markerfacecolor=colors[i], markersize=2, color=lighter[i], linewidth=1)
        ax1.set_ylabel('time')
        plt.yscale('log')
        plt.ylim(ymax = 1)
        plt.ylim(ymin = -10)
        plt.legend()

#decision plots
    f2 = plt.figure()
    ax2 = ax1.twinx()
    dfD = {'x': data[:,0]}
    for i, n in enumerate(N):
       dfD['n={}'.format(n)] = data[:,3 + i * 3]

    dfD = pd.DataFrame(dfD)

    for i, n in enumerate(N):
        ax2.plot('x', 'n={}'.format(n), data=dfD, marker='o', markerfacecolor=decisionColors[i], markersize=5, color=lighter[i], linewidth=5)
        ax2.set_ylabel('decision')
        plt.yscale('log')

    if k == 5:
        plt.ylim(ymax = 1000000)
        plt.ylim(ymin = 0)
    else:
        plt.yscale('log')
        plt.ylim(ymax = 100000)
        plt.ylim(ymin = 0)

    #plt.legend()
    #plt.show()
    f.savefig('satisfiablity-{}.pdf'.format(k))
    #f1.savefig('time-{}.pdf'.format(k))
    #f2.savefig('decision-{}.pdf'.format(k))
    f1.savefig('combined-{}.pdf'.format(k))
