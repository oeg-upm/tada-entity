from experiment import *
from tadae.models import AnnRun, EntityAnn
from graph.type_graph import TypeGraph
import click
from commons import valpha
from collections import Counter
import pandas as pd
import pprint
import numpy as np
from commons.easysparql import get_children_of_class
from commons import ENDPOINT

NOT_FOUND_FNAME = "iswc_notfound.tsv"
INCORRECT_FNAME = "iswc_incorrect.tsv"
CORRECT_FNAME = "iswc_correct.tsv"
RESULTS_FNAME = "iswc_results.csv"
ALPHAS_FNAME = "iswc_alphas.tsv"
GOLD_FNAME = "goldstandard.csv"


def validate(alpha, fsid):
    tg = TypeGraph()  # dummy
    fs_funcs = range(len(tg.fs_funcs))
    f = open(meta_dir)
    reader = csv.reader(f)
    tot = 1  # only used for the progress bar
    ccc = 300

    unique_cols = 0  # The ones with high number of unique items
    multi_cols = 0  # The ones with a lot of duplicate data
    empty_cols = 0  # The ones with no results (from the unique cols)

    leaves = 0
    nonleaves = 0
    nonleave_nodes = []
    with click.progressbar(range(tot)) as bar:
        ann_runs = AnnRun.objects.filter(name__startswith="iswc_con")
        # ann_runs = AnnRun.objects.filter(name__startswith="iswc_col")
        for ann_run in ann_runs:
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
                cells = [c.text_value for c in ent_ann.cells]
                unique_cells = set(cells)

                is_entity = False
                if len(unique_cells)*1.0/len(cells) >= 0.95:
                    unique_cols +=1
                    is_entity = True
                else:
                    multi_cols +=1
                    is_entity = False
                print("%4d %4d (%2.4f) %s" % (len(cells), len(unique_cells), len(unique_cells)*1.0/len(cells), ann_run.name))
                if is_entity:
                    graph = annotator.load_graph(entity_ann=ent_ann)
                    results = annotator.score_graph(entity_ann=ent_ann, alpha=alpha, graph=graph, fsid=fs_funcs[fsid])[0:1]
                    if len(results) > 0:
                        append_results(results=results, ent_ann=ent_ann)
                        childs = get_children_of_class(class_name=results[0], endpoint=ENDPOINT)
                        if len(childs) == 0:
                            leaves += 1
                        else:
                            nonleaves += 1
                            nonleave_nodes.append(results[0])
                            #print results[0]
                    else:
                        empty_cols += 1
            bar.update(1)
            if ccc < 0:
                break
            else:
                ccc -= 1
    print("Unique: %d, Multi: %d, Empty: %d" % (unique_cols-empty_cols, multi_cols, empty_cols))
    print("Leaves: %d, Non: %d" % (leaves-empty_cols, nonleaves))
    print("Non-leaves: ")
    print(nonleave_nodes)


def append_results(results, ent_ann):
    # fname = ent_ann.ann_run.name[5:]
    # name = fname[:-4]
    # f = open("iswc_results.csv", "a")
    # from experiment import detect_subject_idx
    # idx = detect_subject_idx(fname=fname)
    col_str, fname = ent_ann.ann_run.name.split("__")
    col_idx = col_str[9:]
    name = fname[:-4]
    f = open(RESULTS_FNAME, "a")
    s = """"%s","%s","%s"\n""" % (name, col_idx, results[0])
    f.write(s)
    f.close()


def reverse_validation(alpha, fsid):
    """
    From the gold standard, look for the corresponding columns and check the
    precision and recall
    :param alpha:
    :param fsid:
    :return:
    """
    tg = TypeGraph()  # dummy
    fs_funcs = range(len(tg.fs_funcs))
    correct = 0
    incorrect = 0
    notfound = 0
    f = open(os.path.join("experiments/iswc_challenge", GOLD_FNAME))

    for line in f.readlines():
        if line.strip() == "":
            break
        fname, col_id_str, class_uri = line.replace('"', '').split(",")
        run_name = "iswc_con_%s__%s" % (col_id_str, fname)
        ann_runs = AnnRun.objects.filter(name__startswith=run_name)
        if len(ann_runs) == 0:
            print("not found first: "+run_name)
            notfound += 1
        elif len(ann_runs) == 1:
            ann_run = ann_runs[0]
            ent_ann = ann_run.entityann_set.all()[0]
            cells = [c.text_value for c in ent_ann.cells]
            # print("%3d  %s" % (len(cells), ann_run.name))
            graph = annotator.load_graph(entity_ann=ent_ann)
            results = annotator.score_graph(entity_ann=ent_ann, alpha=alpha, graph=graph, fsid=fs_funcs[fsid])
            # print("class_uri: %s" % class_uri)
            # print("results 0: %s" % results[0])
            # print("results 1: %s" % results[1])
            #results = results[0:1]
            if len(results) > 0:
                if class_uri.strip() == results[0].strip():
                    correct += 1
                else:
                    print("\nclass_uri: %s" % class_uri.strip())
                    print("results 0: %s" % results[0])
                    print("results 1: %s" % results[1])
                    print("%3d  %s" % (len(cells), ann_run.name))
                    incorrect += 1
            else:
                print("not found second: "+run_name)
                notfound += 1
        else:
            print("error, multiple occurences of "+fname)
            raise Exception("multiple occurences of"+fname)
    prec, recall, f1 = valpha.compute_scores(correct=correct, incorrect=incorrect, notfound=notfound)
    print("precision: %s, recall: %s, F1: %s" % (prec, recall, f1))
    print("correct: %d, incorrect: %d, notfound: %d" % (correct, incorrect, notfound))


def inspect():
    """
    Inspect
    :return:
    """
    ann_runs = AnnRun.objects.filter(name__startswith="iswc_con")
    # ann_runs = AnnRun.objects.filter(name__startswith="iswc_col")

    gold = []

    f = open(os.path.join("experiments/iswc_challenge",GOLD_FNAME))
    for line in f.readlines():
        fname, col_id_str, class_uri = line.replace('"', '').split(",")
        # fname = fname_with_ext[:-4]
        run_name = "iswc_con_%s__%s.csv" % (col_id_str, fname)
        # example_name = "iswc_con_%s__%s" % (col_id_str, fname)
        # ann_runs = AnnRun.objects.filter(name__startswith=example_name)
        ann_runs = AnnRun.objects.filter(name=run_name)
        if len(ann_runs) == 0:
            print("not found")
        else:
            print("\nrun name: <%s>" % run_name)
            print("act name: <%s>" % ann_runs[0].name)
        gold.append(run_name)

    print gold

    good_ones = []
    bad_ones = []

    for ann_run in ann_runs:
        ent_ann = ann_run.entityann_set.all()[0]
        noentities = 0
        withentities = 0

        for c in ent_ann.cells:
            if len(c.entities) > 0:
                withentities += 1
            else:
                noentities += 1

        p = (withentities*1.0)/(withentities+noentities)
        if ann_run.name in gold:
            good_ones.append(p)
        else:
            bad_ones.append(p)

        print("entities: %3d, no: %3d, (%.2f) - %s" % (withentities, noentities,
                                                       (withentities*1.0)/(withentities+noentities), ann_run.name))

    num_good = len(good_ones)
    num_bad = len(bad_ones)
    if num_good == 0:
        print("good ones: 0")
    else:
        print("good ones: %d (%f.3)" % (len(good_ones), sum(good_ones)*1.0/len(good_ones)))
    if num_bad == 0:
        print("bad ones: 0")
    else:
        print("bad ones: %d (%f.3)" % (len(bad_ones), sum(bad_ones)*1.0/len(bad_ones)))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == 'reverse':
            # reverse_validation(alpha=10 ** -5, fsid=2)
            reverse_validation(alpha=10 ** -3, fsid=3)

        if sys.argv[1] == 'inspect':
            inspect()
    else:
        #d                                           (camel) F1  Precision (no camel)
        # validate(ks=[1], alpha=10**-5, fsid=2) # 0.407	0.347
        #validate(ks=[1], alpha=10**-3, fsid=2)  # 0.407	0.347
        # validate(ks=[1], alpha=10**-1, fsid=2) # 0.407	0.347
        # validate(ks=[1], alpha=10**-1, fsid=1)   # 0.407	0.347
        # validate(ks=[1], alpha=10 ** -1, fsid=3) # 0.407	0.347
        # validate(ks=[1], alpha=2 * 10 ** -1, fsid=3) # 0.407	0.347

        #validate(alpha=10**-6, fsid=1)  # 0.31	0.265
        #validate(alpha=10**-5, fsid=1)  # 0.4	0.341
        #validate(alpha=10**-3, fsid=1)  # 0.179	0.153
        # validate(alpha=10**-1, fsid=1)

        # burned
        # validate(alpha=10**-1, fsid=2)  # 0.007	0.006
        # validate(alpha=10**-3, fsid=2)  # 0.234	0.2
        # validate(alpha=10 ** -6, fsid=2)  # 0.31	0.265

        # burned
        # validate(alpha=10**-5, fsid=3)  # 0.083	0.071
        #validate(alpha=10**-3, fsid=3) # 0.228	0.194
        # validate(alpha=10**-1, fsid=3) # 0.159	0.135

        #validate(alpha=10**-5, fsid=4) # 0.083	0.071
        #validate(alpha=10**-3, fsid=4) # 0.083	0.071
        #validate(alpha=10**-1, fsid=4)  # 0.179	0.153

        #validate(alpha=10**-5, fsid=5)  # 0.083	0.071
        # validate(alpha=10**-3, fsid=5)  # 0.083	0.071
        #validate(alpha=10**-1, fsid=5)  # 0.159	0.135
        # validate(alpha=0.2, fsid=5) # 0.193	0.165
        #validate(alpha=0.1, fsid=0)

        # After removing high duplicate items
        #validate(alpha=10 ** -3, fsid=2)  # 0.21    0.263    0.214	0.256
        validate(alpha=10 ** -5, fsid=2)  # -     0.485	0.581
        # validate(alpha=10 ** -6, fsid=2)  # - 0.364	0.462
        #validate(alpha=5 * 10 ** -6, fsid=2)  # -  0.323	0.41

        #validate(alpha=10 ** -3, fsid=3)  # 0.21	0.263  0.301	0.36