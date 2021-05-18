import os
from django.test import TestCase
from tadae.models import *
import annotator
import commons
from tadae.settings import BASE_DIR
from annotator.annot import Annotator


class AnnotatorTest(TestCase):
    def setUp(self):
        pass

    def test_remove_unwanted_parent(self):
        annotator = Annotator(endpoint=commons.ENDPOINT)
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
        annotator = Annotator(endpoint=commons.ENDPOINT)
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
        # print("ancestors: ")
        # print(annotator.ancestors.keys())
        self.assertCountEqual(annotator.ancestors["Thing"], [])

    def test_coverage(self):
        annotator = Annotator()
        annotator.cell_ent_class = {
            "CellAB": {
                "entityA": ["classA1", "classA2", "classA3"],
                "entityB": ["classB1", "classB2"]
            },
            "CellX": {
                "EntityX": ["classX", "classA3"],
                "EntityY": [],
            }
        }

        annotator.tgraph.add_class("Thing")
        annotator.tgraph.add_class("classA1")
        annotator.tgraph.add_class("classA2")
        annotator.tgraph.add_class("classA3")
        annotator.tgraph.add_class("classB1")
        annotator.tgraph.add_class("classB2")
        annotator.tgraph.add_class("classX")

        annotator.tgraph.add_parent("classA3", "classA2")
        annotator.tgraph.add_parent("classA2", "classA1")
        annotator.tgraph.add_parent("classB2", "classB1")
        annotator.tgraph.add_parent("classB1", "Thing")
        annotator.tgraph.add_parent("classA1", "Thing")
        annotator.tgraph.add_parent("classX", "Thing")
        for cell in annotator.cell_ent_class:
            d = annotator.cell_ent_class[cell]
            annotator.build_ancestors_lookup()
            new_d = annotator.remove_unwanted_parent_classes_for_cell(d)
            # print("before")
            # print(d)
            # print("after")
            # print(new_d)
            annotator.cell_ent_class[cell] = new_d
        annotator.compute_coverage()
        self.assertCountEqual(annotator.ancestors["classA3"], ["classA1", "classA2", "Thing"])
        self.assertCountEqual(annotator.ancestors["classA2"], ["classA1", "Thing"])
        self.assertCountEqual(annotator.ancestors["classB2"], ["classB1", "Thing"])
        self.assertCountEqual(annotator.ancestors["classX"], ["Thing"])
        self.assertCountEqual(annotator.ancestors["Thing"], [])
        # Ic
        self.assertAlmostEqual(annotator.tgraph.nodes["classX"].Ic, 0.25)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA3"].Ic, 0.75)
        self.assertAlmostEqual(annotator.tgraph.nodes["classB2"].Ic, 0.5)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA1"].Ic, 0)
        # Lc
        self.assertAlmostEqual(annotator.tgraph.nodes["classX"].Lc, 0.25)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA3"].Lc, 0.75)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA2"].Lc, 0.75)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA1"].Lc, 0.75)
        self.assertAlmostEqual(annotator.tgraph.nodes["classB2"].Lc, 0.5)
        self.assertAlmostEqual(annotator.tgraph.nodes["classB1"].Lc, 0.5)
        self.assertAlmostEqual(annotator.tgraph.nodes["Thing"].Lc, annotator.tgraph.nodes["classX"].Lc +
                               annotator.tgraph.nodes["classA3"].Lc + annotator.tgraph.nodes["classB2"].Lc)
        # m
        self.assertEqual(annotator.tgraph.m, 2)
        # fc
        self.assertAlmostEqual(annotator.tgraph.nodes["classX"].fc, 0.25 / 2)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA3"].fc, 0.75 / 2)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA2"].fc, 0.75 / 2)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA1"].fc, 0.75 / 2)
        self.assertAlmostEqual(annotator.tgraph.nodes["classB2"].fc, 0.5 / 2)
        self.assertAlmostEqual(annotator.tgraph.nodes["classB1"].fc, 0.5 / 2)
        self.assertAlmostEqual(annotator.tgraph.nodes["Thing"].fc, 1.5 / 2)

    def test_specificity(self):
        annotator = Annotator()
        annotator.cell_ent_class = {
            "CellAB": {
                "entityA": ["classA1", "classA2", "classA3"],
                "entityB": ["classB1", "classB2"]
            },
            "CellX": {
                "EntityX": ["classX", "classA3"],
                "EntityY": [],
            }
        }

        annotator.tgraph.add_class("Thing")
        annotator.tgraph.add_class("classA1")
        annotator.tgraph.add_class("classA2")
        annotator.tgraph.add_class("classA3")
        annotator.tgraph.add_class("classB1")
        annotator.tgraph.add_class("classB2")
        annotator.tgraph.add_class("classX")

        annotator.tgraph.add_parent("classA3", "classA2")
        annotator.tgraph.add_parent("classA2", "classA1")
        annotator.tgraph.add_parent("classB2", "classB1")
        annotator.tgraph.add_parent("classB1", "Thing")
        annotator.tgraph.add_parent("classA1", "Thing")
        annotator.tgraph.add_parent("classX", "Thing")
        for cell in annotator.cell_ent_class:
            d = annotator.cell_ent_class[cell]
            annotator.build_ancestors_lookup()
            new_d = annotator.remove_unwanted_parent_classes_for_cell(d)
            # print("before")
            # print(d)
            # print("after")
            # print(new_d)
            annotator.cell_ent_class[cell] = new_d

        annotator.classes_counts["classB2"] = 35
        annotator.classes_counts["classB1"] = annotator.classes_counts["classB2"] + 17

        annotator.classes_counts["classA3"] = 30
        annotator.classes_counts["classA2"] = annotator.classes_counts["classA3"] + 10
        annotator.classes_counts["classA1"] = annotator.classes_counts["classA2"] + 10

        annotator.classes_counts["classX"] = 10

        annotator.classes_counts["Thing"] = annotator.classes_counts["classX"] + annotator.classes_counts["classA1"] + \
                                            annotator.classes_counts["classB1"]

        annotator.compute_Is()
        annotator.compute_Ls()
        annotator.compute_fs()
        # Is
        self.assertAlmostEqual(annotator.tgraph.nodes["classX"].Is, 10.0 / 112)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA1"].Is, 50.0 / 112)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA3"].Is, 30.0 / 40)
        self.assertAlmostEqual(annotator.tgraph.nodes["classB2"].Is, 35.0 / 52)
        # Ls
        self.assertAlmostEqual(annotator.tgraph.nodes["classX"].Ls, 10.0 / 112)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA3"].Ls, 50.0 / 112 * 40.0 / 50 * 30.0 / 40)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA1"].Ls, 50.0 / 112)
        self.assertAlmostEqual(annotator.tgraph.nodes["classB2"].Ls, 35.0 / 52 * 52.0 / 112)
        self.assertAlmostEqual(annotator.tgraph.nodes["classB1"].Ls, 52.0 / 112)
        # fs
        self.assertAlmostEqual(annotator.tgraph.nodes["classX"].fs, -10.0 / 112 + 1)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA3"].fs, -50.0 / 112 * 40.0 / 50 * 30.0 / 40 + 1)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA2"].fs, -50.0 / 112 * 40.0 / 50 + 1)
        self.assertAlmostEqual(annotator.tgraph.nodes["classA1"].fs, -50.0 / 112 + 1)
        self.assertAlmostEqual(annotator.tgraph.nodes["classB2"].fs, -35.0 / 52 * 52.0 / 112 + 1)
        self.assertAlmostEqual(annotator.tgraph.nodes["classB1"].fs, -52.0 / 112 + 1)
        self.assertAlmostEqual(annotator.tgraph.nodes["Thing"].fs, 0)

    def test_f(self):
        annotator = Annotator()
        annotator.cell_ent_class = {
            "CellAB": {
                "entityA": ["classA1", "classA2", "classA3"],
                "entityB": ["classB1", "classB2"]
            },
            "CellX": {
                "EntityX": ["classX", "classA3"],
                "EntityY": [],
            }
        }

        annotator.tgraph.add_class("Thing")
        annotator.tgraph.add_class("classA1")
        annotator.tgraph.add_class("classA2")
        annotator.tgraph.add_class("classA3")
        annotator.tgraph.add_class("classB1")
        annotator.tgraph.add_class("classB2")
        annotator.tgraph.add_class("classX")

        annotator.tgraph.add_parent("classA3", "classA2")
        annotator.tgraph.add_parent("classA2", "classA1")
        annotator.tgraph.add_parent("classB2", "classB1")
        annotator.tgraph.add_parent("classB1", "Thing")
        annotator.tgraph.add_parent("classA1", "Thing")
        annotator.tgraph.add_parent("classX", "Thing")
        for cell in annotator.cell_ent_class:
            d = annotator.cell_ent_class[cell]
            annotator.build_ancestors_lookup()
            new_d = annotator.remove_unwanted_parent_classes_for_cell(d)
            # print("before")
            # print(d)
            # print("after")
            # print(new_d)
            annotator.cell_ent_class[cell] = new_d

        annotator.tgraph.nodes["classX"].fs = -10.0 / 112 + 1
        annotator.tgraph.nodes["classA3"].fs = -50.0 / 112 * 40.0 / 50 * 30.0 / 40 + 1
        annotator.tgraph.nodes["classA2"].fs = -50.0 / 112 * 40.0 / 50
        annotator.tgraph.nodes["classA1"].fs = -50.0 / 112 + 1
        annotator.tgraph.nodes["classB2"].fs = -35.0 / 52 * 52.0 / 112 + 1
        annotator.tgraph.nodes["classB1"].fs = -52.0 / 112 + 1
        annotator.tgraph.nodes["Thing"].fs = 0

        annotator.tgraph.nodes["classX"].fc = 0.25 / 2
        annotator.tgraph.nodes["classA3"].fc = 0.75 / 2
        annotator.tgraph.nodes["classA2"].fc = 0.75 / 2
        annotator.tgraph.nodes["classA1"].fc = 0.75 / 2
        annotator.tgraph.nodes["classB2"].fc = 0.5 / 2
        annotator.tgraph.nodes["classB1"].fc = 0.5 / 2
        annotator.tgraph.nodes["Thing"].fc = 1.5 / 2

        annotator.compute_f(0.5)

        self.assertCountEqual(annotator.get_top_k(1), ["classA3"])

    # def test_annotate_csv(self):
    #     annotator = Annotator(endpoint=commons.ENDPOINT)
    #     annotator.annotate_table(file_dir="tests/swimmers.csv")
