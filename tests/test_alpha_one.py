import os
from unittest import TestCase
import annotator
import commons
from annotator.annot import Annotator
import experiments.alpha_eval_one as aone
import math
import pandas as pd


class AlphaOneTest(TestCase):

    def test_compute_class_alpha_accuracy(self):
        arr = [
            ["abc1.txt", 0, 0, 0.1, 0.2],
            ["abc2.txt", 0, 0, 0.8, 0.9],
            ["abc3.txt", 0, 0, 0.7, 0.9],
        ]
        df = pd.DataFrame(arr, columns=['fname', 'colid', 'fsid', 'from_alpha', 'to_alpha'])
        acc = aone.compute_class_alpha_accuracy(df, {'mean': 0.85, 'median': 0.82})
        self.assertEqual(acc['mean'], 2.0/3)

    def test_compute_accuracy_for_all_classes(self):
        arr = [
            ["abc1.txt", 0, 0, 0.1, 0.2],
            ["abc2.txt", 0, 0, 0.8, 0.9],
            ["abc3.txt", 0, 0, 0.7, 0.9],
            ["abc4.txt", 0, 0, 0.1, 0.2],
            ["abc5.txt", 0, 0, 0.8, 0.9],
            ["abc6.txt", 0, 0, 0.7, 0.9],
        ]
        df = pd.DataFrame(arr, columns=['fname', 'colid', 'fsid', 'from_alpha', 'to_alpha'])
        classes_fnames = {
            'cls1': ["abc1.txt", "abc2.txt", "abc3.txt"],
            'cls2': ["abc4.txt", "abc5.txt", "abc6.txt"]
        }
        classes = {'cls1': {'mean': 0.85, 'median': 0.86}, 'cls2': {'mean': 0.15, 'median': 0.15}}
        acc = aone.compute_accuracy_for_all_classes(df, classes, classes_fnames)
        # print(acc)
        gs = {
            'cls1': {
                'mean': 2.0/3
            },
            'cls2': {
                'mean': 1.0/3
            }
        }
        for c in classes:
            self.assertEqual(acc[c]['mean'], gs[c]['mean'])
