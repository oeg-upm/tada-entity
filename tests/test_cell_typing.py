from django.test import TestCase
from tadae.models import *
import annotator
import commons
from tadae.settings import BASE_DIR


class AnnotateCellsTest(TestCase):
    def setUp(self):
        pass

    def test_cell_annotation(self):
        ann_run = AnnRun(name="testing-swimmers-file")
        ann_run.save()
        prefix = "http://dbpedia.org/ontology/"
        csv_file_dir = os.path.join(BASE_DIR, 'tests', 'swimmers.csv')
        annotator.annotate_csv(ann_run_id=ann_run.id, csv_file_dir=csv_file_dir,
                               endpoint=commons.ENDPOINT,
                              hierarchy=False, entity_col_id=0, onlyprefix=prefix, camel_case=False)
        eanns = ann_run.entityann_set.all()
        self.assertEqual(len(eanns), 1, 'entity annotation is not created for the AnnRun')
        eann = eanns[0]
        cells = eann.cell_set.all()
        f = open(csv_file_dir, "r")
        num_cells = len(f.read().split('\n'))-1  # -1 to ignore the header
        self.assertEqual(num_cells, len(cells))
        agg_annos = []
        for c in cells:
            for e in c.entity_set.all():
                for cc in e.cclass_set.all():
                    agg_annos.append(cc)
        # this is just an approximation to make sure that there are a handful number of classes
        self.assertTrue(len(agg_annos) > num_cells)

    # def test_fail(self):
    #     self.assertTrue(False)
