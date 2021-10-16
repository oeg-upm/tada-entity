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
from annotator.annot import Annotator
from commons import ENDPOINT
from experiments.alpha_analysis import shorten_uri
from experiments.alpha_eval_one import get_classes_fnames, generate_diagram

import matplotlib.pyplot as plt


def add_alpha_per_file(df_alphas):
    """
    Add mid alpha between from_alpha and to_alpha for each file

    :param df_alphas:
    :return:
    """
    alphas = []
    for idx, row in df_alphas.iterrows():
        # print("idx: %d" % idx)
        if row['from_alpha'] >= 0 and row['to_alpha'] >= 0:
            a = (row['from_alpha'] + row['to_alpha']) * 0.5
        else:
            a = -1
        alphas.append(a)
    df_alphas.insert(5, 'alpha', alphas)


def annotate_column(fpath, col_id, title_case):
    """
    Get the annotator which includes the annotations

    :param fpath:
    :param col_id:
    :param title_case:
    :return:
    """
    # create empty logger to disable the logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    annotator = Annotator(endpoint=ENDPOINT, title_case=title_case, num_of_threads=3, logger=logger,
                               class_prefs=["http://dbpedia.org/ontology/", "http://www.w3.org/2002/07/owl#Thing"])
    annotator.annotate_table(file_dir=fpath, subject_col_id=col_id)
    return annotator


def predict_class(annotator, fsid, alpha):
    """
    Returns the candidates using a given alpha and fsid

    :param annotator:
    :param fsid:
    :param alpha:
    :return:
    """
    annotator.compute_f(alpha)
    candidates = annotator.get_top_k(fsid=fsid)
    return candidates


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


def compute_file_acc(row, alphas_classes, data_path, correct_class_uri, title_case):
    annotator = annotate_column(os.path.join(data_path, row['fname']), row['colid'], title_case)
    acc = dict()
    for fsid in range(1, 6):
        acc[fsid] = {
            'mean': -1,
            'median': -1
        }
        for a_attr in ['mean', 'median']:
            candidate_alpha = -1
            candidate_class = None
            for class_uri in alphas_classes[fsid]:
                # print(alphas_classes)
                # print("=====")
                # print(alphas_classes[fsid])
                alpha = alphas_classes[fsid][class_uri][a_attr]
                candidates = predict_class(annotator, fsid, alpha)
                # print("pred_class")
                if candidates == []:
                    print("No candidates")
                    continue
                pred_class = candidates[0]
                # print("fsid: %d - class: %s - alpha: %f" % (fsid, pred_class, alpha))
                if pred_class == class_uri:
                    if candidate_alpha < alpha:
                        if candidate_alpha >= 0:
                            print("compute_file_acc> Prediction of %s colid %d (fsid %d)" % (row['fname'], row['colid'], fsid))
                            print("\tSwitch <%s, %d> to <%s, %d>" % (candidate_class, candidate_alpha, pred_class, alpha))
                        candidate_alpha = alpha
                        candidate_class = class_uri
            if candidate_class == correct_class_uri:
                res = 1
                # print("Correct candidate: fsid: %d - class: %s (correct: %s)- alpha: %f - a_attr: %s - fname: %s" % (fsid, candidate_class, correct_class_uri, alpha, a_attr, row['fname']))
            else:
                res = 0
                # print(row)
                print("Invalid candidate: fsid: %d - class: %s (correct: %s)- alpha: %f - a_attr: %s - fname: %s" % (fsid, candidate_class, correct_class_uri, alpha, a_attr, row['fname']))
            acc[fsid][a_attr] = res
    return acc


def get_file_acc(row, class_files_alpha, alphas_classes, class_uri, title_case, data_path):
    # old = alphas_classes[class_uri].copy()
    print("get_file_acc> alphas classes: ")
    print(alphas_classes)
    print("fname: %s colid: %d fsid: %d" % (row['fname'], row['colid'], row['fsid']))

    old = dict()
    for fsid in range(1, 6):
        old[fsid] = dict()
        old[fsid][class_uri] = alphas_classes[fsid][class_uri].copy()
    # print("Checking ")
    # print("fname: %s colid: %d fsid: %d" % (row['fname'], row['colid'], row['fsid']))
    # print(class_files_alpha)
    alphas_classes[class_uri] = class_files_alpha[row.fsid][row.fname][row.colid].copy()
    # acc = compute_file_acc(row, alphas_classes)
    # df_fname = df_class[df_class.fname == row.fname]
    # df_col = df_fname[df_fname.colid == row.colid]
    acc = compute_file_acc(row=row, alphas_classes=alphas_classes, data_path=data_path, correct_class_uri=class_uri,
                           title_case=title_case)
    # print("fname: %s colid: %d fsid: %d" % (row['fname'], row['colid'], row['fsid']))
    # print("get_file_acc> keys: "+str(list(acc.keys())))
    # """
    # (row, alphas_classes, data_path, correct_class_uri, title_case)
    # """
    # alphas_classes[class_uri] = old

    for fsid in range(1, 6):
        alphas_classes[fsid][class_uri] = old[fsid][class_uri]

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
                    alphas[fsid][row['fname']] = {row['colid']: []}
                alphas[fsid][row['fname']][row['colid']].append(row2['alpha'])

    for fsid in alphas:
        for fname in alphas[fsid]:
            for colid in alphas[fsid][fname]:
                d = {
                    'mean': np.mean(alphas[fsid][fname][colid]),
                    'media': np.median(alphas[fsid][fname][colid])
                }
                alphas[fsid][fname][colid] = d
    return alphas


# def get_acc_per_class(df_class, alphas_classes, class_uri):
#     acc = []
#     for idx, row in df_class.iterrows():
#         acc.append(get_file_acc(row, idx, alphas_classes, class_uri, df_class))
#     return sum(acc)/len(acc)


def get_acc_per_class(df_class, alphas_classes, class_uri, title_case, data_path):
    # Get the alpha (mean and median) for file class (using one file out from the same class) for the given rows.
    # print("\n\ndf_class: ")
    # print(df_class)
    class_files_alpha = get_class_files_alphas(df_class)
    # print("class_files_alpha: ")
    # print(class_files_alpha)
    acc = dict()
    computed_files = dict()
    # print("get_acc_per_class> in")
    # print(df_class)
    for idx, row in df_class.iterrows():
        # print("row: ")
        # print(row)
        if row['fname'] in computed_files:
            if row['colid'] in computed_files[row['fname']]:
                continue
        # print(row)
        # print("===========\n\n")
        # print("fname: %s" % row['fname'])
        file_acc = get_file_acc(row, class_files_alpha, alphas_classes, class_uri, title_case, data_path)
        # print("get_acc_per_class> file_acc: ")
        # print(file_acc)
        # print("=======")
        for fsid in file_acc:
            # print("get_acc_per_class> fsid: %d" % fsid)
            if fsid not in acc:
                acc[fsid] = {'mean': [], 'median': []}
            for a_attr in file_acc[fsid]:
                # print("\t%s" % a_attr)
                # print(file_acc[fsid][a_attr])
                acc[fsid][a_attr].append(file_acc[fsid][a_attr])
        if row['fname'] not in computed_files:
            computed_files[row['fname']] = dict()
        computed_files[row['fname']][row['colid']] = True

    for fsid in acc:
        for a_attr in acc[fsid]:
            acc[fsid][a_attr] = sum(acc[fsid][a_attr])/len(acc[fsid][a_attr])
    # print(acc)
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


def get_accuracy_for_classes(df_alphas, classes_fnames, alphas_classes, title_case, data_path):
    acc = dict()
    for class_uri in classes_fnames:
        # Get rows with files (with their colid) of the class class_uri
        # print("get_accuracy_for_classes> class uri: %s" % class_uri)
        # print("Pre")
        # print(df_alphas)
        # print("classes fnames: ")
        # print(classes_fnames)
        # df_class = df_alphas[df_alphas[['fname', 'colid']].apply(tuple, axis=1).isin(classes_fnames[class_uri])]
        # print("tuple: ")
        # print(tuple(tuple(t) for t in classes_fnames[class_uri]))
        # df_class = df_alphas[df_alphas[['fname', 'colid']].apply(tuple, axis=1).isin(tuple(classes_fnames[class_uri]))]
        t = [tuple(tt) for tt in classes_fnames[class_uri]]
        # print(t)
        df_class = df_alphas[df_alphas[['fname', 'colid']].apply(tuple, axis=1).isin(t)]

        # print("Post")
        # print(df_class)
        # print("\n\n")
        # df_class = df_alphas[df_alphas.fname.isin(classes_fnames[class_uri])]
        # Get accuracy of the class_uri
        acc[class_uri] = get_acc_per_class(df_class, alphas_classes, class_uri, title_case, data_path)
        # print("Acc: ")
        # print(acc[class_uri])
    return acc


def get_alpha_per_class(df_alphas, classes_fnames):
    d = dict()
    for class_uri in classes_fnames:
        print("get_alpha_per_class> ")
        print(class_uri)
        t = [tuple(tt) for tt in classes_fnames[class_uri]]
        df_class = df_alphas[df_alphas[['fname', 'colid']].apply(tuple, axis=1).isin(t)]
        print(df_class)
        # df_class = df_alphas[df_alphas.fname.isin(classes_fnames[class_uri])]
        for idx, row in df_class.iterrows():
            if row['from_alpha'] >= 0 and row['to_alpha'] >= 0:
                if class_uri not in d:
                    d[class_uri] = {'alphas': []}
                # if 'alphas' not in d[class_uri]:
                #     d[class_uri]['alphas'] = []
                d[class_uri]['alphas'].append((row['from_alpha'] + row['to_alpha']) * 0.5)

    for class_uri in d:
        if class_uri in d and len(d[class_uri]) > 0:
            d[class_uri]['mean'] = np.mean(d[class_uri]['alphas'])
            d[class_uri]['median'] = np.median(d[class_uri]['alphas'])
    return d


def get_accuracy(df_alphas, classes_fnames, title_case, data_path):
    alphas_classes = dict()
    for fsid in range(1, 6):
        df_alphas_fsid = df_alphas[df_alphas.fsid == fsid]
        alphas_classes[fsid] = get_alpha_per_class(df_alphas_fsid, classes_fnames)
        print("get_accuracy> ")
        print(alphas_classes[fsid])
    acc = get_accuracy_for_classes(df_alphas, classes_fnames, alphas_classes, title_case, data_path)
    return acc


def workflow(falpha, draw_basename, dataset, fmeta, title_case, data_path):
    df_alphas = pd.read_csv(falpha)
    df_alphas[["colid"]] = df_alphas[["colid"]].apply(pd.to_numeric)
    add_alpha_per_file(df_alphas)
    classes_fnames = get_classes_fnames_col_ids(fmeta, dataset)
    acc = get_accuracy(df_alphas, classes_fnames, title_case, data_path)
    generate_diagram(acc, draw_basename)


def get_classes_fnames_col_ids(fpath, dataset, ext=".csv", subject_col_fpath=None):
    d = dict()
    f = open(fpath)
    if dataset == "wcv2":
        with open(subject_col_fpath) as f_subj_col:
            subj_col_dict = dict()
            for line in f_subj_col:
                sline = line.strip()
                if sline == "":
                    continue
                fn, colid = line.split(',')
                colid = int(colid)
                subj_col_dict[fn+".tar.gz"] = colid

    for line in f.readlines():
        sline = line.strip()
        if sline == "":
            continue
        if dataset == "wcv2":
            fname, _, class_uri = sline.split(',')
            colid = subj_col_dict[fname]
        elif dataset == "wcv1":
            fname, _, class_uri, colid = sline.split(',')
            fname = fname.split(".")[0]
            colid = int(colid)
        else:
            raise Exception("Unknown dataset")
        fname = fname.replace('"', '')
        fname += ext
        class_uri = class_uri.replace('"', "")
        if class_uri not in d:
            d[class_uri] = []
        d[class_uri].append([fname, colid])
    f.close()
    return d


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
    parser.add_argument('--title_case', default="title", choices=["title", "original"],
                        help="Whether title case or not. true or false")
    parser.add_argument('--data-path', help="The path to the data (csv files)")
    args = parser.parse_args()

    if args.falpha and args.fscores and args.fmeta and args.dataset and args.draw and args.data_path:
        workflow(falpha=args.falpha, draw_basename=args.draw, data_path=args.data_path,
                 fmeta=args.fmeta, dataset=args.dataset, title_case=(args.title_case.lower() == "title"))
    else:
        parser.print_usage()
        parser.print_help()


if __name__ == "__main__":
    main()


