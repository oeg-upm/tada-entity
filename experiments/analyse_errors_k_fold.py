"""
This script is to analyse misclassifications related to k-fold leave one out cross validation
with class or files. So this is also used to validate One alpha for all as well.
"""
import argparse
import seaborn as sns
import pandas as pd
import numpy as np

from experiments.alpha_analysis import shorten_uri
from experiments.alpha_cond_pair import get_classes_fnames_col_ids, add_alpha_per_file
from experiments.alpha_analysis import shorten_uri
import experiments.alpha_eval_one as one

from collections import Counter
import matplotlib.pyplot as plt


def check_range_per_class(df_alphas, classes_fnames):
    ranges = []
    for class_uri in classes_fnames:
        t = [tuple(tt) for tt in classes_fnames[class_uri]]
        df_class = df_alphas[df_alphas[['fname', 'colid']].apply(tuple, axis=1).isin(t)]
        if len(df_class.index) > 1:
            diff = max(df_class['alpha']) - min(df_class['alpha'])
            ranges.append(diff)
            # r_mean = np.mean(df_class['alpha'])
            # # ranges['mean'].append(r_mean)
            # r_median = np.median(df_class['alpha'])
            # ranges['median'].append(r_median)

            # print("\t\t%s\t\t%f" % (shorten_uri(class_uri), diff))
    return ranges


def check_ranges_per_fsid_workflow(falpha, fmeta, dataset, subject_col):
    df_alphas = pd.read_csv(falpha)
    df_alphas[["colid"]] = df_alphas[["colid"]].apply(pd.to_numeric)
    add_alpha_per_file(df_alphas)
    classes_fnames = get_classes_fnames_col_ids(fmeta, dataset, subject_col_fpath=subject_col)
    df_alphas = df_alphas[df_alphas.from_alpha >= 0]
    print("|fsid\t|range mean\t| range median\t|")
    print("|:---:|:---:|:---:|")
    for fsid in range(1, 6):
        # print("\n\nfsid: %d" % fsid)
        df_fsid = df_alphas[df_alphas.fsid == fsid]
        a_range = check_range_per_class(df_fsid, classes_fnames)
        print("|%d\t|%f\t|%f\t|" % (fsid, np.mean(a_range), np.median(a_range)))


def check_sd_per_class(df_alphas, classes_fnames):
    class_alphas = {
        'mean': [],
        'median': []
    }
    diffs = {
        'mean': [],
        'median': []
    }
    for class_uri in classes_fnames:
        t = [tuple(tt) for tt in classes_fnames[class_uri]]
        df_class = df_alphas[df_alphas[['fname', 'colid']].apply(tuple, axis=1).isin(t)]
        if len(df_class.index) > 1:
            class_alphas['mean'].append(np.mean(df_class['alpha']))
            class_alphas['median'].append(np.median(df_class['alpha']))

    mean_val = np.mean(class_alphas['mean'])
    median_val = np.median(class_alphas['median'])
    for i in range(len('mean')):
        d = abs(class_alphas['mean'][i]-mean_val)
        diffs['mean'].append(d)
        d = abs(class_alphas['median'][i]-median_val)
        diffs['median'].append(d)
    return diffs


def check_sd_per_fsid_workflow(falpha, fmeta, dataset, subject_col):
    df_alphas = pd.read_csv(falpha)
    df_alphas[["colid"]] = df_alphas[["colid"]].apply(pd.to_numeric)
    add_alpha_per_file(df_alphas)
    classes_fnames = get_classes_fnames_col_ids(fmeta, dataset, subject_col_fpath=subject_col)
    df_alphas = df_alphas[df_alphas.from_alpha >= 0]
    print("|fsid\t|distance mean\t| distance median\t|")
    print("|:---:|:---:|:---:|")
    for fsid in range(1, 6):
        # print("\n\nfsid: %d" % fsid)
        df_fsid = df_alphas[df_alphas.fsid == fsid]
        diffs = check_sd_per_class(df_fsid, classes_fnames)
        print("|%d\t|%f\t|%f\t|" % (fsid, np.mean(diffs['mean']), np.median(diffs['median'])))


def check_one_per_fsid_workflow(falpha, fmeta, dataset, draw_fname_base):
    df_alphas = pd.read_csv(falpha)
    df_alphas[["colid"]] = df_alphas[["colid"]].apply(pd.to_numeric)
    add_alpha_per_file(df_alphas)
    classes_fnames = one.get_classes_fnames(fmeta, dataset)  # get_classes_fnames_col_ids(fmeta, dataset, subject_col_fpath=subject_col)
    df_alphas = df_alphas[df_alphas.from_alpha >= 0]

    print("|fsid\t|class\t|alpha mean\t|mean alpha used\t|alpha median\t|median alpha used\t|")
    print("|:---:|:---:|:---:|:---:|:---:|:---:|")
    compa = dict()
    for fsid in range(1, 6):
        # print("\n\nfsid: %d" % fsid)
        df_alpha_fsid = df_alphas[df_alphas.fsid == fsid]

        alphas_per_class_optimal = one.get_alpha_per_class(df_alpha_fsid, classes_fnames)
        alpha_per_class_used = one.get_alpha_one_class_out(alphas_per_class_optimal)
        # print(alphas_per_class_optimal)
        # print(alpha_per_class_used)
        compa[fsid] = dict()
        for class_uri in alphas_per_class_optimal:
            if class_uri not in alpha_per_class_used:
                continue
            print("|%d\t|%s\t|%f\t|%f\t|%f\t|%f\t|" % (fsid, shorten_uri(class_uri), alphas_per_class_optimal[class_uri]['mean'], alpha_per_class_used[class_uri]['mean'],
                                        alphas_per_class_optimal[class_uri]['median'], alpha_per_class_used[class_uri]['median']))
            compa[fsid][class_uri] = {
                'optimal alpha (mean)': alphas_per_class_optimal[class_uri]['mean'],
                'optimal alpha (median)': alphas_per_class_optimal[class_uri]['median'],
                'predicted alpha (mean)': alpha_per_class_used[class_uri]['mean'],
                'predicted alpha (median)': alpha_per_class_used[class_uri]['median']
            }
#             compa[fsid][class_uri] = {
#                 'optimal class alpha (using mean)': alphas_per_class_optimal[class_uri]['mean'],
# #                'class alpha media': alphas_per_class_optimal[class_uri]['median'],
#                 'predicted alpha (using mean)': alpha_per_class_used[class_uri]['mean'],
# #               'one-out alpha median': alpha_per_class_used[class_uri]['median']
#             }
    if draw_fname_base:
        generate_diagram_one(compa, draw_fname_base)


def generate_diagram_one(compa, draw_file_base):
    """
    :param acc: acc
    :param draw_file_base: base of the diagram
    :return: None
    """
    sns.set(rc={'figure.figsize': (11.7, 14)})
    sns.set_style("white")
    for fsid in compa:
        rows = []
        for class_uri in compa[fsid]:
            for a_attr in compa[fsid][class_uri]:
                r = [shorten_uri(class_uri), compa[fsid][class_uri][a_attr], a_attr]
                rows.append(r)
        data = pd.DataFrame(rows, columns=['Class', 'Alpha', 'Aggr'])

        ax = sns.barplot(x="Alpha", y="Class",
                         hue="Aggr",
                         data=data, linewidth=1.0,
                         # palette="colorblind",
                         # palette="Spectral",
                         # palette="pastel",
                         # palette="ch:start=.2,rot=-.3",
                         # palette="YlOrBr",
                         # dodge=False,
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
        draw_fname = draw_file_base+"_fsid%d" % (fsid)
        # change_width(ax, 0.35)

        plt.setp(ax.lines, color='k')
        ax.figure.savefig('docs/%s.svg' % draw_fname, bbox_inches="tight")
        ax.figure.clf()


def main():
    """
    Parse the arguments
    :return:
    """
    parser = argparse.ArgumentParser(description='Error analysis of k-fold leave one out cross validation')
    parser.add_argument('action', choices=['range', 'sd', 'one'], help="The action/analysis to perform")
    parser.add_argument('--falpha', help="The path to the alpha results file.")
    parser.add_argument('--fmeta', help="The path to the meta file which contain the filenames and classes.")
    parser.add_argument('--dataset', choices=['wcv1', 'wcv2'], help="The path to the csv files")
    parser.add_argument('--draw', help="The base name for the diagram file (without the extension)")
    # parser.add_argument('--title_case', default="title", choices=["title", "original"],
    #                     help="Whether title case or not. true or false")
    # parser.add_argument('--data-path', help="The path to the data (csv files)")
    parser.add_argument('--subject-col', help="The path to the subject column file (only for wcv2)")
    args = parser.parse_args()

    if args.action == "range":  # Check the mean and the median range of alphas per fsid
        check_ranges_per_fsid_workflow(falpha=args.falpha, fmeta=args.fmeta, dataset=args.dataset,
                              subject_col=args.subject_col)
    elif args.action == "sd":  # Check the average distance of class alphas from the mean per fsid
        check_sd_per_fsid_workflow(falpha=args.falpha, fmeta=args.fmeta, dataset=args.dataset,
                              subject_col=args.subject_col)
    elif args.action == "one": # Check the errors of classes using a single alpha for all with leave one class out
        check_one_per_fsid_workflow(falpha=args.falpha, fmeta=args.fmeta, dataset=args.dataset,
                              draw_fname_base=args.draw)
    #
    # if args.falpha and args.fmeta and args.dataset and args.draw:
    #     workflow(falpha=args.falpha, draw_basename=args.draw,
    #              fmeta=args.fmeta, dataset=args.dataset)
    else:
        parser.print_usage()
        parser.print_help()


if __name__ == "__main__":
    main()
