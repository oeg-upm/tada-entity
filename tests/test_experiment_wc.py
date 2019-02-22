from django.test import TestCase
from tadae.models import *
import annotator
import commons
from tadae.settings import BASE_DIR
from experiments.webcommons_v2.validation import compute_scores


class ExperimentWCTest(TestCase):
    def setUp(self):
        pass

    def test_scoring(self):
        precision, recall, f1 = compute_scores(2, 18, 8)
        self.assertEqual(precision, "0.1000")
        self.assertEqual(recall, "0.2000")
        self.assertEqual(f1, "0.1333")
