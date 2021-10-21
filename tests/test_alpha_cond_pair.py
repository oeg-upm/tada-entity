import os
from unittest import TestCase
import annotator
import commons
from annotator.annot import Annotator
import experiments.alpha_cond_pair as acp
import math
import pandas as pd


class AlphaCondPairTest(TestCase):

    def test_annotate_column(self):
        fpath = "tests/swimmers.csv"
        colid = 0
        evaluator = acp.annotate_column(fpath=fpath, col_id=colid, title_case=True)
        self.assertNotEqual(evaluator, None)

    def test_predict_class(self):
        fpath = "tests/swimmers.csv"
        colid = 0
        fsid = 3
        alpha = 0.1
        annotator = acp.annotate_column(fpath=fpath, col_id=colid, title_case=True)
        candidates = acp.predict_class(annotator, fsid, alpha)
        self.assertGreater(len(candidates), 0)
        self.assertEqual(candidates[0], 'http://dbpedia.org/ontology/Swimmer')

    def test_add_alpha_per_file(self):
        df = pd.read_csv('tests/alpha_test_1.csv')
        df2 = pd.DataFrame([['swimmers-new.csv', 0, 1, -1, -1]], columns=['fname','colid','fsid','from_alpha','to_alpha'])
        df = df.append(df2, ignore_index=True)
        acp.add_alpha_per_file(df)
        for idx, row in df.iterrows():
            self.assertIn('alpha', row)
        alphas = list(df['alpha'])
        self.assertIn(-1, alphas)

    def test_compute_file_acc(self):
        df = pd.read_csv('tests/alpha_test_2.csv')
        acc = None
        data_path = "tests"
        correct_class_uri = "http://dbpedia.org/ontology/Swimmer"
        alphas_classes = {
            1: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.005, 'median': 0.005}
            },
            2: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.005, 'median': 0.005}
            },
            3: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.09},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.1, 'median': 0.11}
            },
            4: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.09},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.1, 'median': 0.11}
            },
            5: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.09},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.1, 'median': 0.11}
            },
        }
        for idx, row in df.iterrows():
            acc = acp.compute_file_acc(row, alphas_classes, data_path, correct_class_uri, False)
            break

        for fsid in range(1, 6):
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[fsid][a_attr], 1)

    def test_get_file_acc(self):
        df = pd.read_csv('tests/alpha_test_1.csv')
        acp.add_alpha_per_file(df)
        acc = None
        data_path = "tests"
        correct_class_uri = "http://dbpedia.org/ontology/Swimmer"

        alphas_classes = {
            1: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.0005, 'median': 0.0005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.005, 'median': 0.005}
            },
            2: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.005, 'median': 0.005}
            },
            3: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.09},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.1, 'median': 0.11}
            },
            4: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.09},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.1, 'median': 0.11}
            },
            5: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.9, 'median': 0.9},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.9, 'median': 0.9}
            },
        }

        class_files_alpha = acp.get_class_files_alphas(df)

        for idx, row in df.iterrows():
            acc = acp.get_file_acc(row, class_files_alpha, alphas_classes, correct_class_uri, False, data_path, "max")
            break

        for fsid in range(1, 6):
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[fsid][a_attr], 1)

    def test_get_file_acc2(self):
        df = pd.read_csv('tests/alpha_test_3.csv')
        acp.add_alpha_per_file(df)
        acc = None
        data_path = "tests"
        correct_class_uri = "http://dbpedia.org/ontology/Swimmer"
        correct_class_uri2 = "http://dbpedia.org/ontology/GolfPlayer"
        correct_class_uri3 = "http://dbpedia.org/ontology/Bird"

        alphas_classes = {
            1: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.004, 'median': 0.004},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.004, 'median': 0.004}
            },
            2: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.004, 'median': 0.004},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.004, 'median': 0.004}

            },
            3: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.1},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.25, 'median': 0.24}
            },
            4: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.01},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.4, 'median': 0.4}
            },
            5: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.1},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.1},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.4, 'median': 0.4}
            },
        }

        df_swimmers = df[df.fname.isin(['swimmers.csv', 'swimmers2.csv'])]
        df_golfers = df[df.fname.isin(['golfplayers.csv', 'golfplayers2.csv'])]
        df_birds = df[df.fname.isin(['birds.csv', 'birds2.csv'])]

        swimmers_files_alpha = acp.get_class_files_alphas(df_swimmers)
        golfers_files_alpha = acp.get_class_files_alphas(df_golfers)
        birds_files_alpha = acp.get_class_files_alphas(df_birds)

        for idx, row in df_swimmers.iterrows():
            acc = acp.get_file_acc(row, swimmers_files_alpha, alphas_classes, correct_class_uri, False, data_path, "max")
            break

        for fsid in range(1, 5):
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[fsid][a_attr], 1)

        for idx, row in df_golfers.iterrows():
            acc = acp.get_file_acc(row, golfers_files_alpha, alphas_classes, correct_class_uri2, False, data_path, "max")
            break
        for fsid in range(1, 5):
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[fsid][a_attr], 1)

        for idx, row in df_birds.iterrows():
            acc = acp.get_file_acc(row, birds_files_alpha, alphas_classes, correct_class_uri3, False, data_path, "max")
            break
        for fsid in range(1, 5):
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[fsid][a_attr], 1)

    def test_get_file_acc3(self):
        """
        This is to verify if the changing the alphas for the class is reverted afterwards.
        :return:
        """
        df = pd.read_csv('tests/alpha_test_2.csv')
        acp.add_alpha_per_file(df)
        acc = None
        data_path = "tests"
        correct_class_uri = "http://dbpedia.org/ontology/Swimmer"
        correct_class_uri2 = "http://dbpedia.org/ontology/GolfPlayer"
        correct_class_uri3 = "http://dbpedia.org/ontology/Bird"

        alphas_classes = {
            1: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.004, 'median': 0.004},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.004, 'median': 0.004}
            },
            2: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.004, 'median': 0.004},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.004, 'median': 0.004}

            },
            3: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.1},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.25, 'median': 0.24}
            },
            4: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.01},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.4, 'median': 0.4}

            },
            5: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.1},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.4, 'median': 0.4}

            },
        }

        df_swimmers = df[df.fname.isin(['swimmers.csv', 'swimmers2.csv'])]
        df_golfers = df[df.fname.isin(['golfplayers.csv', 'golfplayers2.csv'])]
        df_birds = df[df.fname.isin(['birds.csv', 'birds2.csv'])]

        swimmers_files_alpha = acp.get_class_files_alphas(df_swimmers)
        golfers_files_alpha = acp.get_class_files_alphas(df_golfers)
        birds_files_alpha = acp.get_class_files_alphas(df_birds)

        for idx, row in df_swimmers.iterrows():
            acc = acp.get_file_acc(row, swimmers_files_alpha, alphas_classes, correct_class_uri, False, data_path, "max")
            break

        for fsid in range(1, 6):
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[fsid][a_attr], 1)

        for idx, row in df_golfers.iterrows():
            acc = acp.get_file_acc(row, golfers_files_alpha, alphas_classes, correct_class_uri2, False, data_path, "max")
            break
        for fsid in range(1, 6):
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[fsid][a_attr], 1)

        for idx, row in df_birds.iterrows():
            acc = acp.get_file_acc(row, birds_files_alpha, alphas_classes, correct_class_uri3, False, data_path, "max")
            break
        for fsid in range(1, 6):
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[fsid][a_attr], 1)

        gs_alphas_classes = {
            1: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.004, 'median': 0.004},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.004, 'median': 0.004}
            },
            2: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.004, 'median': 0.004},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.004, 'median': 0.004}

            },
            3: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.1},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.25, 'median': 0.24}
            },
            4: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.01},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.4, 'median': 0.4}

            },
            5: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.1},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.4, 'median': 0.4}
            },
        }

        for fsid in range(1,6):
            for cls in [correct_class_uri, correct_class_uri2]:
                self.assertDictEqual(alphas_classes[fsid][cls], gs_alphas_classes[fsid][cls])

    def test_get_acc_per_class(self):
        df = pd.read_csv('tests/alpha_test_3.csv')
        acp.add_alpha_per_file(df)
        acc = dict()
        data_path = "tests"
        correct_class_uris = ["http://dbpedia.org/ontology/Swimmer", "http://dbpedia.org/ontology/GolfPlayer",
                             "http://dbpedia.org/ontology/Bird"]
        alphas_classes = {
            1: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.004, 'median': 0.004},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.004, 'median': 0.004}
            },
            2: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.004, 'median': 0.004},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.004, 'median': 0.004}
            },
            3: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.1},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.25, 'median': 0.24}
            },
            4: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.01},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.4, 'median': 0.4}
            },
            5: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.99, 'median': 0.99},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.0, 'median': 0.0},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.99, 'median': 0.99}
            },
        }

        df_swimmers = df[df.fname.isin(['swimmers.csv', 'swimmers2.csv'])]
        df_golfers = df[df.fname.isin(['golfplayers.csv', 'golfplayers2.csv'])]
        df_birds = df[df.fname.isin(['birds.csv', 'birds2.csv'])]

        dfs = [df_swimmers, df_golfers, df_birds]

        for idx, df in enumerate(dfs):
            acc[idx] = acp.get_acc_per_class(df, alphas_classes, correct_class_uris[idx], False, data_path, "max")

        for fsid in range(1, 5):
            for class_idx in range(len(dfs)):
                self.assertIn(fsid, acc[class_idx])
                for a_attr in acc[class_idx][fsid]:
                    self.assertEqual(acc[class_idx][fsid][a_attr], 1.0)

        for fsid in range(5, 6):
            for class_idx in range(len(dfs)):
                self.assertIn(fsid, acc[class_idx])
                for a_attr in acc[class_idx][fsid]:
                    self.assertNotEqual(acc[class_idx][fsid][a_attr], 1.0)

    def test_get_accuracy_for_classes(self):
        df = pd.read_csv('tests/alpha_test_3.csv')
        df[["colid"]] = df[["colid"]].apply(pd.to_numeric)
        acp.add_alpha_per_file(df)
        data_path = "tests"
        correct_class_uris = ["http://dbpedia.org/ontology/Swimmer", "http://dbpedia.org/ontology/GolfPlayer",
                              "http://dbpedia.org/ontology/Bird"]
        alphas_classes = {
            1: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.004, 'median': 0.004},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.004, 'median': 0.004}
            },
            2: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.004, 'median': 0.004},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.004, 'median': 0.004}

            },
            3: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.1},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.25, 'median': 0.24}
            },
            4: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.01},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.4, 'median': 0.4}

            },
            5: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.99, 'median': 0.99},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.99, 'median': 0.99},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.99, 'median': 0.99}

            },
        }

        classes_fnames = acp.get_classes_fnames_col_ids("tests/meta1.csv", "wcv1")
        acc = acp.get_accuracy_for_classes(df, classes_fnames, alphas_classes, True, "tests", "max")

        for fsid in range(1, 5):
            for class_uri in correct_class_uris:
                self.assertIn(fsid, acc[class_uri])
                for a_attr in acc[class_uri][fsid]:
                    self.assertEqual(acc[class_uri][fsid][a_attr], 1.0)

        for fsid in range(5, 6):
            for class_uri in correct_class_uris:
                self.assertIn(fsid, acc[class_uri])
                for a_attr in acc[class_uri][fsid]:
                    self.assertNotEqual(acc[class_uri][fsid][a_attr], 1.0)

    def test_get_accuracy_for_all(self):
        df = pd.read_csv('tests/alpha_test_3.csv')
        df[["colid"]] = df[["colid"]].apply(pd.to_numeric)
        acp.add_alpha_per_file(df)

        data_path = "tests"
        correct_class_uris = ["http://dbpedia.org/ontology/Swimmer", "http://dbpedia.org/ontology/GolfPlayer",
                              "http://dbpedia.org/ontology/Bird"]
        alphas_classes = {
            1: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.004, 'median': 0.004},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.004, 'median': 0.004}
            },
            2: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.005, 'median': 0.005},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.004, 'median': 0.004},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.004, 'median': 0.004}

            },
            3: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.1},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.25, 'median': 0.24}
            },
            4: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.1, 'median': 0.11},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.09, 'median': 0.01},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.4, 'median': 0.4}
            },
            5: {
                "http://dbpedia.org/ontology/Swimmer": {'mean': 0.99, 'median': 0.99},
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.99, 'median': 0.99},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.99, 'median': 0.99}
            },
        }

        classes_fnames = acp.get_classes_fnames_col_ids("tests/meta1.csv", "wcv1")
        acc = acp.get_accuracy(df, classes_fnames, False, data_path, "max")

        for fsid in range(1, 5):
            for class_uri in correct_class_uris:
                self.assertIn(fsid, acc[class_uri])
                for a_attr in acc[class_uri][fsid]:
                    self.assertEqual(acc[class_uri][fsid][a_attr], 1.0)

        for fsid in range(5, 6):
            for class_uri in correct_class_uris:
                self.assertIn(fsid, acc[class_uri])
                for a_attr in acc[class_uri][fsid]:
                    self.assertNotEqual(acc[class_uri][fsid][a_attr], 1.0)

    def test_workflow_swimmers(self):
        data_path = "tests"
        correct_class_uris = ["http://dbpedia.org/ontology/Swimmer", "http://dbpedia.org/ontology/GolfPlayer",
                              "http://dbpedia.org/ontology/Bird"]
        acc = acp.workflow('tests/alpha_test_5.csv', None, "wcv1", "tests/meta1.csv", False, data_path, None, "max")
        for fsid in range(1, 5):
            for class_uri in correct_class_uris:
                self.assertIn(fsid, acc[class_uri])
                for a_attr in acc[class_uri][fsid]:
                    self.assertEqual(acc[class_uri][fsid][a_attr], 1.0)
                break

        for fsid in range(5, 6):
            for class_uri in correct_class_uris:
                self.assertIn(fsid, acc[class_uri])
                for a_attr in acc[class_uri][fsid]:
                    self.assertNotEqual(acc[class_uri][fsid][a_attr], 1.0)
                break

    def test_workflow1(self):

        data_path = "tests"
        correct_class_uris = ["http://dbpedia.org/ontology/Swimmer", "http://dbpedia.org/ontology/GolfPlayer",
                              "http://dbpedia.org/ontology/Bird"]

        acc = acp.workflow('tests/alpha_test_3.csv', None, "wcv1", "tests/meta1.csv", False, data_path, None, "max")

        for fsid in range(1, 5):
            for class_uri in correct_class_uris:
                self.assertIn(fsid, acc[class_uri])
                for a_attr in acc[class_uri][fsid]:
                    self.assertEqual(acc[class_uri][fsid][a_attr], 1.0)
                break

        for fsid in range(5, 6):
            for class_uri in correct_class_uris:
                self.assertIn(fsid, acc[class_uri])
                for a_attr in acc[class_uri][fsid]:
                    self.assertNotEqual(acc[class_uri][fsid][a_attr], 1.0)
                break

    def test_workflow2(self):
        """
        The case of classes with single files and -1 alpha for some fsid
        :return:
        """
        data_path = "tests"
        correct_class_uris = ["http://dbpedia.org/ontology/Swimmer", "http://dbpedia.org/ontology/GolfPlayer",
                              "http://dbpedia.org/ontology/Bird"]

        acc = acp.workflow('tests/alpha_test_4.csv', None, "wcv1", "tests/meta2.csv", False, data_path, None, "max")

        # Swimmer
        for a_attr in ['mean', 'median']:
            self.assertEqual(acc[correct_class_uris[0]][1][a_attr], 1.0)

        for a_attr in ['mean', 'median']:
            self.assertEqual(acc[correct_class_uris[0]][2][a_attr], -1)

        for fsid in range(3, 5):
            self.assertIn(fsid, acc[correct_class_uris[0]])
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[correct_class_uris[0]][fsid][a_attr], 1.0)

        # Golf
        for fsid in range(3, 5):
            self.assertIn(fsid, acc[correct_class_uris[1]])
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[correct_class_uris[1]][fsid][a_attr], 1.0)

        for a_attr in ['mean', 'median']:
            self.assertEqual(acc[correct_class_uris[1]][2][a_attr], -1)

        for a_attr in ['mean', 'median']:
            self.assertEqual(acc[correct_class_uris[1]][1][a_attr], 1.0)

        # Birds
        for fsid in range(1, 5):
            self.assertIn(fsid, acc[correct_class_uris[2]])
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[correct_class_uris[2]][fsid][a_attr], -1)

    def test_swimmer(self):
        annotator = acp.annotate_column("tests/swimmers.csv", 0, False)
        class_uri = "http://dbpedia.org/ontology/Swimmer"

        candidates = acp.predict_class(annotator, 1, 0.0001)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 2, 0.0001)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 3, 0.001)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 4, 0.1)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 5, 1.0)
        self.assertNotEqual(class_uri, candidates[0])

        annotator = acp.annotate_column("tests/swimmers2.csv", 0, False)
        class_uri = "http://dbpedia.org/ontology/Swimmer"

        candidates = acp.predict_class(annotator, 1, 0.0001)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 2, 0.0001)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 3, 0.001)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 4, 0.1)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 5, 1.0)
        self.assertNotEqual(class_uri, candidates[0])

    def test_golfer(self):
        annotator = acp.annotate_column("tests/golfplayers.csv", 0, False)
        class_uri = "http://dbpedia.org/ontology/GolfPlayer"

        candidates = acp.predict_class(annotator, 1, 0.0001)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 2, 0.0001)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 3, 0.001)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 4, 0.1)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 5, 1.0)
        self.assertNotEqual(class_uri, candidates[0])

        annotator = acp.annotate_column("tests/golfplayers2.csv", 0, False)
        class_uri = "http://dbpedia.org/ontology/GolfPlayer"

        candidates = acp.predict_class(annotator, 1, 0.0001)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 2, 0.0001)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 3, 0.001)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 4, 0.1)
        self.assertEqual(class_uri, candidates[0])

        candidates = acp.predict_class(annotator, 5, 1.0)
        self.assertNotEqual(class_uri, candidates[0])
