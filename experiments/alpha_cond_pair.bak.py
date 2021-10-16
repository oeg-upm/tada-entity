"""
This is about the prediction of alpha using the conditional input output pair of parameters and outcome
"""

import os
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
from collections import Counter
import logging

from experiments.alpha_analysis import shorten_uri
from experiments.alpha_eval_one import get_classes_fnames, generate_diagram, get_alpha_per_class

import matplotlib.pyplot as plt


def add_alpha_per_file(df_alphas):
    for class_uri in classes_fnames:
        df_class = df_alphas[df_alphas.fname.isin(classes_fnames[class_uri])]
        for idx, row in df_class.iterrows():
            if row['from_alpha'] >= 0 and row['to_alpha'] >= 0:
                row['alpha'] = (row['from_alpha'] + row['to_alpha']) * 0.5
            else:
                row['alpha'] = -1


def predict_class(row, alphas_classes):
    pass


def validate_annotation(class_uri, fname, col_id, fpath, title_case, alphas_fsid):
    # create empty logger to disable the logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # logger = None
    annotator = Annotator(endpoint=ENDPOINT, title_case=title_case, num_of_threads=3, logger=logger,
                               class_prefs=["http://dbpedia.org/ontology/", "http://www.w3.org/2002/07/owl#Thing"])
    annotator.annotate_table(file_dir=fpath, subject_col_id=col_id)
    d = dict()
    for fsid in range(1, 6):
        d[fsid] = dict()
        for a_attr in ['alpha_mean', 'alpha_median']:
            if class_uri in alphas_fsid[fsid] and fname in alphas_fsid[fsid][class_uri]:
                annotator.compute_f(alphas_fsid[fsid][class_uri][fname][a_attr])
                candidates = annotator.get_top_k(fsid=fsid)
                if len(candidates) > 0 and class_uri == candidates[0]:
                    d[fsid][a_attr] = True
                else:
                    d[fsid][a_attr] = False
    return d



# def get_file_acc(row, idx, alphas_classes, class_uri, df_class):
#     old = alphas_classes[class_uri].copy()
#     alphas = []
#     for idx2, row2 in df_class[df_class.fsid == row.fsid].iterrows():
#         if idx == idx2:
#             continue
#         alphas.append(row2['alpha'])
#     alphas_classes[class_uri] = {
#         'mean': np.mean(alphas),
#         'media': np.median(alphas)
#     }
#     if predict_class(row) == class_uri:
#         return 1
#     return 0








## Need to continue work on this
def compute_file_acc(row, alphas_classes):
    acc = dict()
    for a_attr in ['mean', 'median']:
        max_alpha = -1
        corr_class = None
        for class_uri in alphas_classes:
            pred_class = get_pred()

### I need to continue working on this
def get_file_acc(row, class_files_alpha, alphas_classes, class_uri, df_class):
    old = alphas_classes[class_uri].copy()
    alphas_classes[class_uri] = class_files_alpha[row.fsid][row.fname].copy()
    # acc = compute_file_acc(row, alphas_classes)
    df_fname = df_class[df_class.fname == row.fname]
    df_col = df_fname[df_fname.colid == row.colid]
    acc = compute_file_acc(df_col, alphas_classes)
    alphas_classes[class_uri] = old
    return acc
    #     class_files_alpha[fsid][fname][a_attr]
    #
    # alphas_classes[class_uri] = alphas_classes
    # if predict_class(row) == class_uri:
    #     return 1
    # return 0




def get_class_files_alphas(df_class):
    """
    Compute the mean and media alphas to be used for each file using one out.
    :param df_class:
    :return:
    """
    # alphas_classes_fsid = dict()
    alphas = dict()
    # for fsid in range(1, 6):
    #     for class_uri in alphas_classes:
    #         if class_uri not in alphas_classes_fsid:
    #             alphas_classes_fsid[class_uri] = dict()
    #         alphas_classes_fsid[class_uri][fsid] = alphas_classes[class_uri].copy()
    #

    for fsid in range(1, 6):
        df_class_fsid = df_class[df_class.fsid == fsid]
        alphas[fsid] = dict()
        for idx, row in df_class_fsid.iterrows():
            for idx2, row2 in df_class_fsid.iterrows():
                if idx == idx2:
                    continue
                if row['fname'] not in alphas[fsid]:
                    alphas[fsid][row['fname']] = []
                alphas[fsid][row['fname']].append(row2['alpha'])

    for fsid in alphas:
        for fname in alphas[fsid]:
            d = {
                'mean': np.mean(alphas[fsid][fname]),
                'media': np.median(alphas[fsid][fname])
            }
            alphas[fsid][fname] = d
    return alphas


# def get_acc_per_class(df_class, alphas_classes, class_uri):
#     acc = []
#     for idx, row in df_class.iterrows():
#         acc.append(get_file_acc(row, idx, alphas_classes, class_uri, df_class))
#     return sum(acc)/len(acc)

def get_acc_per_class(df_class, alphas_classes, class_uri):
    # Get the alpha (mean and median) for each file (using one out file) for the given rows.
    class_files_alpha = get_class_files_alphas(df_class)
    acc = dict()
    computed_files = dict()
    for idx, row in df_class.iterrows():
        if row['fname'] in computed_files:
            continue
        file_acc = get_file_acc(row, class_files_alpha, alphas_classes, class_uri, df_class)
        if row.fsid not in acc:
            acc[row.fsid] = {'mean': [], 'median': []}
        for a_attr in ['mean', 'median']:
            acc[row.fsid][a_attr].append(file_acc[a_attr])
        computed_files[row['fname']] = True
    for a_attr in ['mean', 'median']:
        for fsid in acc:
            acc[fsid][a_attr] = sum(acc[fsid][a_attr])/len(acc[fsid][a_attr])
    return acc


# def get_accuracy_for_fsid(df_alphas, classes_fnames, alphas_classes):
#     acc = dict()
#     for class_uri in classes_fnames:
#         df_class = df_alphas[df_alphas.fname.isin(classes_fnames[class_uri])]
#         acc[class_uri] = get_acc_per_class(df_class, alphas_classes, class_uri)
#

# def get_alpha_per_class(df_alphas, classes_fnames, alphas_classes):
#     acc = dict()
#     for class_uri in classes_fnames:
#         df_class = df_alphas[df_alphas.fname.isin(classes_fnames[class_uri])]
#         acc[class_uri] = get_acc_per_class(df_class, alphas_classes, class_uri)


# def get_accuracy(df_alphas, classes_fnames):
#     acc = dict()
#     for fsid in range(1, 6):
#         df_alphas_fsid = df_alphas[df_alphas.fsid==fsid]
#         alphas_classes = get_alpha_per_class(df_alphas_fsid, classes_fnames)
#         acc[fsid] = get_accuracy_for_fsid(df_alphas_fsid, classes_fnames, alphas_classes)
#     return acc


def get_accuracy_for_classes(df_alphas, classes_fnames, alphas_classes):
    acc = dict()
    for class_uri in classes_fnames:
        # Get rows with files of the class class_uri
        df_class = df_alphas[df_alphas.fname.isin(classes_fnames[class_uri])]
        # Get accuracy of the class_uri
        acc[class_uri] = get_acc_per_class(df_class, alphas_classes, class_uri)
    return acc


def get_accuracy(df_alphas, classes_fnames):
    alphas_classes = dict()
    for fsid in range(1, 6):
        df_alphas_fsid = df_alphas[df_alphas.fsid == fsid]
        alphas_classes[fsid] = get_alpha_per_class(df_alphas_fsid, classes_fnames)
    acc = get_accuracy_for_classes(df_alphas, classes_fnames, alphas_classes)
    return acc


def workflow(falpha, draw_basename, dataset, fmeta):
    df_alphas = pd.read_csv(falpha)
    add_alpha_per_file(df_alphas)
    classes_fnames = get_classes_fnames(fmeta, dataset)
    acc = get_accuracy(df_alphas, df_scores, classes_fnames)
    generate_diagram(acc, draw_basename)


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
    args = parser.parse_args()

    if args.falpha and args.fscores and args.fmeta and args.dataset and args.draw:
        workflow(falpha=args.falpha, draw_basename=args.draw,
                 fmeta=args.fmeta, dataset=args.dataset)
    else:
        parser.print_usage()
        parser.print_help()


if __name__ == "__main__":
    main()


