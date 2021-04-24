from annotator import cmd
import argparse
import json
import os
import time
import logging
import random
import traceback
import string
import math
import sys
import pandas as pd

from tadae.models import AnnRun, EntityAnn, Cell, CClass, Entity


from multiprocessing import Process, Lock, Pipe
# from PPool.Pool import Pool
from TPool.TPool import Pool
from commons import random_string

from graph.type_graph import TypeGraph
from commons.logger import set_config
from commons.easysparql import get_entities, get_classes, get_entities_and_classes, get_entities_and_classes_naive
from commons.easysparql import get_parents_of_class
from commons.easysparql import get_classes_subjects_count
from commons.tgraph import TGraph


class Annotator:

    def __init__(self, num_of_threads=10, logger=logging.getLogger(__name__), endpoint="", onlyprefix=None):
        self.logger = logger
        self.num_of_threads = num_of_threads
        self.endpoint = endpoint
        self.onlyprefix = onlyprefix
        self.tgraph = TGraph()
        self.cell_ent_class = dict()
        self.use_db = True
        self.lock = Lock()
        self.ancestors = dict()

    def detect_subject_col(self, file_dir):
        return 0

    def annotate_table(self, ann_run_id=None, file_dir=None, subject_col_id=None):
        logger = self.logger
        if subject_col_id is None:
            subject_col_id = self.detect_subject_col(file_dir)
        if self.use_db:
            try:
                ann_run = AnnRun.objects.get(id=ann_run_id)
            except:
                ann_run = AnnRun(name=random_string(5), status='started')

            ann_run.status = 'adding dataset: ' + str(file_dir.split(os.path.sep)[-1])
            ann_run.save()
            entity_ann = EntityAnn(ann_run=ann_run, col_id=subject_col_id, status="cell annotation")
            entity_ann.save()

        start = time.time()
        logger.info('annotating: ' + file_dir)
        df = pd.read_csv(file_dir)
        mat = df.values
        mat = mat.astype(str)
        params_list = []
        for r in mat:
            row = r
            logger.debug('entity_column_id check: ' + str((subject_col_id, row[subject_col_id])))
            params_list.append((entity_ann, row, subject_col_id))

        logger.debug("annotate_csv> number of total processes to run: " + str(len(params_list)))
        pool = Pool(max_num_of_threads=self.num_of_threads, func=self.annotate_single_cell, params_list=params_list)
        pool.run()
        logger.debug("annotate_csv> annotated all cells")
        logger.debug("annotate_csv> all processes are stopped now")
        end = time.time()
        logger.debug("Time spent: %f" % (end - start))
        if self.use_db:
            ann_run.status = 'datasets are added'
            ann_run.save()

    def annotate_single_cell(self, entity_ann, row, entity_column_id):
        logger = self.logger
        logger.debug("annotate_single_cell> start")
        if self.use_db:
            logger.debug("entity_ann parent name: " + entity_ann.ann_run.name)
        cell_value = row[entity_column_id]
        lock = self.lock
        lock.acquire()
        logger.debug("annotate_single_cell> cell lock acquired")
        try:
            if cell_value in self.cell_ent_class:  # already processed
                return
            if self.use_db:
                cell = Cell(text_value=cell_value, entity_ann=entity_ann)
                cell.save()
        except Exception as ex:
            logger.debug("annotate_single_cell> cell value: <" + cell_value + ">")
            logger.debug(str(ex))
            traceback.print_exc()
            lock.release()
            return

        logger.debug("annotate_single_cell> releasing lock")
        lock.release()

        logger.debug("cell: " + str(cell_value))
        attrs = []
        for i in range(len(row)):
            if i != entity_column_id:
                attrs.append(row[i])
        entity_class_pairs = get_entities_and_classes(subject_name=cell_value, attributes=attrs,
                                                      endpoint=self.endpoint)
        if len(entity_class_pairs) == 0:
            logger.debug("annotate_single_cell> no high quality  entity_class_pairs are found, hence trying the naive")
            entity_class_pairs = get_entities_and_classes_naive(subject_name=cell_value, endpoint=self.endpoint)

        d = dict()
        for ent_class in entity_class_pairs:
            ent, class_uri = ent_class
            if ent not in d:
                d[ent] = []
            d[ent].append(class_uri)

        self.build_class_graph(d)
        self.build_ancestors_lookup()
        d = self.remove_unwanted_parent_classes_for_cell(d)
        lock.acquire()
        self.cell_ent_class[cell_value] = d
        lock.release()

        if self.use_db:
            lock.acquire()
            for ent in d:
                try:
                    e = Entity(cell=cell, entity=ent)
                    e.save()

                    for class_uri in d[ent]:
                        if self.onlyprefix is None or (class_uri.startswith(self.onlyprefix)):
                            ccclass = CClass(entity=e, cclass=class_uri)
                            ccclass.save()

                except Exception as ex:
                    logger.debug("annotate_single_cell> entity value: <" + ent + ">")
                    logger.debug("annotate_single_cell> class value: <" + class_uri + ">")
                    logger.debug(str(ex))
                    traceback.print_exc()
                    lock.release()
                    return
            lock.release()

    def remove_unwanted_parent_classes_for_cell(self, entities):
        """
        :param entities: a dict of entities as keys and the values are a list of classes uris
        :param lock:
        :return:
        """
        d = dict()
        for ent in entities:
            d[ent] = self.remove_unwanted_parent_classes_for_entity(entities[ent])
        return d

    def remove_unwanted_parent_classes_for_entity(self, classes):
        """
        :param classes: a list of classes uris
        :return: list
        """
        lock = self.lock
        lock.acquire()
        for class_uri in classes:
            if class_uri not in self.ancestors:
                d = dict()
                # class_anc[class_uri] = dict()
                ancestors = self.tgraph.get_ancestors(class_uri)
                for anc in ancestors:
                    d[anc] = True  # The value true means nothing here. We just want to use dict for the fast lookup
                self.ancestors[class_uri] = d

        unwanted = []
        for class_uri in classes:
            for another_uri in classes:
                if class_uri == another_uri:  # in case a class can be a subClassOf itself
                    continue
                if another_uri in self.ancestors[class_uri]:
                    unwanted.append(another_uri)
        lock.release()

        wanted = list(set(classes) - set(unwanted))
        return wanted

    def build_class_graph(self, entities):
        """
        :param entities: dict of entity uris as keys and the values are the list of classes
        :return:
        """
        lock = self.lock
        for ent in entities:
            for class_uri in entities[ent]:
                lock.acquire()
                added = self.tgraph.add_class(class_uri)
                lock.release()
                if added:
                    parents = get_parents_of_class(class_uri, endpoint=self.endpoint)
                    lock.acquire()
                    for p in parents:
                        added = self.tgraph.add_class(p)
                        if added:
                            self.tgraph.add_parent(class_uri, p)
                    lock.release()

    def build_ancestors_lookup(self):
        for class_uri in self.tgraph.nodes:
            if class_uri not in self.ancestors:
                d = dict()
                ancestors = self.tgraph.get_ancestors(class_uri)
                for anc in ancestors:
                    d[anc] = True  # The value true means nothing here. We just want to use dict for the fast lookup
                self.ancestors[class_uri] = d

    def type_subject_column(self, ann_run=None):
        self.compute_coverage()
        # latest_scores = graph.get_scores()
        # store_scores(ann_run, [n.title for n in latest_scores])
        # print("scores: ")
        # for n in latest_scores:
        #     print("%f %s" % (n.score, n.title))
        # for te in timed_events:
        #     print("event: %s took: %.2f seconds" % (te[0], te[1]))
        # graph_file_name = "%d %s.json" % (ann_run.id, ann_run.name)
        # graph_file_name = graph_file_name.replace(' ', '_')
        # graph_file_dir = os.path.join(MODELS_DIR, graph_file_name)
        # logger.debug("graph_file_dir: " + graph_file_dir)
        # graph.save(graph_file_dir)
        # # entity_ann.graph_file.name = graph_file_name
        # # entity_ann.graph_dir = graph_file_dir
        # entity_ann.graph_dir = graph_file_name
        # entity_ann.save()
        # ann_run.status = 'Annotation is complete'
        # ann_run.save()

    # New coverage
    def compute_coverage(self):
        cov = dict()
        m = 0
        for cell in self.cell_ent_class:
            entities = self.cell_ent_class[cell]
            if len(entities) == 0:
                continue

            e_score = 1.0 / len(entities)
            found_one_class_at_least = False
            for entity in entities:
                classes = entities[entity]
                if len(classes) == 0:
                    continue

                found_one_class_at_least = True
                c_score = 1.0 / len(classes)
                for class_uri in classes:
                    if class_uri not in cov:
                        cov[class_uri] = 0

                    cov[class_uri] += c_score * e_score

            if found_one_class_at_least:
                m += 1

        self.tgraph.m = m
        for class_uri in cov:
            self.tgraph.nodes[class_uri].Ic = cov[class_uri]

    # def compute_coverage_ls(self):
    #     for node in self.tgraph.nodes:


# a = Annotator()
# a.test_threads()


if __name__ == '__main__':
    file_dir = sys.argv[1]
    a = Annotator(endpoint="https://en-dbpedia.oeg.fi.upm.es/sparql")
    a.annotate_table(file_dir=file_dir)

