from collections import Counter
import pandas as pd
import pprint
import numpy as np

import matplotlib.cm
cmap = matplotlib.cm.jet
cmap = matplotlib.cm.viridis
#cmap = matplotlib.cm.plasma
#cmap = matplotlib.cm.inferno
# cmap = matplotlib.cm.magma
# cmap = matplotlib.cm.GnBu
# cmap = matplotlib.cm.winter
# cmap = matplotlib.cm.hot


def alpha_stat(ks, alphas_fname):
    df = pd.read_csv(alphas_fname, sep='\t')
    # print df.columns.values
    d = dict()
    for k in ks:
        df_k = df[df.k==k]
        d_count = dict(Counter(df_k['alpha']))
        d[k] = d_count
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(d)
    print d
    plot_alpha_stat(d)


def plot_alpha_stat(d):
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt

    ind = np.arange(len(d[d.keys()[-1]]))  # the x locations for the groups
    width = 0.20  # the width of the bars
    fig, ax = plt.subplots()

    # custom_colors = [ 'royalblue', 'mediumpurple', 'mediumvioletred','hotpink' ,'greenyellow', 'dodgerblue', 'aquamarine' ,'deeppink', 'darkturquoise', 'skyblue']

    for idx, k in enumerate(sorted(d.keys())):
        vals = []
        for a in sorted(d[k].keys()):
            vals.append(d[k][a])

        _ = ax.bar(ind + width * idx - width/2, vals, width,
                   color=cmap(idx*1.0/len(d.keys())),
                   #color=custom_colors[idx],
                   label="k="+str(k))

    ax.set_ylabel('Count')
    ax.set_title('Alphas for each k')
    ax.set_xticks(ind)
    ax.set_xticklabels(tuple(sorted(d[d.keys()[-1]].keys())))
    ax.legend()
    plt.show()