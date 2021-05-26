import os
from django.test import TestCase
from tadae.models import *
import annotator
import commons
from tadae.settings import BASE_DIR
from annotator.annot import Annotator


class AnnotatorOnlineTest(TestCase):
    def setUp(self):
        pass

    def test_ancestors(self):
        annotator = Annotator(endpoint=commons.ENDPOINT)
        annotator.annotate_table(file_dir="tests/swimmers.csv", subject_col_id=0)
        self.assertIn("http://dbpedia.org/ontology/Swimmer", annotator.ancestors)
        sw_ancs = ["http://dbpedia.org/ontology/Athlete", "http://dbpedia.org/ontology/Person",
                   "http://dbpedia.org/ontology/Agent", "http://www.w3.org/2002/07/owl#Thing"]
        for uri in sw_ancs:
            self.assertIn(uri, annotator.ancestors)
        ath_ancs = sw_ancs[1:]
        prs_ancs = ath_ancs[1:]
        agt_ancs = prs_ancs[1:]
        self.assertCountEqual(annotator.ancestors["http://dbpedia.org/ontology/Swimmer"], sw_ancs)
        self.assertCountEqual(annotator.ancestors[sw_ancs[0]], ath_ancs)
        self.assertCountEqual(annotator.ancestors[sw_ancs[1]], prs_ancs)
        self.assertCountEqual(annotator.ancestors[sw_ancs[2]], agt_ancs)

    def test_remove_unwanted_parent(self):
        annotator = Annotator(endpoint=commons.ENDPOINT, alpha=0.4)
        annotator.annotate_table(file_dir="tests/swimmers.csv", subject_col_id=0)

        cell = "Joanne Deakins"
        ent = "http://dbpedia.org/resource/Joanne_Deakins"
        self.assertIn(cell, annotator.cell_ent_class)
        self.assertIn(ent, annotator.cell_ent_class[cell])
        self.assertIn("http://dbpedia.org/ontology/Swimmer", annotator.cell_ent_class[cell][ent])
        self.assertNotIn("http://dbpedia.org/ontology/Athlete", annotator.cell_ent_class[cell][ent])
        self.assertNotIn("http://dbpedia.org/ontology/Person", annotator.cell_ent_class[cell][ent])
        self.assertNotIn("http://dbpedia.org/ontology/Agent", annotator.cell_ent_class[cell][ent])
        self.assertNotIn("http://www.w3.org/2002/07/owl#Thing", annotator.cell_ent_class[cell][ent])

        cell = "Billy Fiske"
        ent = "http://dbpedia.org/resource/Billy_Fiske"
        self.assertIn(cell, annotator.cell_ent_class)
        self.assertIn(ent, annotator.cell_ent_class[cell])
        self.assertIn("http://dbpedia.org/ontology/MilitaryPerson", annotator.cell_ent_class[cell][ent])
        self.assertNotIn("http://dbpedia.org/ontology/Person", annotator.cell_ent_class[cell][ent])
        self.assertNotIn("http://dbpedia.org/ontology/Agent", annotator.cell_ent_class[cell][ent])
        self.assertNotIn("http://www.w3.org/2002/07/owl#Thing", annotator.cell_ent_class[cell][ent])

    def test_coverage(self):
        annotator = Annotator(endpoint=commons.ENDPOINT, alpha=0.4,
            class_prefs=["http://dbpedia.org/ontology/", "http://www.w3.org/2002/07/owl#Thing"])
        annotator.annotate_table(file_dir="tests/swimmers.csv", subject_col_id=0)
        annotator.compute_coverage()
        # Ic
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].Ic, 3)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/MilitaryPerson"].Ic, 2)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Ic, 5)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Ic, 0)
        # Lc
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].Lc, 10)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/MilitaryPerson"].Lc, 2)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Lc, 5)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Lc, 10)
        # m
        self.assertEqual(annotator.tgraph.m, 10)
        # fc
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].fc,
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].Lc /annotator.tgraph.m)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/MilitaryPerson"].fc,
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/MilitaryPerson"].Lc/annotator.tgraph.m)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].fc,
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Lc/annotator.tgraph.m)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].fc,
                               annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Lc/annotator.tgraph.m)

        annotator.clear_for_reuse()

        annotator.annotate_table(file_dir="tests/swimmers.csv", subject_col_id=0)
        annotator.compute_coverage()
        # Ic
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].Ic, 3)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/MilitaryPerson"].Ic, 2)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Ic, 5)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Ic, 0)
        # Lc
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].Lc, 10)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/MilitaryPerson"].Lc, 2)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Lc, 5)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Lc, 10)
        # m
        self.assertEqual(annotator.tgraph.m, 10)
        # fc
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].fc,
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].Lc /annotator.tgraph.m)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/MilitaryPerson"].fc,
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/MilitaryPerson"].Lc/annotator.tgraph.m)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].fc,
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Lc/annotator.tgraph.m)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].fc,
                               annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Lc/annotator.tgraph.m)

    def test_specificity(self):
        annotator = Annotator(endpoint=commons.ENDPOINT, alpha=0.4)
        annotator.annotate_table(file_dir="tests/swimmers.csv", subject_col_id=0)

        num_swim = 5299.0
        num_ath = 720676.0
        num_psn = 3386396.0

        annotator.compute_Is()
        annotator.compute_Ls()
        annotator.compute_fs()

        # Is
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Is, num_swim/num_ath)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Athlete"].Is, num_ath/num_psn)
        # self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].Is, 30.0 / 40)
        # self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Agent"].Is, 35.0 / 52)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Is, 1.0)
        # Ls
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Ls,
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Is *
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/Athlete"].Ls)

        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Athlete"].Ls,
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/Athlete"].Is *
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].Ls)

        # self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].Ls, 50.0 / 112)
        # self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Agent"].Ls, 35.0 / 52 * 52.0 / 112)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Ls,
                               annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Is)
        # fs
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].fs[3],
                               -annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Ls + 1)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Athlete"].fs[3],
                               -annotator.tgraph.nodes["http://dbpedia.org/ontology/Athlete"].Ls + 1)
        # self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].fs, -50.0 / 112 * 40.0 / 50 + 1)
        # self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Agent"].fs, -50.0 / 112 + 1)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].fs[3],
                               -annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Ls + 1)

        annotator.clear_for_reuse()

        annotator.annotate_table(file_dir="tests/swimmers.csv", subject_col_id=0)

        annotator.compute_Is()
        annotator.compute_Ls()
        annotator.compute_fs()

        # Is
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Is, num_swim/num_ath)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Athlete"].Is, num_ath/num_psn)
        # self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].Is, 30.0 / 40)
        # self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Agent"].Is, 35.0 / 52)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Is, 1.0)
        # Ls
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Ls,
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Is *
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/Athlete"].Ls)

        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Athlete"].Ls,
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/Athlete"].Is *
                               annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].Ls)

        # self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].Ls, 50.0 / 112)
        # self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Agent"].Ls, 35.0 / 52 * 52.0 / 112)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Ls,
                               annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Is)
        # fs
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].fs[3],
                               -annotator.tgraph.nodes["http://dbpedia.org/ontology/Swimmer"].Ls + 1)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Athlete"].fs[3],
                               -annotator.tgraph.nodes["http://dbpedia.org/ontology/Athlete"].Ls + 1)
        # self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Person"].fs, -50.0 / 112 * 40.0 / 50 + 1)
        # self.assertAlmostEqual(annotator.tgraph.nodes["http://dbpedia.org/ontology/Agent"].fs, -50.0 / 112 + 1)
        self.assertAlmostEqual(annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].fs[3],
                               -annotator.tgraph.nodes["http://www.w3.org/2002/07/owl#Thing"].Ls + 1)

    def test_f(self):
        annotator = Annotator(endpoint=commons.ENDPOINT, alpha=0.4)
        annotator.annotate_table(file_dir="tests/swimmers.csv", subject_col_id=0)

        annotator.compute_f(0.3)

        self.assertCountEqual(annotator.get_top_k(k=1, fsid=3), ["http://dbpedia.org/ontology/Swimmer"])
