from django.test import TestCase
from django.urls import reverse

from tadae.models import *
import annotator
import commons
from tadae.settings import BASE_DIR


class AnnotateColTest(TestCase):

    def setUp(self):
        ann_run = AnnRun(name="testing-swimmers-file")
        ann_run.save()
        self.ann_run = ann_run
        prefix = "http://dbpedia.org/ontology/"
        csv_file_dir = os.path.join(BASE_DIR, 'tests', 'swimmers.csv')
        annotator.annotate_csv(ann_run_id=ann_run.id, csv_file_dir=csv_file_dir,
                               endpoint=commons.ENDPOINT, hierarchy=False, entity_col_id=0, onlyprefix=prefix,
                               camel_case=False)
        annotator.dotype(ann_run, commons.ENDPOINT, onlyprefix=None)

    def test_col_annotation(self):
        self.assertTrue(True)
        ann_text = """<td>1</td><td><ahref="http://dbpedia.org/ontology/Swimmer">http://dbpedia.org/ontology/Swimmer</a>"""
        response = self.client.get(reverse('ent_ann_recompute')+'?alpha=0.1&ann='+str(self.ann_run.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(ann_text, response.content.replace(' ', '').replace('\n', ''))





