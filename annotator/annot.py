import os
import time
import logging
import traceback
import math

import sys
import pandas as pd


from multiprocessing import Process, Lock, Pipe
from TPool.TPool import Pool

from commons import random_string
from commons.easysparql import get_entities_and_classes, get_entities_and_classes_naive
from commons.easysparql import get_parents_of_class, get_num_class_subjects
from commons.tgraph import TGraph


class Annotator:
    def __init__(self, num_of_threads=10, logger=None, endpoint="", class_prefs=[], alpha=None, title_case=False):
        if logger is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)
            # create console handler and set level to debug
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            logger.addHandler(handler)

        self.title_case = title_case
        self.logger = logger
        self.num_of_threads = num_of_threads
        self.endpoint = endpoint
        self.class_prefs = class_prefs
        self.tgraph = TGraph()
        self.cell_ent_class = dict()
        self.lock = Lock()
        self.ancestors = dict()
        self.classes_counts = dict()
        self.alpha = alpha

    def clear_for_reuse(self):
        self.alpha = None
        self.cell_ent_class = dict()
        self.tgraph.clear_for_reuse()

    def detect_subject_col(self, file_dir):
        return 0

    def _load_table(self, file_dir):
        df = pd.read_csv(file_dir)
        mat = df.values
        mat = mat.astype(str)
        return mat

    def _get_cell_ann_param_list(self, subject_col_id, file_dir):
        params_list = []
        for r in self._load_table(file_dir):
            row = r
            # self.logger.debug('entity_column_id check: ' + str((subject_col_id, row[subject_col_id])))
            params_list.append((row, subject_col_id))
        return params_list

    def annotate_table(self, file_dir=None, subject_col_id=None):
        logger = self.logger
        if subject_col_id is None:
            subject_col_id = self.detect_subject_col(file_dir)

        start = time.time()
        logger.info('annotating: %s (col=%d)' % (file_dir, subject_col_id))
        params_list = self._get_cell_ann_param_list(subject_col_id, file_dir)

        # logger.debug("annotate_csv> total number of lines: " + str(len(params_list)))
        pool = Pool(max_num_of_threads=self.num_of_threads, func=self.annotate_single_cell, params_list=params_list)
        pool.run()
        # logger.debug("annotate_csv> annotated all cells")

        self.build_ancestors_lookup()
        self.remove_unwanted_parent_classes()
        self.compute_coverage()
        self.compute_specificity()
        if self.alpha:
            self.compute_f(self.alpha)

        end = time.time()
        logger.debug("Time spent: %f seconds" % (end - start))

    def annotate_single_cell(self, row, entity_column_id):
        # logger.debug("annotate_single_cell> start")

        cell_value = row[entity_column_id]
        self.lock.acquire()
        # logger.debug("annotate_single_cell> cell lock acquired")
        try:
            if cell_value in self.cell_ent_class:  # already processed
                self.lock.release()
                return

        except Exception as ex:
            self.logger.debug("annotate_single_cell> cell value: <" + cell_value + ">")
            self.logger.debug(str(ex))
            traceback.print_exc()
            self.lock.release()
            return

        # logger.debug("annotate_single_cell> releasing lock")
        self.lock.release()

        # logger.debug("cell: " + str(cell_value))
        self._add_entities_and_classes_to_cell(row, entity_column_id, cell_value)

    def _add_entities_and_classes_to_cell(self, row, entity_column_id, cell_value):
        attrs = []

        for i in range(len(row)):
            if i != entity_column_id:
                attrs.append(row[i])

        entity_class_pairs = []
        if self.title_case:
            possible_cell_values = [cell_value, cell_value.title()]
        else:
            possible_cell_values = [cell_value]
        for cell_val in possible_cell_values:
            entity_class_pairs = get_entities_and_classes(subject_name=cell_val, attributes=attrs,
                                                          endpoint=self.endpoint)
            if len(entity_class_pairs) > 0:
                break

        if len(entity_class_pairs) == 0:
            for cell_val in possible_cell_values:
                entity_class_pairs = get_entities_and_classes_naive(subject_name=cell_val, endpoint=self.endpoint)
                if len(entity_class_pairs) > 0:
                    break
        # entity_class_pairs = get_entities_and_classes(subject_name=cell_value, attributes=attrs, endpoint=self.endpoint)
        #
        # if len(entity_class_pairs) == 0:
        #     # logger.debug("_add_entities_and> no high quality  entity_class_pairs are found, hence trying the naive")
        #     entity_class_pairs = get_entities_and_classes_naive(subject_name=cell_value, endpoint=self.endpoint)
        # # else:
        # #     logger.debug("_add_entities_and>  high quality")

        d = dict()
        for ent_class in entity_class_pairs:
            ent, class_uri = ent_class
            if not self.class_prefix_match(class_uri):
                continue
            if ent not in d:
                d[ent] = []
            d[ent].append(class_uri)

        self.build_class_graph(d)
        self.lock.acquire()
        self.cell_ent_class[cell_value] = d
        self.lock.release()

    def class_prefix_match(self, class_uri):
        if len(self.class_prefs) == 0:
            return True
        for pref in self.class_prefs:
            if class_uri[:len(pref)] == pref:
                return True
        return False

    def remove_unwanted_parent_classes(self):
        for cell in self.cell_ent_class:
            d = self.remove_unwanted_parent_classes_for_cell(self.cell_ent_class[cell])
            self.cell_ent_class[cell] = d

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
        self.lock.acquire()
        for ent in entities:
            for class_uri in entities[ent]:
                self.add_class_to_graph(class_uri)
        self.lock.release()

    def add_class_to_graph(self, class_uri):
        if not self.class_prefix_match(class_uri):
            return False
        newly_added = self.tgraph.add_class(class_uri)
        if newly_added:
            parents = get_parents_of_class(class_uri, endpoint=self.endpoint)
            for p in parents:
                if not self.class_prefix_match(p):
                    continue
                self.add_class_to_graph(p)
                self.tgraph.add_parent(class_uri, p)
        return newly_added

    def build_ancestors_lookup(self):
        self.lock.acquire()
        for class_uri in self.tgraph.nodes:
            if class_uri not in self.ancestors:
                d = dict()
                ancestors = self.tgraph.get_ancestors(class_uri)
                for anc in ancestors:
                    d[anc] = True  # The value true means nothing here. We just want to use dict for the fast lookup

                self.ancestors[class_uri] = d
        self.lock.release()

    def compute_coverage(self):
        self.compute_Ic()
        self.compute_Lc()
        self.compute_fc()

    def _compute_Lc_for_node(self, node):
        if node.Lc is not None:
            return node.Lc
        curr_lc = 0
        for ch_uri in node.childs:
            ch = node.childs[ch_uri]
            curr_lc += self._compute_Lc_for_node(ch)
        if node.Ic is None:
            node.Ic = 0
        node.Lc = curr_lc + node.Ic
        return node.Lc

    def compute_Lc(self):
        for class_uri in self.tgraph.nodes:
            node = self.tgraph.nodes[class_uri]
            self._compute_Lc_for_node(node)

    def compute_fc(self):
        for class_uri in self.tgraph.nodes:
            node = self.tgraph.nodes[class_uri]
            if self.tgraph.m == 0:  # this happens incase the previous run had some annotations, but this one no annotations
                node.fc = 0
            else:
                node.fc = node.Lc / self.tgraph.m

    def compute_Ic(self):
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

    def compute_specificity(self):
        self._compute_classes_counts()
        self.compute_Is()
        self.compute_Ls()
        self.compute_fs()

    def compute_fs(self):
        for class_uri in self.tgraph.nodes:
            node = self.tgraph.nodes[class_uri]
            node.fs[1] = math.sqrt(1 - node.Ls * node.Ls)
            node.fs[2] = -1 * node.Ls * node.Ls + 1
            node.fs[3] = -1 * node.Ls + 1
            node.fs[4] = 1 - math.sqrt(node.Ls)
            node.fs[5] = (1 - math.sqrt(node.Ls)) ** 2

    def _compute_classes_counts(self):
        for class_uri in self.tgraph.nodes:
            if class_uri not in self.classes_counts:  # to skip in case it was cleared for the reuse
                num = get_num_class_subjects(class_uri, self.endpoint)
                self.classes_counts[class_uri] = num

    def compute_Is(self):
        for class_uri in self.tgraph.nodes:
            node = self.tgraph.nodes[class_uri]
            par_classes = [p for p in node.parents]
            if len(par_classes) == 0:
                node.Is = 1
            else:
                pars = [int(self.classes_counts[pclass]) for pclass in par_classes]
                max_pr = max(pars)
                node.Is = int(self.classes_counts[class_uri]) / max_pr
                if node.Is > 1:
                    print("Error: count class <%s>: %d and parent: %d" % (
                        class_uri, self.classes_counts[class_uri], max_pr))
                    raise Exception("Exception in compute_Is. Too big Is")

    def compute_Ls(self):
        for class_uri in self.tgraph.nodes:
            self._compute_Ls_for_node(self.tgraph.nodes[class_uri])

    def _compute_Ls_for_node(self, node):
        if node.Ls is None:
            pars = []
            for p in node.parents:
                pars.append(self._compute_Ls_for_node(self.tgraph.nodes[p]))
            if len(pars) == 0:
                par_max = 1
            else:
                par_max = max(pars)
            node.Ls = par_max * node.Is
        return node.Ls

    def compute_f(self, alpha):
        self.alpha = alpha
        for class_uri in self.tgraph.nodes:
            node = self.tgraph.nodes[class_uri]
            for fsid in range(1, 6):
                node.f[fsid] = node.fc * alpha + node.fs[fsid] * (1 - alpha)

    def get_top_k(self, fsid=None, k=None):
        if self.alpha is None:
            print("Error: alpha is missing. You need to call compute_f(alpha) function before")
            return None
        if fsid is None:
            print("Error: expecting the fsid")
            return None
        scores = []
        for class_uri in self.tgraph.nodes:
            node = self.tgraph.nodes[class_uri]
            if node.fc == 0:
                # print("get_top_k> skip fc %s" % class_uri)
                continue
            # if node.f[fsid] == 0:
            #     print("get_top_k> skip %s" % class_uri)

            pair = (node.class_uri, node.f[fsid])
            scores.append(pair)
        scores.sort(key=lambda x: x[1], reverse=True)
        classes = [sc[0] for sc in scores]
        if k:
            classes = classes[:k]
        return classes

    def print_ann(self):
        for c in self.cell_ent_class:
            print(c)
            for ent in self.cell_ent_class[c]:
                print("\t" + ent)
                for cl in self.cell_ent_class[c][ent]:
                    print("\t\t" + cl)

    def print_hierarchy(self):
        print("\nprint_hierarchy: ")
        for n in self.tgraph.nodes:
            node = self.tgraph.nodes[n]
            print(node.class_uri)
            for ch in node.childs:
                print("\t" + node.childs[ch].class_uri)

    def print_ancestors(self):
        print("\nprint_ancestors: ")
        for class_uri in self.ancestors:
            print(class_uri)
            if self.ancestors[class_uri]:
                for anc in self.ancestors[class_uri]:
                    print("\t" + anc)


if __name__ == '__main__':
    file_dir = sys.argv[1]
    print("file dir: "+file_dir)
    # a = Annotator(endpoint="https://en-dbpedia.oeg.fi.upm.es/sparql", alpha=0.3)
    a = Annotator(endpoint="https://en-dbpedia.oeg.fi.upm.es/sparql",
                  class_prefs=["http://dbpedia.org/ontology/", "http://www.w3.org/2002/07/owl#Thing"])
    if len(sys.argv) >= 3:
        col_id = int(sys.argv[2])
    else:
        col_id = 0
    print("col id: %d " % col_id)
    a.annotate_table(file_dir=file_dir, subject_col_id=col_id)
    a.compute_f(0.01)
    print(a.get_top_k(k=3, fsid=3))
    #a.print_ann()
    # a.print_ancestors()
    # print(a.ancestors)
    # a.print_hierarchy()
    # print(a.cell_ent_class)
