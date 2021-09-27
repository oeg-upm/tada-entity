import os
from unittest import TestCase
import annotator
import commons
from annotator.annot import Annotator
import experiments.alpha_eval as ae
import math
import pandas as pd


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
        self.assertIn(3, acc)
        self.assertTrue(acc[3]['alpha_mean'])

    def test_run_class(self):
        d = dict()
        class_uri = "http://dbpedia.org/ontology/Swimmer"
        fname = "swimmers.csv"
        fname2 = "swimmers2.csv"
        fnames = [fname, fname2]
        col_id = 0
        for i in range(1, 6):
            d[i] = {class_uri: dict()}
            for fn in fnames:
                d[i][class_uri][fn] = {
                    'alpha': 0.1,
                    'col_id': col_id,
                    'alpha_mean': 0.11,
                    'alpha_median': 0.12
                }
        title_case = True
        data_dir = "tests"
        alphas_fsid = d
        acc = ae.run_with_class(class_uri, alphas_fsid, title_case, data_dir)
        self.assertIn(3, acc)
        self.assertTrue(acc[3]['alpha_mean'])

    def test_aggregate_alpha(self):
        class_uri = "http://dbpedia.org/ontology/Swimmer"
        fname = "swimmers.csv"
        fname2 = "swimmers2.csv"
        rows = []
        for i in range(1,6):
            r = ['swimmers.csv', 0, i, 0.9, 1.1]
            rows.append(r)
        df = pd.DataFrame(rows, columns=["fname", "colid", "fsid", "from_alpha", "to_alpha"])
        classes_dict = {
            fname: class_uri,
            fname2: class_uri
        }
        d = ae.aggregate_alpha_per_class_per_file(df, classes_dict)
        self.assertIn(class_uri, d)
        self.assertIn(fname, d[class_uri])
        self.assertIn('alpha', d[class_uri][fname])

    def test_run_pred(self):
        d = dict()
        class_uri = "http://dbpedia.org/ontology/Swimmer"
        fname = "swimmers.csv"
        fname2 = "swimmers2.csv"
        fnames = [fname, fname2]
        col_id = 0
        for i in range(1, 6):
            d[i] = {class_uri: dict()}
            for fn in fnames:
                d[i][class_uri][fn] = {
                    'alpha': 0.1,
                    'col_id': col_id,
                    'alpha_mean': 0.11,
                    'alpha_median': 0.12
                }
        title_case = True
        data_dir = "tests"
        alphas_fsid = d
        d = ae.run_with_pred_alpha(alphas_fsid, title_case, data_dir, [class_uri])
        self.assertIn(3, d)
        self.assertIn(class_uri, d[3])
        self.assertIn('alpha_mean', d[3][class_uri])

    def test_compute_k_fold_alpha_accuracy(self):
        class_uri = "http://dbpedia.org/ontology/Swimmer"
        fname = "swimmers.csv"
        fname2 = "swimmers2.csv"
        falpha = "tests/alpha_test_1.csv"
        data_dir = "tests"
        classes_list = [class_uri]
        classes_dict = {
            fname: class_uri,
            fname2: class_uri
        }
        acc = ae.compute_k_fold_alpha_accuracy(falpha, data_dir, classes_dict, classes_list)
        self.assertIn(3, acc)
        self.assertIn(class_uri, acc[3])
        self.assertIn('num', acc[3][class_uri])
