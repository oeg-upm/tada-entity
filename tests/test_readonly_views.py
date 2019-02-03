from django.test import TestCase
from django.urls import reverse


class ReadonyViewsTest(TestCase):

    def test_about(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_ent_ann_add(self):
        response = self.client.get(reverse('ent_ann_add'))
        self.assertEqual(response.status_code, 200)

    def test_ent_ann_recompute(self):
        response = self.client.get(reverse('ent_ann_recompute'))
        self.assertEqual(response.status_code, 200)

    # def test_ent_ann_raw_results(self):
    #     response = self.client.get(reverse('ent_ann_raw_results'))
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_ent_ann_stored_results(self):
    #     response = self.client.get(reverse('ent_ann_stored_results'))
    #     self.assertEqual(response.status_code, 200)

    def test_ent_ann_list(self):
        response = self.client.get(reverse('ent_ann_list'))
        self.assertEqual(response.status_code, 200)


