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
from experiments.alpha_eval_one import get_classes_fnames

import matplotlib.pyplot as plt


def add_alpha_per_file(df_alphas):
    """
    Add mid alpha between from_alpha and to_alpha for each file

    :param df_alphas:
    :return:
    """
    alphas = []
    for idx, row in df_alphas.iterrows():
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
    annotator = Annotator(endpoint=ENDPOINT, title_case=title_case, num_of_threads=3, logger=None,
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


def compute_file_acc(row, alphas_classes, data_path, correct_class_uri, title_case, alpha_voting="max"):
    annotator = annotate_column(os.path.join(data_path, row['fname']), row['colid'], title_case)
    acc = dict()
    for fsid in range(1, 6):
        acc[fsid] = {
            'mean': -1,
            'median': -1
        }
        for a_attr in ['mean', 'median']:
            if fsid in alphas_classes and correct_class_uri in alphas_classes[fsid]:
                if alphas_classes[fsid][correct_class_uri][a_attr] == -1:
                    acc[fsid][a_attr] = -1
                    print("compute_file_acc> set accuracy to -1 for %s with fsid %d attr %s" % (row.fname, fsid, a_attr))
                    continue
                candidate_alpha = -1
                candidate_class = None
                for class_uri in alphas_classes[fsid]:
                    alpha = alphas_classes[fsid][class_uri][a_attr]
                    candidates = predict_class(annotator, fsid, alpha)
                    if candidates == []:
                        print("No candidates")
                        continue
                    pred_class = candidates[0]
                    if pred_class == class_uri:
                        if alpha_voting == "max":
                            if candidate_alpha < alpha:
                                if candidate_alpha >= 0:
                                    print("compute_file_acc> Prediction of %s colid %d (fsid %d)" % (row['fname'], row['colid'], fsid))
                                    print("\tSwitch max <%s, %f> to <%s, %f>" % (candidate_class, candidate_alpha, pred_class, alpha))
                                candidate_alpha = alpha
                                candidate_class = class_uri
                        elif alpha_voting == "min":
                            if candidate_alpha > -1:
                                if candidate_alpha > alpha:
                                    print("compute_file_acc> Prediction of %s colid %d (fsid %d)" % (
                                    row['fname'], row['colid'], fsid))
                                    print("\tSwitch min <%s, %f> to <%s, %f>" % (candidate_class, candidate_alpha, pred_class, alpha))
                                    candidate_alpha = alpha
                                    candidate_class = class_uri
                            else:
                                candidate_alpha = alpha
                                candidate_class = class_uri
                        else:
                            raise Exception("unknown alpha voting method")
                if candidate_class == correct_class_uri:
                    res = 1
                else:
                    res = 0
                    print("Invalid candidate: fsid: %d - class: %s (correct: %s)- alpha: %f - a_attr: %s - fname: %s" % (fsid, candidate_class, correct_class_uri, alpha, a_attr, row['fname']))
                acc[fsid][a_attr] = res
    return acc


def get_file_acc(row, class_files_alpha, alphas_classes, class_uri, title_case, data_path, alpha_voting):
    old = dict()
    for fsid in range(1, 6):
        old[fsid] = dict()
        if fsid in alphas_classes and class_uri in alphas_classes[fsid]:
            old[fsid][class_uri] = alphas_classes[fsid][class_uri].copy()
            # Just to verify
            alphas_classes[fsid][class_uri] = None

            if fsid in class_files_alpha and row.fname in class_files_alpha[fsid] and row.colid in class_files_alpha[fsid][row.fname]:
                alphas_classes[fsid][class_uri] = class_files_alpha[fsid][row.fname][row.colid].copy()
            else:
                alphas_classes[fsid][class_uri] = {'mean': -1, 'median': -1}
    acc = compute_file_acc(row=row, alphas_classes=alphas_classes, data_path=data_path, correct_class_uri=class_uri,
                           title_case=title_case, alpha_voting=alpha_voting)
    for fsid in range(1, 6):
        if fsid in old and class_uri in old[fsid]:
            alphas_classes[fsid][class_uri] = old[fsid][class_uri]
    return acc


def get_class_files_alphas(df_class):
    """
    Compute the mean and media alphas to be used for each file using one out.
    :param df_class:
    :return:
    """
    alphas = dict()
    for fsid in range(1, 6):
        df_class_fsid = df_class[df_class.fsid == fsid]
        alphas[fsid] = dict()
        for idx, row in df_class_fsid.iterrows():
            if row['alpha'] >= 0:
                for idx2, row2 in df_class_fsid.iterrows():
                    if idx == idx2:
                        continue
                    if row['fname'] not in alphas[fsid]:
                        alphas[fsid][row['fname']] = {row['colid']: []}
                    if row2['alpha'] >= 0:
                        alphas[fsid][row['fname']][row['colid']].append(row2['alpha'])

    for fsid in alphas:
        for fname in alphas[fsid]:
            for colid in alphas[fsid][fname]:
                d = {
                    'mean': np.mean(alphas[fsid][fname][colid]),
                    'median': np.median(alphas[fsid][fname][colid])
                }
                alphas[fsid][fname][colid] = d
    return alphas


def get_acc_per_class(df_class, alphas_classes, class_uri, title_case, data_path, alpha_voting):
    # Get the alpha (mean and median) for file class (using one file out from the same class) for the given rows.
    class_files_alpha = get_class_files_alphas(df_class)
    acc = dict()
    computed_files = dict()

    for idx, row in df_class.iterrows():
        if row['fname'] in computed_files:
            if row['colid'] in computed_files[row['fname']]:
                continue

        file_acc = get_file_acc(row, class_files_alpha, alphas_classes, class_uri, title_case, data_path, alpha_voting)
        for fsid in file_acc:
            if fsid not in acc:
                acc[fsid] = {'mean': [], 'median': []}
            for a_attr in file_acc[fsid]:
                if file_acc[fsid][a_attr] >= 0:
                    acc[fsid][a_attr].append(file_acc[fsid][a_attr])
        if row['fname'] not in computed_files:
            computed_files[row['fname']] = dict()
        computed_files[row['fname']][row['colid']] = True

    for fsid in acc:
        for a_attr in acc[fsid]:
            # # DEBUG
            # print("\nDEBUG: ")
            # print(acc[fsid][a_attr])
            # in case there is a single file, one file out per class is not applicable
            if len(acc[fsid][a_attr]) <= 1:
                acc[fsid][a_attr] = -1
                print("get_acc_per_class> Ignoring fsid %d for class %s" % (fsid, class_uri))
                continue
            else:
                # if -1 in acc[fsid][a_attr]:
                #     raise Exception("Something went wrong")
                acc[fsid][a_attr] = sum(acc[fsid][a_attr])/len(acc[fsid][a_attr])
    return acc


def get_accuracy_for_classes(df_alphas, classes_fnames, alphas_classes, title_case, data_path, alpha_voting):
    acc = dict()
    for class_uri in classes_fnames:
        # # DEBUG
        # if 'Airline' not in class_uri:
        #     continue
        # Get rows with files (with their colid) of the class class_uri
        t = [tuple(tt) for tt in classes_fnames[class_uri]]
        df_class = df_alphas[df_alphas[['fname', 'colid']].apply(tuple, axis=1).isin(t)]
        # Get accuracy of the class_uri
        acc[class_uri] = get_acc_per_class(df_class, alphas_classes, class_uri, title_case, data_path, alpha_voting)
    return acc


def get_alpha_per_class(df_alphas, classes_fnames):
    d = dict()
    for class_uri in classes_fnames:
        t = [tuple(tt) for tt in classes_fnames[class_uri]]
        df_class = df_alphas[df_alphas[['fname', 'colid']].apply(tuple, axis=1).isin(t)]
        for idx, row in df_class.iterrows():
            if row['from_alpha'] >= 0 and row['to_alpha'] >= 0:
                if class_uri not in d:
                    d[class_uri] = {'alphas': []}
                d[class_uri]['alphas'].append((row['from_alpha'] + row['to_alpha']) * 0.5)

    to_be_del = []
    for class_uri in d:
        if class_uri in d and len(d[class_uri]['alphas']) > 1:
            d[class_uri]['mean'] = np.mean(d[class_uri]['alphas'])
            d[class_uri]['median'] = np.median(d[class_uri]['alphas'])
        else:
            to_be_del.append(class_uri)
    for c in to_be_del:
        del d[c]
    return d


def get_accuracy(df_alphas, classes_fnames, title_case, data_path, alpha_voting):
    alphas_classes = dict()
    for fsid in range(1, 6):
        df_alphas_fsid = df_alphas[df_alphas.fsid == fsid]
        alphas_classes[fsid] = get_alpha_per_class(df_alphas_fsid, classes_fnames)
    acc = get_accuracy_for_classes(df_alphas, classes_fnames, alphas_classes, title_case, data_path, alpha_voting)
    return acc


def workflow(falpha, draw_basename, dataset, fmeta, title_case, data_path, subject_col_fpath, alpha_voting):
    df_alphas = pd.read_csv(falpha)
    df_alphas[["colid"]] = df_alphas[["colid"]].apply(pd.to_numeric)
    add_alpha_per_file(df_alphas)
    classes_fnames = get_classes_fnames_col_ids(fmeta, dataset, subject_col_fpath=subject_col_fpath)
    acc = get_accuracy(df_alphas, classes_fnames, title_case, data_path, alpha_voting)
    print_accuracy_per_fsid(acc)
    if draw_basename:
        generate_diagram(acc, draw_basename)
    return acc


def print_accuracy_per_fsid(acc):
    print("|fsid\t|accuracy of mean\t|accuracy of median|")
    print("|:---:|:---:|:---:|")
    for fsid in range(1, 6):
        scores = {
            'mean': [],
            'median': []
        }
        for class_uri in acc:
            if fsid not in acc[class_uri]:
                continue
            for a_attr in ['mean', 'median']:
                if acc[class_uri][fsid][a_attr] == -1:
                    continue
                scores[a_attr].append(acc[class_uri][fsid][a_attr])
                # print("%d\t%s\t%s\t\t%f" % (fsid, shorten_uri(class_uri), a_attr, acc[class_uri][fsid][a_attr]))
        print("%d\t|%f\t|%f" % (fsid, np.mean(scores['mean']), np.mean(scores['median'])))



def get_classes_fnames_col_ids(fpath, dataset, ext=".csv", subject_col_fpath=None):
    d = dict()
    f = open(fpath)
    if dataset == "wcv2":
        with open(subject_col_fpath) as f_subj_col:
            subj_col_dict = dict()
            for line in f_subj_col:
                sline = line.strip()
                # sline = sline.replace('"', '')
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
            fname = fname.replace('"', '')
            print("fname: "+fname)
            print(subj_col_dict)
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


def generate_diagram(acc, draw_file_base):
    """
    :param acc: acc
    :param draw_file_base: base of the diagram
    :return: None
    """
    for fsid in range(1, 6):
        rows = []
        for class_uri in acc:
            if fsid not in acc[class_uri]:
                continue
            for a_attr in ['mean', 'median']:
                if acc[class_uri][fsid][a_attr] == -1:
                    continue
                r = [shorten_uri(class_uri), acc[class_uri][fsid][a_attr], a_attr]
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
        # print(ax.get_yticklabels())
        labels = [t.get_text() for t in texts]
        ax.set_yticks(new_ticks)
        ax.set_yticklabels(labels, fontsize=8)
        # print(ax.get_yticklabels())
        draw_fname = draw_file_base+"_fsid%d" % (fsid)
        plt.setp(ax.lines, color='k')
        ax.figure.savefig('docs/%s.svg' % draw_fname, bbox_inches="tight")
        ax.figure.clf()


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
    parser.add_argument('--subject-col', help="The path to the subject column file (only for wcv2)")
    parser.add_argument('--alpha-voting', default="max", choices=['max', 'min'],
                        help="The voting method to select alpha if there are several candidates")
    args = parser.parse_args()

    if args.falpha and args.fmeta and args.dataset and args.draw and args.data_path:
        workflow(falpha=args.falpha, draw_basename=args.draw, data_path=args.data_path, subject_col_fpath=args.subject_col,
                 fmeta=args.fmeta, dataset=args.dataset, title_case=(args.title_case.lower() == "title"),
                 alpha_voting=args.alpha_voting)
    else:
        parser.print_usage()
        parser.print_help()


if __name__ == "__main__":
    main()


