from experiment import *
from tadae.models import AnnRun, EntityAnn
from graph.type_graph import TypeGraph
import click
from commons import valpha
import pprint


NOT_FOUND_FNAME = "wc_v1_notfound.tsv"
INCORRECT_FNAME = "wc_v1_incorrect.tsv"
CORRECT_FNAME = "wc_v1_correct.tsv"
RESULTS_FNAME = "wc_v1_results.tsv"
ALPHAS_FNAME = "wc_v1_alphas.tsv"


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
    valpha.prepare_report_files(not_found_fname=NOT_FOUND_FNAME, incorrect_fname=INCORRECT_FNAME,
                                correct_fname=CORRECT_FNAME, alphas_fname=ALPHAS_FNAME)
    tg = TypeGraph()  # dummy
    fs_funcs = range(len(tg.fs_funcs))
    f = open(meta_dir)
    reader = csv.reader(f)
    tot = 233  # only used for the progress bar
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
    #ccc = 5
    ccc = 10000
    with click.progressbar(range(tot)) as bar:
        for line in reader:
            file_name, concept = get_file_and_concept_from_line(line)
            correct_type = line[2].strip()
            csv_fname = get_csv_file(concept, file_name)
            # print("%d csv_fname: %s"%(corr+inco, csv_fname))
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
                    results_bool = valpha.validate_ent_ann(ent_ann=ent_ann, fsid=fsid, ks=kss,
                                                           correct_type=correct_type,
                                                           for_all_alphas=for_all_alphas,
                                                           not_found_fname=NOT_FOUND_FNAME,
                                                           correct_fname=CORRECT_FNAME, incorrect_fname=INCORRECT_FNAME,
                                                           alphas_fname=ALPHAS_FNAME)
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


if __name__ == "__main__":
    ks = [1, 3, 5, 10]
    if len(sys.argv) == 2 and sys.argv[1] == 'alpha':
        print("Note that all values of alphas will be reported")
        validate(ks=ks, for_all_alphas=True)
        valpha.alpha_stat(ks=ks, alphas_fname=ALPHAS_FNAME)
    elif len(sys.argv) == 2 and sys.argv[1] == 'alphastat':
        valpha.alpha_stat(ks=ks, alphas_fname=ALPHAS_FNAME)
    else:
        validate(ks=ks, for_all_alphas=False)
