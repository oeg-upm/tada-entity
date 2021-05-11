from django.test import TestCase
from commons import easysparql, ENDPOINT


class EasySPARQLTest(TestCase):

    def setUp(self):
        pass

    def test_get_parents(self):
        class_uri = "http://dbpedia.org/ontology/Person"
        parents = easysparql.get_parents_of_class(class_uri, ENDPOINT)
        print("parents: ")
        print(parents)
        self.assertGreater(len(parents), 0)



