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
    plt.title('Satisfiability\n($k = {}$, 100 experiments per dot)'.format(k))
    plt.axes().set_xlabel('$r = \\frac{l}{n}$')

    [plt.plot(
        xs, data[:,1 + i * 3], '-o', markerfacecolor=colors[i][1], markersize=3, color=colors[i][0], linewidth=2
    ) for i in range(len(N))]

    plt.legend(N, title='$n$')

    # Mark crossover.
    plt.axhline(0.5, color='black', linestyle='--', linewidth=1)

    f.savefig('satisfiability-{}.pdf'.format(k))

    # Combined plots (decisions/time):
    f = plt.figure()
    plt.title('Hardness\n($k = {}$, 100 experiments per dot)'.format(k))
    ax1 = plt.axes()
    ax1.set_xlabel('$r = \\frac{l}{n}$')
    ax1.set_autoscaley_on(True)
    ax1.set_ylabel('Decisions [1]')

    if k in {3, 5}:
        # Switch to logarithmic scaling and set limits.
        ax1.set_yscale('log')

        # Add second y-axis for execution time.
        ax2 = ax1.twinx()
        ax2.set_ylabel('Average Execution Time [s]')
        ax2.set_yscale('log')
        ax2.set_autoscaley_on(True)

        [ax2.plot(
            xs, data[:,2 + i * 3], '--o', markerfacecolor=colors[i][1], markersize=3, color=colors[i][0], linewidth=2
        ) for i in range(len(N))]

        plt.gca().add_artist(ax2.legend(N, title='$n$'))

    [ax1.plot(
        xs, data[:,3 + i * 3], '-o', markerfacecolor=colors[i][1], markersize=3, color=colors[i][0], linewidth=2
    ) for i in range(len(N))]

    ax1.legend(N, loc=(3 if k == 2 else 2), title='$n$')

    f.savefig('combined-{}.pdf'.format(k))
