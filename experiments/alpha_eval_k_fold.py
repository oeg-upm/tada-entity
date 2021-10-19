"""
This script evaluate the prediction of alpha values per class using k-fold
"""
import os
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
from experiments.alpha_analysis import get_classes, shorten_uri
from annotator.annot import Annotator
from commons import ENDPOINT
from collections import Counter
import logging

import matplotlib.pyplot as plt


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


def measure_class_accuracy(class_uri, data_dir, fnames_colid, alphas_fsid, title_case):
    acc = dict()
    for fname in fnames_colid:
        fpath = os.path.join(data_dir, fname)
        fname_acc = validate_annotation(class_uri=class_uri, fname=fname, fpath=fpath, col_id=fnames_colid[fname],
                                        title_case=title_case, alphas_fsid=alphas_fsid)
        for fsid in fname_acc:
            if fsid not in acc:
                acc[fsid] = {
                    'alpha_mean': [],
                    'alpha_median': []
                }
            if fsid in fname_acc and 'alpha_mean' in fname_acc[fsid]:
                acc[fsid]['alpha_mean'].append(fname_acc[fsid]['alpha_mean'])
                acc[fsid]['alpha_median'].append(fname_acc[fsid]['alpha_median'])
            else:
                print("measure_class_accuracy> No optimal alpha for fsid: %d, fname: %s" % (fsid, fname))
    # print("measure_class_accuracy> acc for class %s: " % class_uri)
    # print(acc)
    return acc


def run_with_class(class_uri, alphas_per_file, title_case, data_dir):
    # Computer alphas mean and median for the k-fold test
    fname_colids = dict()
    for fsid in range(1, 6):
        if class_uri not in alphas_per_file[fsid]:
            print("run_with_class> class <%s> is not in the alpha dict <not an error>" % class_uri)
            continue
        fnames = list(alphas_per_file[fsid][class_uri])
        if len(fnames) < 2:
            del alphas_per_file[fsid][class_uri]
            print("run_with_class> class <%s> with less than 2 files with optimal alphas" % class_uri)
            continue

        alphas = [alphas_per_file[fsid][class_uri][fname]['alpha'] for fname in alphas_per_file[fsid][class_uri]]
        for i, fname in enumerate(fnames):
            # alphas = [alphas_per_file[fsid][class_uri][fname]['alpha'] for fname in alphas_per_file[fsid][class_uri]]
            in_alphas = alphas[0:i] + alphas[i+1:]
            alpha_mean = np.mean(in_alphas)
            alpha_median = np.median(in_alphas)
            alphas_per_file[fsid][class_uri][fname]["alpha_mean"] = alpha_mean
            alphas_per_file[fsid][class_uri][fname]["alpha_median"] = alpha_median
            fname_colids[fname] = alphas_per_file[fsid][class_uri][fname]['col_id']
    # predict and computer accuracy of the predicted alpha
    acc = measure_class_accuracy(class_uri=class_uri, fnames_colid=fname_colids, data_dir=data_dir,
                              alphas_fsid=alphas_per_file, title_case=title_case)
    return acc
    # acc = dict()
    # for fname in fname_colids:
    #     f_acc = measure_file_accuracy(class_uri=class_uri, fname=fname, col_id=fname_colids[fname], data_dir=data_dir,
    #                           alphas_fsid=alphas_per_file)
    #     acc[fname] = f_acc
    # return acc
    # fpath = os.path.join(data_dir, fname)
        # fname_acc = validate_annotation(class_uri=class_uri, fname=fname, fpath=fpath, col_id=fname_colids[fname],
        #                                 title_case=title_case, alphas_fsid=alphas_per_file)
        # for fsid in fname_acc:
        #     if fsid not in acc:
        #         acc[fsid] = {class_uri: {
        #             'alpha_mean': [],
        #             'alpha_median': []
        #         }}
        #     acc[fsid]['alpha_mean'].append(fname_acc[fsid]['alpha_mean'])
        #     acc[fsid]['alpha_median'].append(fname_acc[fsid]['alpha_median'])
    # print(acc)
    # return acc

    # for fsid in range(1, 6):
    #     fnames = list(alphas_per_file[fsid][class_uri])
    #     if len(fnames) < 2:
    #         # Ignore somehow
    #         continue
    #     for i, fname in enumerate(fnames):
    #         in_alphas = alphas[0:i] + alphas[i+1:]
    #         alpha_mean = np.mean(in_alphas)
    #         alpha_median = np.median(in_alphas)
    #         fpath = os.path.join(data_dir, fname)
    #         mea = validate_annotation(class_uri=class_uri, col_id=col_ids[i], fpath=fpath, title_case=title_case, alpha=alpha_mean, fsid=fsid)
    #         med = validate_annotation(class_uri=class_uri, col_id=col_ids[i], fpath=fpath, title_case=title_case, alpha=alpha_median, fsid=fsid)
    #         median_res.append(med)
    #         mean_res.append(mea)
    #     return mean_res, median_res

# def run_with_class(class_uri, alphas_per_file, title_case, data_dir, fsid):
#     alphas = []
#     fnames = []
#     col_ids = []
#     mean_res = []
#     median_res = []
#     for fname in alphas_per_file:
#         a = alphas_per_file[fname]['alpha']
#         if a >= 0:
#             fnames.append(fname)
#             alphas.append(a)
#             col_ids.append(alphas_per_file[fname]['col_id'])
#     if len(alphas) < 2:
#         return []
#     for i in range(len(fnames)):
#         in_alphas = alphas[0:i] + alphas[i+1:]
#         alpha_mean = np.mean(in_alphas)
#         alpha_median = np.median(in_alphas)
#         fpath = os.path.join(data_dir, fnames[i])
#         mea = validate_annotation(class_uri=class_uri, col_id=col_ids[i], fpath=fpath, title_case=title_case, alpha=alpha_mean, fsid=fsid)
#         med = validate_annotation(class_uri=class_uri, col_id=col_ids[i], fpath=fpath, title_case=title_case, alpha=alpha_median, fsid=fsid)
#         median_res.append(med)
#         mean_res.append(mea)
#     return mean_res, median_res


def run_with_pred_alpha(alphas_fsid, title_case, data_dir, classes):
    """
    :param alphas_fsid: alpha dict
    :param title_case: bool
    :param data_dir: the path to the csv files
    :param classes: list of classes
    :return: dict
        {
            fsid: {
                cls1: {
                    'alpha_mean': <>,
                    'alpha_median': <>
                }
            }
        }
    """
    acc = dict()
    for fsid in range(1, 6):
        acc[fsid] = dict()
    for cls in classes:
        acc_cls = run_with_class(cls, alphas_fsid, title_case, data_dir)
        for fsid in range(1, 6):
            acc[fsid][cls] = dict()
            for a_attr in ['alpha_mean', 'alpha_median']:
                # Because some files does not have optimal alphas for certain fsid
                if fsid in acc_cls and a_attr in acc_cls[fsid]:
                    bool_counter = Counter(acc_cls[fsid][a_attr])
                    corrs = 0
                    if True in bool_counter:
                        corrs = bool_counter[True]
                    if len(acc_cls[fsid][a_attr]) == 0:
                        acc[fsid][cls][a_attr] = 0
                        print("run_with_pred_alpha> class: %s, fsid: %d, empty alphas (not an error)" % (cls, fsid))
                    else:
                        acc[fsid][cls][a_attr] = corrs * 1.0 / len(acc_cls[fsid][a_attr])
                    # acc[fsid][cls][a_attr] = Counter(acc_cls[fsid][a_attr])[True] * 1.0 / len(acc_cls[fsid][a_attr])
                    acc[fsid][cls]['num'] = len(acc_cls[fsid][a_attr])
                else:
                    print("run_with_pred_alpha> class: %s, fsid: %d, does not have an optimal alpha (not an error)" % (cls, fsid))

    return acc


def compute_k_fold_alpha_accuracy(falpha, data_dir, fnames_and_classes, classes_list, title_case):
    df_all = pd.read_csv(falpha)
    alphas_fsid = dict()
    for fsid in range(1, 6):
        df = df_all[df_all.fsid == fsid]
        alphas_fsid[fsid] = aggregate_alpha_per_class_per_file(df, fnames_and_classes)

    acc = run_with_pred_alpha(alphas_fsid, title_case=title_case, data_dir=data_dir, classes=classes_list)
    return acc


def save_accuracy(acc, title_case, dataset):
    lines = []
    title_str = "original"
    if title_case:
        title_str = "title"
    line = "class,fsid,mean,median,num"
    lines.append(line)
    for fsid in range(1, 6):
        for cls in acc[fsid]:
            if fsid in acc and cls in acc[fsid] and 'alpha_mean' in acc[fsid][cls]:
                line = "%s,%d,%.2f,%.2f,%d" % (cls, fsid, acc[fsid][cls]['alpha_mean'], acc[fsid][cls]['alpha_median'],
                                               acc[fsid][cls]['num'])
                lines.append(line)
    fname = "%s_k_fold_alpha_%s.csv" % (dataset, title_str)
    with open(fname, "w") as f:
        f.write("\n".join(lines))


def aggregate_alpha_per_class_per_file(df, fnames_and_classes):
    """
    :param df: DataFrame of a meta file (filtered to have the same fsid)
    :param fnames_and_classes: a dict of fnames (keys) and their classes (vals)
    :return:
    """
    """fname,colid,fsid,from_alpha,to_alpha"""
    d = dict()
    for idx, row in df.iterrows():
        c = fnames_and_classes[row['fname']]
        if c not in d:
            d[c] = dict()
        if row['from_alpha'] >= 0:
            d[c][row['fname']] = {
                'alpha': (row['from_alpha'] + row['to_alpha'])/2,
                'col_id': row['colid']
            }
    return d


def get_classes_list(classes_dict):
    classes = []
    for fname in classes_dict:
        classes.append(classes_dict[fname])
    return list(set(classes))


def workflow(falpha, fmeta, data_dir, title_case, dataset):
    """
    :param falpha:
    :param fmeta:
    :param data_dir: the path to the csv data
    :param title_case: bool
    :param dataset: str  wcv1, or wcv2, or ..
    :return:
    """
    fnames_and_classes = get_classes(fmeta, dataset)
    classes_list = get_classes_list(fnames_and_classes)
    acc = compute_k_fold_alpha_accuracy(falpha, data_dir, fnames_and_classes, classes_list, title_case)
    save_accuracy(acc, title_case, dataset)


def generate_diagram(fscores, title_case, draw_file_base):
    """
    :param fscores: path to scores file
    :param title_case: bool
    :param draw_file_base: base of the diagram
    :return: None
    """
    if title_case:
        title_txt = "title"
    else:
        title_txt = "original"
    df_all = pd.read_csv(fscores)
    for fsid in range(1, 6):
        df = df_all[df_all.fsid == fsid]
        df = df[df.num > 0]
        # for idx, row in df.iterrows():
        #     row['class'] = shorten_uri(row['class'])
        rows = []
        for idx, df_row in df.iterrows():
            for a_attr in ['mean', 'median']:
                print("df_row")
                print(df_row)
                r = [shorten_uri(df_row['class']), df_row[a_attr], a_attr]
                rows.append(r)
        data = pd.DataFrame(rows, columns=['Class', 'Accuracy', 'Aggr'])
        # ax = sns.boxplot(x="Alpha", y="Class",
        #                  hue="Aggr",
        #                  data=data, linewidth=1.0,
        #                  # palette="colorblind",
        #                  palette="Spectral",
        #                  # palette="pastel",
        #                  dodge=True,
        #                  # palette="ch:start=.2,rot=-.3",
        #                  orient="h",
        #                  flierprops=dict(markerfacecolor='0.50', markersize=2))

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
        draw_fname = draw_file_base+"_fsid%d_%s" % (fsid, title_txt)  # "wcv2_alpha_k_fold_fsid%d_title.csv" % fsid
        # draw_fname = "wcv2_alpha_k_fold_fsid%d_title.csv" % fsid
        plt.setp(ax.lines, color='k')
        ax.figure.savefig('docs/%s.svg' % draw_fname, bbox_inches="tight")
        ax.figure.clf()


def main():
    """
    Parse the arguments
    :return:
    """
    parser = argparse.ArgumentParser(description='Alpha Evaluator')
    parser.add_argument('--falpha', help="The path to the alpha results file.")
    parser.add_argument('--fmeta', help="The path to the meta file which contain the classes.")
    parser.add_argument('--data_dir', help="The path to the csv files")
    parser.add_argument('--dataset', choices=["wcv1", "wcv2", "st19-r1",  "st19-r2", "st19-r3", "st19-r4"],
                        help="The name of the dataset as the meta file differ for each")
    parser.add_argument('--title', choices=["true", "false"], default="true",
                        help="Whether to force title case or use the original case")
    parser.add_argument('--draw', help="The base name for the diagram file (without the extension)")
    parser.add_argument('--fscores', help="The path to the k-fold scores file")
    args = parser.parse_args()

    if args.falpha and args.fmeta and args.data_dir and args.title and args.dataset:
        workflow(args.falpha, args.fmeta, args.data_dir, args.title.lower() == "true", dataset=args.dataset)
    elif args.draw and args.title and args.fscores:
        generate_diagram(fscores=args.fscores, title_case=(args.title.lower() == "true"), draw_file_base=args.draw)
    else:
        parser.print_usage()
        parser.print_help()


if __name__ == "__main__":
    main()
