from experiment import *
from tadae.models import AnnRun, EntityAnn
from graph.type_graph import TypeGraph
import click
from commons import valpha
from collections import Counter
import pandas as pd
import pprint
import numpy as np
# np.set_printoptions(suppress=True)
# np.set_printoptions(suppress=True,
#    formatter={'float_kind':'{:.10f}'.format})


NOT_FOUND_FNAME = "og_notfound.tsv"
INCORRECT_FNAME = "og_incorrect.tsv"
CORRECT_FNAME = "og_correct.tsv"
RESULTS_FNAME = "og_results.tsv"
ALPHAS_FNAME = "og_alphas.tsv"


def prepare_report_files():
    f = open(NOT_FOUND_FNAME, "w")
    f.write("file name\n")
    f.close()
    f = open(INCORRECT_FNAME, "w")
    f.write("file name\tfs\tk\n")
    f.close()
    f = open(CORRECT_FNAME, "w")
    f.write("file name\tfs\tk\n")
    f.close()
    f = open(ALPHAS_FNAME, "w")
    f.write("file name\tfs\tk\talpha\n")
    f.close()


def report_incorrect(fname, fsid, k):
    f = open(INCORRECT_FNAME, "a")
    f.write("%s\t%s\t%s\n" % (fname, str(fsid), str(k)))
    f.close()


def report_not_found(fname):
    f = open(NOT_FOUND_FNAME)
    t = f.read()
    f.close()
    if fname not in t:
        f = open(NOT_FOUND_FNAME, "a")
        f.write(fname+"\n")
        f.close()


def report_correct(fname, fsid, k):
    f = open(CORRECT_FNAME, "a")
    f.write("%s\t%s\t%s\n" % (fname, str(fsid), str(k)))
    f.close()


def report_alphas(fname, fsid, k, alpha):
    f = open(ALPHAS_FNAME, "a")
    f.write("%s\t%s\t%s\t%f\n" % (fname, str(fsid), str(k), alpha))
    f.close()


def validate(ks, for_all_alphas):
    prepare_report_files()
    tg = TypeGraph()  # dummy
    fs_funcs = range(len(tg.fs_funcs))
    f = open(meta_dir)
    reader = csv.reader(f)
    tot = 12  # only used for the progress bar
    kss = sorted(ks)  # kssorted to it will be faster to validate for multiple k values
    results = {}
    for fsid in fs_funcs:
        if fsid not in results:
            results[fsid] = {}
        for k in kss:
            if k not in results[fsid]:
                results[fsid][k] = {}
            results[fsid][k] = {"correct": 0, "incorrect": 0, "notfound": 0}
    # if True:
    ccc = 20
    #ccc = -1
    with click.progressbar(range(tot)) as bar:
        for line in reader:
            csv_fname, concept = line[0], line[1]
            correct_type = prefix+concept.strip()
            ann_run = AnnRun.objects.get(name=csv_fname)
            ent_anns = ann_run.entityann_set.all()

            if len(ent_anns) != 1:
                error_msg = """validate> ann run id=%s has multiple entity annotations """ % str(ann_run.id)
                print(error_msg)
                raise Exception(error_msg)

            elif ann_run.status != 'Annotation is complete':
                error_msg = """validate> ann run id=%s is not completed successfully""" % str(ann_run.id)
                print(error_msg)
                raise Exception(error_msg)

            else:
                ent_ann = ent_anns[0]
                for fsid in fs_funcs:
                    results_bool = validate_ent_ann(ent_ann=ent_ann, fsid=fsid, ks=kss, correct_type=correct_type,
                                                    for_all_alphas=for_all_alphas)
                    for k in results_bool.keys():
                        if results_bool[k] == "CORRECT":
                            results[fsid][k]["correct"] += 1
                        elif results_bool[k] == "INCORRECT":
                            results[fsid][k]["incorrect"] += 1
                        elif results_bool[k] == "NOTFOUND":
                            results[fsid][k]["notfound"] += 1
                        else:
                            error_msg = "validate> the annotation result is not recognized"
                            print(error_msg)
                            raise Exception(error_msg)

            bar.update(1)
            if ccc < 0:
                break
            else:
                ccc -=1
                # print("\n\n==================== %d ======================\n\n" % ccc)

    print_results(results, fs_funcs, kss)


def compute_scores(correct, incorrect, notfound):
    """
    :param correct:
    :param incorrect:
    :param notfound:
    :return:
    """
    # print("correct: %d, incorrect: %d, notfound: %d" % (correct, incorrect, notfound))

    try:
        precision_val = correct*1.0 / (correct+incorrect)
        precision = "%.4f" % precision_val
    except Exception as e:
        precision = "n/a"

    try:
        recall_val = correct*1.0 / (correct+notfound)
        recall = "%.4f" % recall_val
    except Exception as e:
        recall = "n/a"

    try:
        f1 = 2 * precision_val * recall_val / (precision_val+recall_val)
        f1 = "%.4f" % f1
    except Exception as e:
        f1 = "n/a"

    return precision, recall, f1


def print_results(results, fs_funcs, kss):
    f = open(RESULTS_FNAME, "w")
    f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % ("fs", "k", "correct", "incorrect", "not found", "precision", "recall", "F1"))
    for fsid in fs_funcs:
        for k in kss:
            precision, recall, f1 = compute_scores(results[fsid][k]["correct"], results[fsid][k]["incorrect"],
                                                   results[fsid][k]["notfound"])
            f.write("%d\t%d\t%d\t%d\t%d\t%s\t%s\t%s\n" % (fsid, k, results[fsid][k]["correct"],
                                                       results[fsid][k]["incorrect"],results[fsid][k]["notfound"],
                                                       precision ,
                                                       recall ,
                                                       f1
                                                    ))
    f.close()
    print("%5s | %5s | %10s | %10s | %10s | %10s | %10s | %10s" % ("fs", "k", "correct", "incorrect", "not found", "precision", "recall", "F1"))
    for fsid in fs_funcs:
        for k in kss:
            precision, recall, f1 = compute_scores(results[fsid][k]["correct"], results[fsid][k]["incorrect"],
                                                   results[fsid][k]["notfound"])
            print("%5d | %5d | %10d | %10d | %10d | %10s | %10s | %10s" % (fsid, k, results[fsid][k]["correct"],
                                                       results[fsid][k]["incorrect"], results[fsid][k]["notfound"],
                                                       precision,
                                                       recall,
                                                       f1))


def validate_ent_ann(ent_ann, fsid, ks, correct_type, for_all_alphas):
    """
    :param ent_ann:
    :param fsid:
    :param ks: a list of k values that should be sorted in a ascending order
    :param correct_type:
    :param for_all_alphas: bool (if true, then it will check alphas that yields a good score)
    :return:
        {
            "k_1": bool,
            "k_2": bool,
            ....
        }
    """
    alphas = [0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.1, 0.05, 0.01, 0.005, 0.001, 0.0005, 0.0001, 0.00005, 0.00001]
    k_id = len(ks)-1  # to start with the largest k
    k = ks[k_id]
    d = {}
    for alpha in alphas:
        if for_all_alphas:
            k_id = len(ks) - 1  # to start with the largest k
            k = ks[k_id]
        graph = annotator.load_graph(entity_ann=ent_ann)
        results = annotator.score_graph(entity_ann=ent_ann, alpha=alpha, graph=graph, fsid=fsid)[0:k]

        if results == []:
            for k in ks:
                d[k] = "NOTFOUND"
                report_not_found(fname=ent_ann.ann_run.name)
            return d

        while correct_type in results:
            d[k] = "CORRECT"
            report_correct(fname=ent_ann.ann_run.name, fsid=fsid, k=k)
            if for_all_alphas:
                report_alphas(fname=ent_ann.ann_run.name, fsid=fsid, k=k, alpha=alpha)
            if k_id == 0:  # no more values of k left
                k_id = -1
                break
            else:
                k_id -= 1
                k = ks[k_id]  # new k
                results = results[0:k]

        if k_id < 0 and not for_all_alphas:
            break

    while k_id >= 0:  # there are some values of k that is smaller than k
        d[k] = "INCORRECT"
        report_incorrect(fname=ent_ann.ann_run.name, fsid=fsid, k=k)
        k_id -= 1
        k = ks[k_id]
    return d


if __name__ == "__main__":
    ks = [1, 3, 5, 10]
    if len(sys.argv) == 2 and sys.argv[1] == 'alpha':
        print("Note that all values of alphas will be reported")
        validate(ks=ks, for_all_alphas=True)

    elif len(sys.argv) == 2 and sys.argv[1] == 'alphastat':
        valpha.alpha_stat(ks=ks, alphas_fname=ALPHAS_FNAME)
    else:
        validate(ks=ks, for_all_alphas=False)
