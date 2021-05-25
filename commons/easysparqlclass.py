from SPARQLWrapper import SPARQLWrapper, JSON

import certifi

# from __init__ import QUERY_LIMIT
QUERY_LIMIT = ""

import pandas as pd
import numpy as np

class EasySparql:

    def __init__(self, endpoint=None, sparql_flavor="dbpedia"):
        self.endpoint = endpoint

    def run_query(self, query=None, raiseexception=False, printempty=False):
        """
        :param query: raw SPARQL query
        :param endpoint: endpoint source that hosts the data
        :return: query result as a dict
        """
        if self.endpoint is None:
            print("endpoints cannot be None")
            return []
        sparql = SPARQLWrapper(endpoint=self.endpoint, custom_cert_filename=certifi.where())
        sparql.setQuery(query=query)
        # sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        # sparql.setTimeout(300)
        try:
            results = sparql.query().convert()
            if len(results["results"]["bindings"]) > 0:
                return results["results"]["bindings"]
            else:
                if printempty:
                    print("returns 0 rows")
                    print("endpoint: " + self.endpoint)
                    print("query: <%s>" % str(query).strip())
                return []
        except Exception as e:
            print(str(e))
            print("sparql error: $$<%s>$$" % str(e))
            print("query: $$<%s>$$" % str(query))
            if raiseexception:
                raise e
            return []

    def get_entities_and_classes(self, subject_name, attributes):
        """
        :param subject_name:
        :param attributes:
        :param endpoint: the SPARQL endpoint
        :return:
        """
        inner_qs = []
        csubject = self.clean_text(subject_name)
        for attr in attributes:
            cattr = self.clean_text(attr)
            q = """
                {
                    ?s rdfs:label "%s"@en.
                    ?s ?p "%s"@en.
                    ?s a ?c.
                } UNION {
                    ?s rdfs:label "%s"@en.
                    ?s ?p ?e.
                    ?e rdfs:label "%s"@en.
                    ?s a ?c.
                }
            """ % (csubject, cattr, csubject, cattr)
            inner_qs.append(q)

        inner_q = "UNION".join(inner_qs)

        query = """
            select distinct ?s ?c where{
                %s
            }
        """ % (inner_q)
        results = self.run_query(query=query)
        try:
            entity_class_pair = [(r['s']['value'], r['c']['value']) for r in results]
        except:
            entity_class_pair = []
        return entity_class_pair

    def get_entities_and_classes_naive(self, subject_name):
        """
        assuming only in the form of name@en. To be extended to other languages and other types e.g. name^^someurltype
        :param subject_name:
        :return:
        """
        csubject = self.clean_text(subject_name)
        if self.sparql_flavor == "dbpedia":
            query = """
                select distinct ?s ?c where{
                    ?s ?p "%s"@en.
                    ?s a ?c
                }
            """ % csubject
        elif self.sparql_flavor == "wikidata":
            query = """
                select distinct ?s ?c where{
                    ?s ?p "%s"@en.
                    ?s wdt:P31 ?c
                }
            """ % csubject
        results = self.run_query(query=query)
        # entity_class_pair = [(r['s']['value'], r['c']['value']) for r in results]
        try:
            entity_class_pair = [(r['s']['value'], r['c']['value']) for r in results]
        except:
            entity_class_pair = []

        return entity_class_pair

    def get_parents_of_class(self, class_name):
        """
        get the parent class of the given class, get the first results in case of multiple ones
        :param class_name:
        :param endpoint:
        :return:
        """
        if self.sparql_flavor == "dbpedia":
            query = """
            select distinct ?c where{
            <%s> rdfs:subClassOf ?c.
            }
            """ % class_name
        elif self.sparql_flavor == "wikidata":
            query = """
            select distinct ?c where{
            <%s> wdt:P279 ?c.
            }
            """ % class_name
        results = self.run_query(query=query)
        classes = [r['c']['value'] for r in results]
        return classes

    def get_num_class_subjects(self, class_uri):
        # print("count subject for class %s" % class_uri)
        query = """
        select count(?s) as ?num
        where {
        ?s a ?c.
        ?c rdfs:subClassOf* <%s>.
        }
        """ % class_uri
        results = self.run_query(query=query)
        return results[0]['num']['value']

    def clean_text(text):
        ctext = text.replace('"', '')
        ctext = ctext.replace("'", "")
        ctext = ctext.strip()
        return ctext


def get_url_stripped(uri):
    """
    :param uri:  <myuri> or uri
    :return: myuri
    """
    uri_stripped = uri.strip()
    if uri_stripped[0] == "<":
        uri_stripped = uri_stripped[1:]
    if uri_stripped[-1] == ">":
        uri_stripped = uri_stripped[:-1]
    return uri_stripped
