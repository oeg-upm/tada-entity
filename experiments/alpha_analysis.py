import pandas as pd
import argparse
import seaborn as sns
import matplotlib.pyplot as plt


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


def analyse_alpha_for_all(falpha, classes):
    """
    :param fmeta: path to the meta file
    :param classes: a dict of fnames and their classes
    :return:
    """
    df_all = pd.read_csv(falpha)
    for fsid in range(1, 6):
        df = df_all[df_all.fsid == fsid]
        al_per_cls = aggregate_alpha_per_class(df, classes)
        analyse_alpha(al_per_cls, "test-alpha.svg")
        break


def analyse_alpha(alpha_per_class, draw_fname):
    rows = []
    for c in alpha_per_class:
        for a_attr in ['from_alpha', 'to_alpha']:
            for a in alpha_per_class[c][a_attr]:
                if a < 0:
                    continue
                r = [shorten_uri(c), a, a_attr]
                rows.append(r)
                print(r)
    # print(rows)
    data = pd.DataFrame(rows, columns=["Class", "Alpha", "Attr"])
    ax = sns.boxplot(x="Class", y="Alpha", hue="Attr", data=data, palette="pastel", orient="v")

    ticks = ax.get_xticks()
    new_ticks = [t for t in ticks]
    texts = ax.get_xticklabels()
    print(ax.get_xticklabels())
    labels = [t.get_text() for t in texts]
    ax.set_xticks(new_ticks)
    ax.set_xticklabels(labels)
    print(ax.get_xticklabels())
    [t.set_rotation(60) for t in ax.get_xticklabels()]

    # ax = sns.boxplot(y="Class", x="Alpha", hue="Attr", data=data, palette="pastel", width=2,  orient="h")
    # ticks = ax.get_yticks()
    # new_ticks = [t*2 + 1 for t in ticks]
    # texts = ax.get_yticklabels()
    # print(ax.get_yticklabels())
    # labels = [t.get_text() for t in texts]
    # ax.set_yticks(new_ticks[:3])
    # ax.set_yticklabels(labels[:3])
    # print(ax.get_yticklabels())
    # [t.set_rotation(30) for t in ax.get_yticklabels()]
    plt.show()


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
            d[c] = {'from_alpha': [], 'to_alpha': []}
        d[c]['from_alpha'].append(row['from_alpha'])
        d[c]['to_alpha'].append(row['to_alpha'])
    return d


def workflow(falpha, fmeta):
    classes = get_classes(fmeta)
    analyse_alpha_for_all(falpha, classes)


def main():
    """
    Parse the arguments
    :return:
    """
    parser = argparse.ArgumentParser(description='Alpha Analysis')
    # parser.add_argument('--debug', action="store_true", default=False, help="Whether to enable debug messages.")
    parser.add_argument('falpha', help="The path to the alpha results file.")
    parser.add_argument('fmeta', help="The path to the meta file which contain the classes.")

    parser.print_usage()
    parser.print_help()
    args = parser.parse_args()
    workflow(args.falpha, args.fmeta)


if __name__ == "__main__":
    main()
