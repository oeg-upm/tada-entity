import argparse
import seaborn as sns
import pandas as pd
import numpy as np
from experiments.alpha_analysis import shorten_uri
from collections import Counter
import matplotlib.pyplot as plt


def compute_class_alpha_accuracy(df_alpha, alphas):
    scores_mean = []
    scores_median = []
    # print("alphas: ")
    # print(alphas)
    for idx, row in df_alpha.iterrows():
        # print("[%.4f - %.4f]" % (row['from_alpha'], row['to_alpha']))
        is_corr = row['from_alpha'] <= alphas['mean'] <= row['to_alpha']
        scores_mean.append(is_corr)
        is_corr = row['from_alpha'] <= alphas['median'] <= row['to_alpha']
        scores_median.append(is_corr)
    acc = {
        'mean': 0,
        'median': 0
    }
    if True in scores_mean:
        acc['mean'] = Counter(scores_mean)[True] / len(scores_mean)
    if True in scores_median:
        acc['median'] = Counter(scores_median)[True] / len(scores_median)
    return acc


def compute_accuracy_for_all_classes(df_alpha, classes_alpha, classes_fnames):
    acc = dict()
    for class_uri in classes_alpha:
        df_alpha_class = df_alpha[df_alpha.fname.isin(classes_fnames[class_uri])]
        # print("classes_fname: <%s>" % class_uri)
        # print(classes_fnames[class_uri])
        # print(df_alpha_class)
        acc[class_uri] = compute_class_alpha_accuracy(df_alpha_class, classes_alpha[class_uri])
    return acc


def get_alpha_one_class_out(df_scores):
    d = dict()
    for idx, row in df_scores.iterrows():
        # print("row")
        # print(row)
        if row['mean'] >= 0 and row['median'] >= 0 and row['num'] > 0:
            for idx2, row2 in df_scores.iterrows():
                if idx == idx2:
                    continue
                if row2['mean'] >= 0 and row2['median'] >= 0 and row2['num'] > 0:
                    if row['class'] not in d:
                        d[row['class']] = {
                            'mean': [],
                            'median': []
                        }
                    d[row['class']]['mean'].append(row2['mean'])
                    d[row['class']]['median'].append(row2['median'])

    for class_uri in d:
        d[class_uri]['mean'] = np.mean(d[class_uri]['mean'])
        d[class_uri]['median'] = np.median(d[class_uri]['median'])
    return d


def get_classes_fnames(fpath, dataset, ext=".csv"):
    d = dict()
    f = open(fpath)
    for line in f.readlines():
        sline = line.strip()
        if sline == "":
            continue
        if dataset == "wcv2":
            fname, _, class_uri = sline.split(',')
        elif dataset == "wcv1":
            fname, _, class_uri, _ = sline.split(',')
            fname = fname.split(".")[0]
        else:
            raise Exception("Unknown dataset")
        fname = fname.replace('"', '')
        fname += ext
        # fname += ".csv"
        # #DEBUG
        # print("%s> fname: %s" % (__name__, fname))
        class_uri = class_uri.replace('"', "")
        if class_uri not in d:
            d[class_uri] = []
        d[class_uri].append(fname)
    return d


def get_accuracy(df_alpha, df_scores, classes_fnames):
    acc = dict()
    for fsid in range(1, 6):
        df_alpha_fsid = df_alpha[df_alpha.fsid == fsid]
        df_scores_fsid = df_scores[df_scores.fsid == fsid]
        alpha_per_class = get_alpha_one_class_out(df_scores_fsid)
        acc[fsid] = compute_accuracy_for_all_classes(df_alpha_fsid, alpha_per_class, classes_fnames)
    return acc


def generate_diagram(acc, draw_file_base):
    """
    :param acc: acc
    :param draw_file_base: base of the diagram
    :return: None
    """
    for fsid in range(1, 6):
        rows = []
        for class_uri in acc[fsid]:
            for a_attr in ['mean', 'median']:
                r = [shorten_uri(class_uri), acc[fsid][class_uri][a_attr], a_attr]
                rows.append(r)
        data = pd.DataFrame(rows, columns=['Class', 'Accuracy', 'Aggr'])

        ax = sns.barplot(x="Accuracy", y="Class",
                         hue="Aggr",
                         data=data, linewidth=1.0,
                         # palette="colorblind",
                         # palette="Spectral",
                         # palette="pastel",
                         # palette="ch:start=.2,rot=-.3",
                         # palette="YlOrBr",
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
        print(ax.get_yticklabels())
        labels = [t.get_text() for t in texts]
        ax.set_yticks(new_ticks)
        ax.set_yticklabels(labels, fontsize=8)
        print(ax.get_yticklabels())
        draw_fname = draw_file_base+"_fsid%d" % (fsid)
        plt.setp(ax.lines, color='k')
        ax.figure.savefig('docs/%s.svg' % draw_fname, bbox_inches="tight")
        ax.figure.clf()


def workflow(falpha, fscores, draw_basename, dataset, fmeta):
    df_alphas = pd.read_csv(falpha)
    df_scores = pd.read_csv(fscores)
    classes_fnames = get_classes_fnames(fmeta, dataset)
    acc = get_accuracy(df_alphas, df_scores, classes_fnames)
    generate_diagram(acc, draw_basename)
    # print(acc)
    # df_meta = pd.read_csv(fmeta)


def main():
    """
    Parse the arguments
    :return:
    """
    parser = argparse.ArgumentParser(description='Evaluate the accuracy of alpha among all classes (k-fold).')
    parser.add_argument('--falpha', help="The path to the alpha results file.")
    parser.add_argument('--fmeta', help="The path to the meta file which contain the filenames and classes.")
    parser.add_argument('--dataset', choices=['wcv1', 'wcv2'], help="The path to the csv files")
    parser.add_argument('--draw', help="The base name for the diagram file (without the extension)")
    parser.add_argument('--fscores', help="The path to the k-fold scores file")
    args = parser.parse_args()

    if args.falpha and args.fscores and args.fmeta and args.dataset and args.draw:
        workflow(falpha=args.falpha, fscores=args.fscores, draw_basename=args.draw,
                 fmeta=args.fmeta, dataset=args.dataset)
    else:
        parser.print_usage()
        parser.print_help()


if __name__ == "__main__":
    main()
