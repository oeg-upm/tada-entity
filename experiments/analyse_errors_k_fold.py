"""
This script is to analyse misclassifications related to k-fold leave one out cross validation
"""
import argparse
import seaborn as sns
import pandas as pd
import numpy as np

from experiments.alpha_analysis import shorten_uri
from experiments.alpha_cond_pair import get_classes_fnames_col_ids, add_alpha_per_file
from experiments.alpha_analysis import shorten_uri


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
    for fsid in range(1, 6):
        # print("\n\nfsid: %d" % fsid)
        df_fsid = df_alphas[df_alphas.fsid == fsid]
        a_range = check_range_per_class(df_fsid, classes_fnames)
        print("fsid: %d ranges mean: %f, median: %f" % (fsid, np.mean(a_range), np.median(a_range)))


def main():
    """
    Parse the arguments
    :return:
    """
    parser = argparse.ArgumentParser(description='Error analysis of k-fold leave one out cross validation')
    parser.add_argument('action', choices=['range'], help="The action/analysis to perform")
    parser.add_argument('--falpha', help="The path to the alpha results file.")
    parser.add_argument('--fmeta', help="The path to the meta file which contain the filenames and classes.")
    parser.add_argument('--dataset', choices=['wcv1', 'wcv2'], help="The path to the csv files")
    parser.add_argument('--draw', help="The base name for the diagram file (without the extension)")
    # parser.add_argument('--title_case', default="title", choices=["title", "original"],
    #                     help="Whether title case or not. true or false")
    # parser.add_argument('--data-path', help="The path to the data (csv files)")
    parser.add_argument('--subject-col', help="The path to the subject column file (only for wcv2)")
    args = parser.parse_args()

    if args.action == "range":
        check_ranges_per_fsid_workflow(falpha=args.falpha, fmeta=args.fmeta, dataset=args.dataset,
                              subject_col=args.subject_col)
    #
    # if args.falpha and args.fmeta and args.dataset and args.draw:
    #     workflow(falpha=args.falpha, draw_basename=args.draw,
    #              fmeta=args.fmeta, dataset=args.dataset)
    else:
        parser.print_usage()
        parser.print_help()


if __name__ == "__main__":
    main()
