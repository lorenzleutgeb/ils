import matplotlib.pyplot as plt
import numpy             as np

setups = [
    (2, [20, 50, 100, 200, 500]),
    (3, [50, 100, 200]),
    (5, [50])
]

colors = [
    ('red', 'tomato'),
    ('xkcd:blue', 'xkcd:azure'),
    ('orange', 'khaki'),
    ('green', 'yellowgreen'),
    ('purple', 'violet'),
]

for setup in setups:
    k, N = setup
    data = np.loadtxt('data-{}.dat'.format(k))

    xs = data[:,0]

    # Satisfiability plot:
    f = plt.figure()

    # Mark crossover.
    plt.axhline(0.5, color='black', linestyle='--', linewidth=1)

    for i, n in enumerate(N):
        plt.plot(xs, data[:,1 + i * 3], '-o', markerfacecolor=colors[i][1], markersize=3, color=colors[i][0], linewidth=2)

    plt.legend(N, title='$n$')
    f.savefig('satisfiablity-{}.pdf'.format(k))

    # Combined plots (decisions/time):
    f = plt.figure()
    ax1 = plt.axes()

    plt.title('Hardness\n($k = {}$, 100 experiments per dot)'.format(k))
    ax1.set_xlabel('$r = \\frac{l}{n}$')
    ax1.set_autoscaley_on(True)

    # By default, we have no second y-axis.
    ax2 = None

    if k in {3, 5}:
        # Switch to logarithmic scaling and set limits.
        ax1.set_yscale('log')

        # Add second y-axis for execution time.
        ax2 = ax1.twinx()
        ax2.set_yscale('log')
        ax2.set_autoscaley_on(True)

    for i, n in enumerate(N):
        ax1.plot(xs, data[:,3 + i * 3], '-o', markerfacecolor=colors[i][1], markersize=3, color=colors[i][0], linewidth=2)
        ax1.set_ylabel('Decisions [1]')

    for i, n in enumerate(N):
        if k == 2:
            continue

        ax2.plot(xs, data[:,2 + i * 3], '--o', markerfacecolor=colors[i][1], markersize=3, color=colors[i][0], linewidth=2)
        ax2.set_ylabel('Average Execution Time [s]')

    if ax2 != None:
        plt.gca().add_artist(ax2.legend(N, title='$n$'))

    ax1.legend(N, loc=(3 if k == 2 else 2), title='$n$')

    f.savefig('combined-{}.pdf'.format(k))
