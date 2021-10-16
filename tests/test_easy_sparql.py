from unittest import TestCase
from commons import ENDPOINT
from easysparql import easysparql
from easysparql import cacher
from easysparql.easysparqlclass import EasySparql



# from commons.easysparqlclass import EasySparql


class EasySPARQLTest(TestCase):

    def setUp(self):
        pass

    def test_get_parents(self):
        class_uri = "http://dbpedia.org/ontology/Person"
        parents = easysparql.get_parents_of_class(class_uri, ENDPOINT)
        # print("parents: ")
        # print(parents)
        self.assertGreater(len(parents), 0)

    def test_get_parents_from_class(self):
        eaql = EasySparql(ENDPOINT)
        class_uri = "http://dbpedia.org/ontology/Person"
        parents = eaql.get_parents_of_class(class_uri)
        # print("parents: ")
        # print(parents)
        self.assertGreater(len(parents), 0)

