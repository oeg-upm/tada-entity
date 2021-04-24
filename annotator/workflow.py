import argparse
import json
import os
import time
import logging
import random
import traceback
import string
import math
import pandas as pd

from tadae.settings import MODELS_DIR, LOG_DIR
from tadae.models import AnnRun, EntityAnn, Cell, CClass, Entity


from multiprocessing import Process, Lock, Pipe
# from PPool.Pool import Pool
from TPool.TPool import Pool


from graph.type_graph import TypeGraph
from commons.logger import set_config
from commons.easysparql import get_entities, get_classes, get_entities_and_classes
from commons.easysparql import get_parents_of_class
from commons.easysparql import get_classes_subjects_count
from commons.tgraph import TGraph

logger = set_config(logging.getLogger(__name__), logdir=os.path.join(LOG_DIR, 'tadae.log'))

MAX_NUM_PROCESSES = 1

USE_DB = True
g_tgraph = None
g_cell_ent_class = None
g_class_ancestors = None


def detect_subject_col(csv_file_dir):
    """
    :param csv_file_dir:
    :return: the index of the entity column, or -1 if it is can't be found
    """
    return 0  # at the moment we assume that the entity column is the first column


def build_graph_from_nodes(graph, nodes_dict):
    """
    :param graph:
    :param nodes_dict: each node (key) contains a list of its parents
    :return:
    """
    logger.debug("adding nodes")
    # add nodes
    for node in nodes_dict:
        graph.add_v(node, None)

    logger.debug("all nodes are added")
    # add edges

    logger.debug("adding edges")
    for node in nodes_dict:
        for p in nodes_dict[node]:
            graph.add_e(p, node)
    logger.debug("all edges are added")
    graph.build_roots()
    logger.debug("roots are built\n\n***\n\n\n\n\n***********")
    # graph.draw("graph-pre.gv")
    logger.debug("will break the cycles")
    graph.break_cycles(log_path=LOG_DIR)
    logger.debug("cycles are broken")


# Old coverage
# def compute_coverage_score_for_graph(entity_ann, graph):
#     for cell in entity_ann.cells:
#         if len(cell.entities) == 0:
#             e_score = 0
#         else:
#             e_score = 1.0 / len(cell.entities)
#
#         for entity in cell.entities:
#             if len(entity.classes) == 0:
#                 c_score = 0
#             else:
#                 c_score = 1.0 / len(entity.classes)
#             for cclass in entity.classes:
#                 n = graph.find_v(cclass.cclass)
#                 if n is None:
#                     print "couldn't find %s" % cclass.cclass
#                 n.coverage_score += c_score


# New coverage
def compute_coverage_score_for_graph(entity_ann, graph):
    for cell in entity_ann.cells:
        if len(cell.entities) == 0:
            e_score = 0
        else:
            e_score = 1.0 / len(cell.entities)
        d = {
        }
        for entity in cell.entities:
            if len(entity.classes) == 0:
                c_score = 0
            else:
                c_score = 1.0 / len(entity.classes)
            for cclass in entity.classes:
                if cclass.cclass not in d:
                    d[cclass.cclass] = []
                d[cclass.cclass].append(c_score*e_score)

        for curi in d.keys():
            curi_cov = sum(d[curi])*1.0/len(d[curi])
            n = graph.find_v(curi)
            if n is None:
                print("couldn't find %s" % curi)
            n.coverage_score += curi_cov
        del d


def v_writer_func(visited, pipe):
    v = None
    while True:
        v = pipe.recv()
        if v == 1:
            pipe.send(visited)
        else:
            visited = v


def count_classes_writer_func(pipe):
    d = {}
    while True:
        v = pipe.recv()
        if v == 1:
            pipe.send(d)
        else:
            print("count_classes_writer_func: ")
            print(v)
            l = list(v.keys())
            k = l[0]
            # k = v.keys()[0]
            d[k] = v[k]


def count_classes_func(c, endpoint, lock, pipe):
    d = get_classes_subjects_count(c, endpoint)
    lock.acquire()
    pipe.send(d)
    lock.release()


def count_classes(classes, endpoint):
    """
    count classes from a given endpoint using a pool of processes
    :param classes:
    :param endpoint:
    :return:
    """
    print("in count classes")
    from multiprocessing import Process, Lock, Pipe

    lock = Lock()
    a_end, b_end = Pipe()

    print("in count classes> the writer process")
    writer_process = Process(target=count_classes_writer_func, args=(a_end,))
    writer_process.start()

    print("in count classes> preparing the pool")
    param_list = [([c], endpoint, lock, b_end) for c in classes]
    pool = Pool(max_num_of_threads=MAX_NUM_PROCESSES, func=count_classes_func, params_list=param_list)
    # pool = Pool(max_num_of_processes=MAX_NUM_PROCESSES, func=count_classes_func, params_list=param_list)
    pool.run()
    print("pool run if finished")
    print("sending 1")
    b_end.send(1)
    print("waiting to receive")
    d = b_end.recv()
    print("received")
    writer_process.terminate()
    print("in count classes> returns :%s" % str(d))
    return d


def remove_nodes(entity_ann, classes):
    for cell in entity_ann.cells:
        for entity in cell.entities:
            for cclass in entity.classes:
                if cclass.cclass in classes:
                    print("removing lonely node: %s" % cclass.cclass)
                    CClass.objects.get(cclass=cclass.cclass, entity=entity).delete()


def remove_empty(entity_ann):
    for cell in entity_ann.cells:
        for entity in cell.entities:
            if len(entity.classes) == 0:
                Entity.objects.get(id=entity.id).delete()


def remove_noise_entities(entity_ann):
    for cell in entity_ann.cells:
        if len(cell.entities) >= 2:
            max_num = 0
            for entity in cell.entities:
                num_classes = len(entity.classes)
                if num_classes > max_num:
                    max_num = num_classes
            num_classes_limit = math.sqrt(max_num)
            for entity in cell.entities:
                if len(entity.classes) < num_classes_limit:
                    logger.debug("remove_noise: "+str(entity.entity))
                    entity.delete()


def get_m(entity_ann):
    """
    :param ann_run:
    :return: number of cells that has entities
    """
    s = 0
    for cell in entity_ann.cells:
        if len(cell.entities) !=0:
            s+=1
    if s!=0:
        return s * 1.0
    return 1.0


def store_scores(ann_run,scores):
    """
    :param scores: a list of tuples in the form of score, type url order by most probable types
    :return:
    """
    ann_run.results = ""
    for uri in scores[:5]:
        ann_run.results += uri[-99:] + ","
    ann_run.save()


def dotype(ann_run, endpoint, onlyprefix):
    ann_run.status = 'removing noisy entities'
    ann_run.save()
    entity_ann = ann_run.entityann_set.all()[0]
    remove_noise_entities(entity_ann)
    ann_run.status = 'subclass queries'
    ann_run.save()
    timed_events = []
    graph = TypeGraph()
    params = []

    v_lock = Lock()
    v_reader_end, v_writer_end = Pipe()
    v_writer_process = Process(target=v_writer_func, args=({}, v_writer_end))
    v_writer_process.start()

    collected_classes = []

    for cell in entity_ann.cells:
        for entity in cell.entities:
            for cclass in entity.classes:
                if cclass.cclass not in collected_classes:
                    if onlyprefix is None or cclass.cclass.startswith(onlyprefix):
                        params.append((cclass.cclass, endpoint, v_lock, v_reader_end, 0, onlyprefix))
                        collected_classes.append(cclass.cclass)

    start = time.time()
    pool = Pool(max_num_of_threads=MAX_NUM_PROCESSES, func=build_graph_while_traversing, params_list=params)
    # pool = Pool(max_num_of_processes=MAX_NUM_PROCESSES, func=build_graph_while_traversing, params_list=params)
    logger.debug("will run the pool")
    pool.run()
    logger.debug("the pool is done")
    end = time.time()
    timed_events.append(("build graph while traversing", end-start))
    v_reader_end.send(1)
    visited = v_reader_end.recv()
    v_writer_process.terminate()
    logger.debug("build graph from nodes\n\n")
    ann_run.status = 'building the class graph'
    ann_run.save()
    start = time.time()
    build_graph_from_nodes(graph=graph, nodes_dict=visited)
    end = time.time()
    timed_events.append(("build graph2", end-start))
    logger.debug("remove single nodes\n\n")
    start = time.time()
    remove_nodes(entity_ann=entity_ann, classes=graph.remove_lonely_nodes())
    end = time.time()
    timed_events.append(("remove lonely nodes", end-start))
    start = time.time()
    remove_empty(entity_ann=entity_ann)
    end = time.time()
    timed_events.append(("remove empty entities", end - start))
    logger.debug("coverage\n\n")
    ann_run.status = 'Computing the coverage scores'
    ann_run.save()
    start = time.time()
    compute_coverage_score_for_graph(entity_ann=entity_ann, graph=graph)
    graph.set_converage_score()
    end = time.time()
    timed_events.append(("coverage", end-start))
    ann_run.status = 'Performing count queries'
    ann_run.save()
    logger.debug("count subjects \n\n")
    start = time.time()
    classes_counts = count_classes(classes=graph.cache, endpoint=endpoint)

    graph.set_nodes_subjects_counts(d=classes_counts)
    end = time.time()
    timed_events.append(("classes counts", end-start))
    logger.debug("specificity\n\n")
    ann_run.status = 'Computing the specificity scores'
    ann_run.save()

    start = time.time()
    logger.debug("specificity score")
    graph.set_specificity_score()
    logger.debug("specificity path")
    graph.set_path_specificity()
    end = time.time()

    timed_events.append(("specificity", end-start))
    start = time.time()
    logger.debug("set depth for graph")
    graph.set_depth_for_graph()
    logger.debug("set score for the graph")
    graph.set_score_for_graph(coverage_weight=0.1, m=get_m(entity_ann))
    end = time.time()
    timed_events.append(("latest score", end-start))
    ann_run.status = 'Computing the overall scores'
    ann_run.save()

    latest_scores = graph.get_scores()
    store_scores(ann_run, [n.title for n in latest_scores])
    print("scores: ")
    for n in latest_scores:
        print("%f %s" % (n.score, n.title))
    for te in timed_events:
        print("event: %s took: %.2f seconds" % (te[0], te[1]))
    graph_file_name = "%d %s.json" % (ann_run.id, ann_run.name)
    graph_file_name = graph_file_name.replace(' ', '_')
    graph_file_dir = os.path.join(MODELS_DIR, graph_file_name)
    logger.debug("graph_file_dir: "+graph_file_dir)
    graph.save(graph_file_dir)
    # entity_ann.graph_file.name = graph_file_name
    # entity_ann.graph_dir = graph_file_dir
    entity_ann.graph_dir = graph_file_name
    entity_ann.save()
    ann_run.status = 'Annotation is complete'
    ann_run.save()


def load_graph(entity_ann):
    graph_dir = os.path.join(MODELS_DIR, entity_ann.graph_dir)
    f = open(graph_dir, 'r')
    j = json.loads(f.read())
    g = TypeGraph()
    g.load(j, get_m(entity_ann))
    return g


def score_graph(graph, alpha, entity_ann, fsid):
    graph.set_score_for_graph(coverage_weight=alpha, m=get_m(entity_ann), fsid=fsid)
    return [n.title for n in graph.get_scores()]


def get_nodes(graph):
    return [graph.index[t] for t in graph.cache]
    # return graph.cache


def get_edges(graph):
    return graph.get_edges()


def random_string(length=4):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

