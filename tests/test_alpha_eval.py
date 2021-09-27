import os
from unittest import TestCase
import annotator
import commons
from annotator.annot import Annotator
import experiments.alpha_eval as ae
import math


class AlphaEvalTest(TestCase):

    def test_validate_ann(self):
        d = dict()
        class_uri = "http://dbpedia.org/ontology/Swimmer"
        fname = "swimmers.csv"
        col_id = 0
        for i in range(1, 6):
            d[i] = dict()
            d[i][class_uri] = {fname: {
                'alpha': 0.1,
                'col_id': col_id,
                'alpha_mean': 0.11,
                'alpha_median': 0.12
            }}
        title_case = True
        fpath = os.path.join("tests", "swimmers.csv")
        res = ae.validate_annotation(class_uri, fname, col_id, fpath, title_case, d)
        self.assertTrue(res[3]['alpha_mean'])
        self.assertTrue(res[3]['alpha_median'])

    def test_measure_class(self):
        d = dict()
        class_uri = "http://dbpedia.org/ontology/Swimmer"
        fname = "swimmers.csv"
        col_id = 0
        for i in range(1, 6):
            d[i] = dict()
            d[i][class_uri] = {fname: {
                'alpha': 0.1,
                'col_id': col_id,
                'alpha_mean': 0.11,
                'alpha_median': 0.12
            }}
        title_case = True
        data_dir = "tests"
        fnames_colid = {
            fname: col_id
        }
        alphas_fsid = d
        acc = ae.measure_class_accuracy(class_uri, data_dir, fnames_colid, alphas_fsid, title_case)
        # print("AAAAAA: ")
        # print(acc)
        # print("fsid: ")
        # print(acc[3]['alpha_mean'])
        self.assertIn(3, acc)
        self.assertTrue(acc[3]['alpha_mean'])
