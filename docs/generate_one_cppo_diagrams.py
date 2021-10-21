import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import sys


sns.set_style("whitegrid")


def generate_diagram(data, draw_file_base):
        ax = sns.barplot(x="Accuracy", y="fsid",
                         hue="Method",
                         data=data, linewidth=1.0,
                         palette="Paired",
                         orient="h")
        # ax.legend_.remove()
        # ax.legend(bbox_to_anchor=(1.01, 1), borderaxespad=0)
        ax.legend(bbox_to_anchor=(1.0, -0.1), borderaxespad=0)
        # ax.set_xlim(0, 1.0)
        # ax.set_ylim(0, 0.7)
        # Horizontal
        ticks = ax.get_yticks()
        new_ticks = [t for t in ticks]
        texts = ax.get_yticklabels()
        # print(ax.get_yticklabels())
        labels = [t.get_text() for t in texts]
        ax.set_yticks(new_ticks)
        ax.set_yticklabels(labels, fontsize=8)
        # print(ax.get_yticklabels())
        draw_fname = draw_file_base  # draw_file_base+"_fsid%d" % (fsid)
        plt.setp(ax.lines, color='k')
        ax.figure.savefig('docs/%s.svg' % draw_fname, bbox_inches="tight")
        ax.figure.clf()


def parse_file(fpath):
    df = pd.read_csv(fpath)
    rows = []
    for idx, row in df.iterrows():
        r = [row['fsid'], row['One Alpha'], 'One Alpha']
        rows.append(r)
        r = [row['fsid'], row['CPPO (max)'], 'CPPO (max)']
        rows.append(r)
        r = [row['fsid'], row['CPPO (min)'], 'CPPO (min)']
        rows.append(r)
    df_new = pd.DataFrame(rows, columns=['fsid', 'Accuracy', 'Method'])
    return df_new


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Expects the results csv file and the basename of the diagram")
    data = parse_file(sys.argv[1])
    generate_diagram(data, sys.argv[2])

