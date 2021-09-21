import pandas as pd
import argparse
import seaborn as sns
import matplotlib.pyplot as plt
import itertools


def shorten_uri(class_uri, base="http://dbpedia.org/ontology/", pref="dbo:"):
    return class_uri.replace(base, pref)


def get_classes(fpath):
    d = dict()
    f = open(fpath)
    for line in f.readlines():
        sline = line.strip()
        if sline == "":
            continue
        fname, _, class_uri = sline.split(',')
        fname = fname.replace('"', '')
        fname += ".csv"
        class_uri = class_uri.replace('"', "")
        d[fname] = class_uri
    return d


def analyse_alpha_for_all(falpha, classes, draw_fname, midalpha):
    """
    :param fmeta: path to the meta file
    :param classes: a dict of fnames and their classes

    :return:
    """
    df_all = pd.read_csv(falpha)
    for fsid in range(1, 6):
        df = df_all[df_all.fsid == fsid]
        al_per_cls = aggregate_alpha_per_class(df, classes)

        analyse_alpha(al_per_cls, draw_fname+"_fsid%d" % (fsid), midalpha)
        # analyse_alpha(al_per_cls, "wcv2_alpha_%s_original_fsid%d" % (fattr,fsid))
        # analyse_alpha(al_per_cls, "wcv2_alpha_fsid%d" % fsid)

        # break


def analyse_alpha(alpha_per_class, draw_fname, midalpha):
    rows = []
    if midalpha:
        attrs = ['mid_alpha']
    else:
        attrs = ['from_alpha', 'to_alpha']
    # attrs = ['from_alpha', 'to_alpha', 'mid_alpha']
    # attrs = ['mid_alpha']
    for c in alpha_per_class:
        for a_attr in attrs:
            for a in alpha_per_class[c][a_attr]:
                if a < 0:
                    continue
                r = [shorten_uri(c), a, a_attr]
                rows.append(r)
                print(r)
    # print(rows)
    data = pd.DataFrame(rows, columns=["Class", "Alpha", "Attr"])
    ax = sns.boxplot(x="Class", y="Alpha",
                     hue="Attr",
                     data=data, linewidth=1.0,
                     # palette="colorblind",
                     palette="Spectral",
                     # palette="pastel",
                     dodge=True,
                     # palette="ch:start=.2,rot=-.3",
                     orient="v",
                     flierprops=dict(markerfacecolor='0.50', markersize=2), whiskerprops={'linestyle': '-'})
    if midalpha:
        # to remove legend
        ax.legend_.remove()
        ax.set_ylim(0, 0.7)
    # ticks = ax.get_xticks()
    # new_ticks = [t-1 for t in ticks]
    # texts = ax.get_xticklabels()
    # print(ax.get_xticklabels())
    # labels = [t.get_text() for t in texts]
    # ax.set_xticks(new_ticks)
    # ax.set_xticklabels(labels)
    # print(ax.get_xticklabels())
    # for i, box in enumerate(ax.artists):
    #     box.set_edgecolor('black')
    # To change bar colors
    # plt.setp(ax.artists, edgecolor='k', facecolor='w')
    # To make whiskers black
    plt.setp(ax.lines, color='k')
    [t.set_rotation(80) for t in ax.get_xticklabels()]
    #plt.show()
    ax.figure.savefig('docs/%s.svg' % draw_fname)
    ax.figure.clf()


def aggregate_alpha_per_class(df, classes):
    """
    :param df: DataFrame of a meta file
    :param calsses: a dict of fnames and their classes
    :return:
    """
    """fname,colid,fsid,from_alpha,to_alpha"""
    d = dict()
    for idx, row in df.iterrows():
        # print("fname: <%s>" % row['fname'])
        # print("classes: ")
        # print(classes)
        c = classes[row['fname']]
        if c not in d:
            d[c] = {'from_alpha': [], 'to_alpha': [], 'mid_alpha': []}
        d[c]['from_alpha'].append(row['from_alpha'])
        d[c]['to_alpha'].append(row['to_alpha'])
        d[c]['mid_alpha'].append((row['from_alpha'] + row['to_alpha'])/2)
    return d


def workflow(falpha, fmeta, draw_fpath, midalpha):
    classes = get_classes(fmeta)
    analyse_alpha_for_all(falpha, classes, draw_fpath, midalpha)


def main():
    """
    Parse the arguments
    :return:
    """
    parser = argparse.ArgumentParser(description='Alpha Analysis')
    # parser.add_argument('--debug', action="store_true", default=False, help="Whether to enable debug messages.")
    parser.add_argument('falpha', help="The path to the alpha results file.")
    parser.add_argument('fmeta', help="The path to the meta file which contain the classes.")
    parser.add_argument('--draw', default="test.svg", help="The filename prefix to draw (without the extension)")
    parser.add_argument('--midalpha', action="store_true", default=False,
                        help="Whether to report the mid ranges of the optimal alpha or just the ranges")
    parser.print_usage()
    parser.print_help()
    args = parser.parse_args()
    workflow(args.falpha, args.fmeta, args.draw, args.midalpha)


if __name__ == "__main__":
    main()
