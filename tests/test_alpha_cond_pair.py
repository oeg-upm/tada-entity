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
        print(candidates)
        self.assertGreater(len(candidates), 0)
        self.assertEqual(candidates[0], 'http://dbpedia.org/ontology/Swimmer')

    def test_add_alpha_per_file(self):
        df = pd.read_csv('tests/alpha_test_1.csv')
        df2 = pd.DataFrame([['swimmers-new.csv', 0, 1, -1, -1]], columns=['fname','colid','fsid','from_alpha','to_alpha'])
        df = df.append(df2, ignore_index=True)
        print(df)
        acp.add_alpha_per_file(df)
        for idx, row in df.iterrows():
            self.assertIn('alpha', row)
        # print(df)
        alphas = list(df['alpha'])
        self.assertIn(-1, alphas)

    def test_compute_file_acc(self):
        df = pd.read_csv('tests/alpha_test_2.csv')
        acc = None
        # alphas_classes = {
        #     1: {'mean': 0.1, 'median': 0.1},
        #     2: {'mean': 0.1, 'median': 0.1},
        #     3: {'mean': 0.1, 'median': 0.1},
        #     4: {'mean': 0.1, 'median': 0.1},
        #     5: {'mean': 0.1, 'median': 0.1}
        # }
        data_path = "tests"
        correct_class_uri = "http://dbpedia.org/ontology/Swimmer"
        # alphas_classes = {
        #     "http://dbpedia.org/ontology/Swimmer": [["swimmers.csv",0], ["swimmers2.csv", 0]],
        #     "http://dbpedia.org/ontology/GolfPlayer": [["goldplayers.csv",0], ["golfplayers2.csv", 0]]
        # }
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
        #
        # print("acc: ")
        # print(acc)

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

        class_files_alpha = acp.get_class_files_alphas(df)

        for idx, row in df.iterrows():
            acc = acp.get_file_acc(row, class_files_alpha, alphas_classes, correct_class_uri, False, data_path)
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
            acc = acp.get_file_acc(row, swimmers_files_alpha, alphas_classes, correct_class_uri, False, data_path)
            break

        for fsid in range(1, 6):
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[fsid][a_attr], 1)

        for idx, row in df_golfers.iterrows():
            acc = acp.get_file_acc(row, golfers_files_alpha, alphas_classes, correct_class_uri2, False, data_path)
            break
        # print(acc)
        for fsid in range(1, 6):
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[fsid][a_attr], 1)

        for idx, row in df_birds.iterrows():
            acc = acp.get_file_acc(row, birds_files_alpha, alphas_classes, correct_class_uri3, False, data_path)
            break
        # print(acc)
        for fsid in range(1, 6):
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
            acc = acp.get_file_acc(row, swimmers_files_alpha, alphas_classes, correct_class_uri, False, data_path)
            break

        for fsid in range(1, 6):
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[fsid][a_attr], 1)

        for idx, row in df_golfers.iterrows():
            acc = acp.get_file_acc(row, golfers_files_alpha, alphas_classes, correct_class_uri2, False, data_path)
            break
        # print(acc)
        for fsid in range(1, 6):
            for a_attr in ['mean', 'median']:
                self.assertEqual(acc[fsid][a_attr], 1)

        for idx, row in df_birds.iterrows():
            acc = acp.get_file_acc(row, birds_files_alpha, alphas_classes, correct_class_uri3, False, data_path)
            break
        # print(acc)
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
                "http://dbpedia.org/ontology/GolfPlayer": {'mean': 0.99, 'median': 0.99},
                "http://dbpedia.org/ontology/Bird": {'mean': 0.99, 'median': 0.99}

            },
        }

        df_swimmers = df[df.fname.isin(['swimmers.csv', 'swimmers2.csv'])]
        df_golfers = df[df.fname.isin(['golfplayers.csv', 'golfplayers2.csv'])]
        df_birds = df[df.fname.isin(['birds.csv', 'birds2.csv'])]

        dfs = [df_swimmers, df_golfers, df_birds]

        for idx, df in enumerate(dfs):
            acc[idx] = acp.get_acc_per_class(df, alphas_classes, correct_class_uris[idx], False, data_path)

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
