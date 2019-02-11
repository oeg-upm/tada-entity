from experiment import *
from tadae.models import AnnRun, EntityAnn
from graph.type_graph import TypeGraph
import click


def validate(k, fsid):
    # from annotator import load_graph, score_graph, get_nodes, get_edges
    f = open(meta_dir)
    reader = csv.reader(f)
    corr = 0
    inco = 0
    tot = 237  # only used for the progress bar
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
                if validate_ent_ann(ent_ann=ent_ann, fsid=fsid, k=k, correct_type=correct_type):
                # # graph = annotator.load_graph(entity_ann=ent_ann)
                # # results = annotator.score_graph(entity_ann=ent_ann, alpha=alpha, graph=graph, fsid=fsid)[0:k]
                # if correct_type in results:
                    corr += 1
                else:
                    inco += 1
            bar.update(1)
    print("fsid: %d, correct: %d, incorrect: %d, precision: %.2f%%" % (fsid, corr, inco, (corr*100.0/(corr+inco)) ))


def validate_ent_ann(ent_ann, fsid, k, correct_type):
    alphas = [0.1, 0.05, 0.01, 0.005, 0.001, 0.0005, 0.0001]
    for alpha in alphas:
        graph = annotator.load_graph(entity_ann=ent_ann)
        results = annotator.score_graph(entity_ann=ent_ann, alpha=alpha, graph=graph, fsid=fsid)[0:k]
        if correct_type in results:
            return True
    return False


def validate_all():
#    ks = [1, 3, 5, 10]
    ks = [1]
    tg = TypeGraph()
    fs_funcs = range(len(tg.fs_funcs))
    for k in ks:
        for fsid in fs_funcs:
            validate(k=k, fsid=fsid)


if __name__ == "__main__":
        validate_all()