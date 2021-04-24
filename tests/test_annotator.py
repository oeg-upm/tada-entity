import os
from django.test import TestCase
from tadae.models import *
import annotator
import commons
from tadae.settings import BASE_DIR
from annotator.annotator import Annotator


class AnnotatorTest(TestCase):
    def setUp(self):
        pass

    def test_remove_unwanted_parent(self):
        annotator = Annotator()
        d = dict()
        d["DDD"] = {
            "DD": True,
            "D": True
        }
        d["DD"] = {
            "D": True
        }
        d["D"] = dict()
        d["BB"] = {
            "B": True
        }
        d["B"] = dict()
        annotator.ancestors = d
        wanted_classes = annotator.remove_unwanted_parent_classes_for_entity(["D", "DD"])
        self.assertCountEqual(wanted_classes, ["DD"])
        wanted_classes = annotator.remove_unwanted_parent_classes_for_entity(["D", "DDD"])
        self.assertCountEqual(wanted_classes, ["DDD"])
        wanted_classes = annotator.remove_unwanted_parent_classes_for_entity(["D", "DDD"])
        self.assertCountEqual(wanted_classes, ["DDD"])
        wanted_classes = annotator.remove_unwanted_parent_classes_for_entity(["D", "B", "DDD"])
        self.assertCountEqual(wanted_classes, ["DDD", "B"])
        wanted_classes = annotator.remove_unwanted_parent_classes_for_entity(["D", "B", "DDD", "BB"])
        self.assertCountEqual(wanted_classes, ["DDD", "BB"])

    def test_build_class_graph(self):
        annotator = Annotator()
        d = {
            "entityA": ["classA1", "classA2", "classA3"],
            "entityB": ["classB1", "classB2"]
        }
        for ent in d:
            for class_uri in d[ent]:
                annotator.tgraph.add_class(class_uri)
        annotator.tgraph.add_parent("classA3", "classA2")
        annotator.tgraph.add_parent("classA2", "classA1")
        annotator.tgraph.add_parent("classB2", "classB1")
        annotator.tgraph.add_class("Thing")
        annotator.tgraph.add_parent("classB1", "Thing")
        annotator.tgraph.add_parent("classA1", "Thing")
        annotator.build_class_graph(d)
        annotator.build_ancestors_lookup()
        annotator.remove_unwanted_parent_classes_for_cell(d)
        self.assertCountEqual(annotator.ancestors["classA3"], ["classA1", "classA2", "Thing"])
        self.assertCountEqual(annotator.ancestors["classA2"], ["classA1", "Thing"])
        self.assertCountEqual(annotator.ancestors["classB2"], ["classB1", "Thing"])
        print("ancestors: ")
        print(annotator.ancestors.keys())
        self.assertCountEqual(annotator.ancestors["Thing"], [])

