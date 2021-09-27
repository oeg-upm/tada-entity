import os
import argparse
import numpy as np
import pandas as pd
from experiments.alpha_analysis import get_classes
from annotator.annot import Annotator
from commons import ENDPOINT
from collections import Counter
import logging


def validate_annotation(class_uri, fname, col_id, fpath, title_case, alphas_fsid):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # # create console handler and set level to debug
    # handler = logging.StreamHandler()
    # handler.setLevel(logging.DEBUG)
    # logger.addHandler(handler)


    annotator = Annotator(endpoint=ENDPOINT, title_case=title_case, num_of_threads=3, logger=logger,
                               class_prefs=["http://dbpedia.org/ontology/", "http://www.w3.org/2002/07/owl#Thing"])
    annotator.annotate_table(file_dir=fpath, subject_col_id=col_id)
    d = dict()
    for fsid in range(1, 6):
        d[fsid] = dict()
        for a_attr in ['alpha_mean', 'alpha_median']:
            if fname in alphas_fsid[fsid][class_uri]:
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
        # print("measure_class_accuracy> fname: %s" % fname)
        fpath = os.path.join(data_dir, fname)
        fname_acc = validate_annotation(class_uri=class_uri, fname=fname, fpath=fpath, col_id=fnames_colid[fname],
                                        title_case=title_case, alphas_fsid=alphas_fsid)
        # print("fname acc: ")
        # print(fname_acc)
        for fsid in fname_acc:
            if fsid not in acc:
                acc[fsid] = {
                    'alpha_mean': [],
                    'alpha_median': []
                }
            acc[fsid]['alpha_mean'].append(fname_acc[fsid]['alpha_mean'])
            acc[fsid]['alpha_median'].append(fname_acc[fsid]['alpha_median'])
    # print("measure_class_accuracy> acc: ")
    # print(acc)
    return acc


def run_with_class(class_uri, alphas_per_file, title_case, data_dir):
    # Computer alphas mean and median for the k-fold test
    alphas = []
    fname_colids = dict()
    for fsid in range(1, 6):
        if class_uri not in alphas_per_file[fsid]:
            print("class <%s> is not in the alpha dict: " % class_uri)
            continue
        fnames = list(alphas_per_file[fsid][class_uri])
        if len(fnames) < 2:
            del alphas_per_file[fsid][class_uri]
            continue
        for f in fnames:
            alphas = [a for a in alphas_per_file[fsid][class_uri][f]]
        for i, fname in enumerate(fnames):
            in_alphas = alphas[0:i] + alphas[i+1:]
            alpha_mean = np.mean(in_alphas)
            alpha_median = np.median(in_alphas)
            alphas_per_file[fsid][class_uri][fname]["alpha_mean"] = alpha_mean
            alphas_per_file[fsid][class_uri][fname]["alpha_median"] = alpha_median
            fname_colids[fname] = alphas_per_file[fsid][class_uri][fname]['col_id']
    # predict and computer accuracy of the predicted alpha
    acc = measure_class_accuracy(class_uri=class_uri, fnames_colid=fname_colids, data_dir=data_dir,
                              alphas_fsid=alphas_per_file, title_case=title_case)
    print("Class Accuracy: ")
    print(acc)
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
    :return:
    """
    acc = dict()
    for cls in classes:
        run_with_class(cls, alphas_fsid, title_case, data_dir)
        break  # TEST
        mean_acc = Counter(mean_res)[True] * 1.0 / len(mean_res)
        median_acc = Counter(median_res)[True] * 1.0 / len(median_res)
        acc[cls] = {
            'mean': mean_acc,
            'median': median_acc,
            'num': len(median_res)
        }
        # print(acc[cls])
        break  # TEST
    return acc


def compute_k_fold_alpha_accuracy(falpha, data_dir, classes_dict, classes_list):
    df_all = pd.read_csv(falpha)
    alphas_fsid = dict()
    for fsid in range(1, 6):
        df = df_all[df_all.fsid == fsid]
        alphas_fsid[fsid] = aggregate_alpha_per_class_per_file(df, classes_dict)



    acc = run_with_pred_alpha(alphas_fsid, title_case=True, data_dir=data_dir, classes=classes_list)
    # draw_diagram(data)
    # save_accuracy(acc, fsid, True)


def save_accuracy(acc, fsid, title_case):
    lines = []
    title_str = "original"
    if title_case:
        title_str = "title"
    for cls in acc:
        line = "%s,%.2f,%.2f,%d" % (cls, acc[cls]['mean'], acc[cls]['median'], acc[cls]['num'])
        lines.append(line)
    with open("wcv2_k_fold_alpha_fsid%d_%s.csv" % (fsid, title_str), "w") as f:
        f.write("\n".join(lines))


def aggregate_alpha_per_class_per_file(df, classes):
    """
    :param df: DataFrame of a meta file
    :param classes: a dict of fnames and their classes
    :return:
    """
    """fname,colid,fsid,from_alpha,to_alpha"""
    d = dict()
    for idx, row in df.iterrows():
        c = classes[row['fname']]
        if c not in d:
            d[c] = dict()
        print(row)
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


def workflow(falpha, fmeta, data_dir):
    """
    :param falpha:
    :param fmeta:
    :return:
    """
    classes_dict = get_classes(fmeta)
    classes_list = get_classes_list(classes_dict=classes_dict)
    compute_k_fold_alpha_accuracy(falpha, classes_dict, data_dir, classes_list)


def main():
    """
    Parse the arguments
    :return:
    """
    parser = argparse.ArgumentParser(description='Alpha Evaluator')
    parser.add_argument('falpha', help="The path to the alpha results file.")
    parser.add_argument('fmeta', help="The path to the meta file which contain the classes.")
    parser.add_argument('data_dir', help="The path to the csv files")
    parser.print_usage()
    parser.print_help()
    args = parser.parse_args()
    workflow(args.falpha, args.fmeta, args.data_dir)


if __name__ == "__main__":
    main()
