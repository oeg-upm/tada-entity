from SPARQLWrapper import SPARQLWrapper, JSON

# import certifi

# from __init__ import QUERY_LIMIT
QUERY_LIMIT = ""

import pandas as pd
import numpy as np


def run_query_with_datatype(query=None, endpoint=None, datatype=None):
    """
    :param query: raw SPARQL query
    :param endpoint: endpoint source that hosts the data
    :param datatype: e.g. "http://dbpedia.org/datatype/centimetre" if None, it will return all datatypes
    :return: query results with the matching datatype, query results not matching the given datatype
    """
    results = run_query(query=query, endpoint=endpoint)
    if len(results) > 0:
        if len(results[0].keys()) == 1:
            k = results[0].keys()[0]
            if datatype is None:
                correct_type_results = [r[k]["value"] for r in results]
                wrong_type_results = []
            else:
                correct_type_results = [r[k]["value"] for r in results if r[k]["datatype"] == datatype]
                wrong_type_results = [r[k]["value"] for r in results if r[k]["datatype"] != datatype]
            return correct_type_results, wrong_type_results
        else:
            print("a query that results in multiple columns is not allowed")
            # Because, if we allow having multiple columns, and the number of values in the first column
            # that matches the given datatype might not be the same as the one in the second column
            # which would results in unbalanced results
    return [], []


def run_query(query=None, endpoint=None, raiseexception=False, printempty=False):
    """
    :param query: raw SPARQL query
    :param endpoint: endpoint source that hosts the data
    :return: query result as a dict
    """
    if endpoint is None:
        print("endpoints cannot be None")
        return []
    # print("endpoint <%s>" % endpoint)
    sparql = SPARQLWrapper(endpoint=endpoint)
    # sparql = SPARQLWrapper(endpoint=endpoint, custom_cert_filename=certifi.where())
    # sparql = SPARQLWrapper(endpoint=endpoint)
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
                print("endpoint: " + endpoint)
                print("query: <%s>" % str(query).strip())
            return []
    except Exception as e:
        print(str(e))
        print("sparql error: $$<%s>$$" % str(e))
        print("query: $$<%s>$$" % str(query))
        if raiseexception:
            raise e
        return []


def get_properties(endpoint=None, class_uri=None, min_count=20):
    """
    :param endpoint: the meta endpoint
    :param class_uri: with or without < and >
    :param min_count:
    :return: returns the properties and can be accessed as follows: properties[idx]['property']['value']
    """
    class_uri_stripped = get_url_stripped(class_uri)

    query = """
    prefix loupe: <http://ont-loupe.linkeddata.es/def/core/>
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>
        select distinct ?p as ?property ?count where {
          graph <http://data.loupe.linked.es/dbpedia/1> {
            ?pp loupe:aboutClass <%s>;
                loupe:aboutProperty ?p;
                loupe:hasDatatypePartition ?pdp;
                loupe:objectCount ?count .
            {
            ?pdp loupe:datatype xsd:double .
            } UNION {
            ?pdp loupe:datatype xsd:integer .
            } UNION {
            ?pdp loupe:datatype xsd:decimal .
            }
           FILTER(?count > %d)
         }
        }
        ORDER BY desc(?count)
        %s
    """ % (class_uri_stripped, min_count, QUERY_LIMIT)
    properties = run_query(query=query, endpoint=endpoint)
    return properties


def get_properties_as_list(endpoint=None, class_uri=None, min_count=20):
    properties = get_properties(endpoint=endpoint, class_uri=class_uri, min_count=min_count)
    clean_properties = [p['property'] for p in properties]
    return pd.DataFrame(clean_properties)['value']


def get_objects(endpoint=None, class_uri=None, property_uri=None, isnumericfilter=True, failbacknofilter=True):
    class_uri_stripped = class_uri.strip()
    if class_uri_stripped[0] == "<" and class_uri_stripped[-1] == ">":
        class_uri_stripped = class_uri_stripped[1:-1]
    property_uri_stripped = property_uri.strip()
    if property_uri_stripped[0] == "<" and property_uri_stripped[-1] == ">":
        property_uri_stripped = property_uri_stripped[1:-1]
    if isnumericfilter:
        try:
            query = """
                select ?o where{ ?s  a <%s>. ?s <%s> ?o FILTER(isNumeric(?o))} %s
            """ % (class_uri_stripped, property_uri_stripped, QUERY_LIMIT)
            objects = run_query(query=query, endpoint=endpoint, raiseexception=True)
        except Exception as e:
            if failbacknofilter:
                print("fail back ... ")
                query = """
                    select ?o where{ ?s  a <%s>. ?s <%s> ?o} %s
                """ % (class_uri_stripped, property_uri_stripped, QUERY_LIMIT)
                objects = run_query(query=query, endpoint=endpoint)
    else:
        query = """
            select ?o where{ ?s  a <%s>. ?s <%s> ?o} %s
        """ % (class_uri_stripped, property_uri_stripped, QUERY_LIMIT)
        objects = run_query(query=query, endpoint=endpoint)

    return objects


def get_objects_as_list(endpoint=None, class_uri=None, property_uri=None, isnumericfilter=True):
    objects = get_objects(endpoint=endpoint, class_uri=class_uri, property_uri=property_uri,
                          isnumericfilter=isnumericfilter)
    clean_objects = [o['o'] for o in objects]
    if len(clean_objects) == 0:
        print("no objects found for class %s property %s in endpoint %s" % (class_uri, property_uri, endpoint))
        col_mat = pd.DataFrame([]).as_matrix()
        col_mat.shape = (0, 0)
        return col_mat

    # to get rid of the strings that can not be transformed into numbers
    col_mat = pd.DataFrame(clean_objects)['value'].apply(pd.to_numeric, errors='coerce').dropna(how='any').as_matrix()
    col_mat.shape = (col_mat.shape[0], 1)
    col_mat = col_mat.astype(np.float)
    # remove nan is any source: http://stackoverflow.com/questions/11620914/removing-nan-values-from-an-array
    col_mat_num = col_mat[~np.isnan(col_mat)]
    col_mat_num.shape = (col_mat_num.shape[0], 1)
    if (col_mat.shape[0] - col_mat_num.shape[0]) < col_mat_num.shape[0]:  # to check how clean is the data
        return col_mat_num
    else:
        a = np.array([])
        a.shape = (0, 1)
        return a


def get_classes(endpoint=None):
    if endpoint is None:
        raise Exception("get_classes> endpoint should not be None")
    query = """
        select distinct ?Concept where { [] a ?Concept}
    """
    results = run_query(endpoint=endpoint, query=query, raiseexception=True)
    classes = [r['Concept']['value'] for r in results]
    return classes


################################################################
#                  Property Extraction A-BOX                   #
################################################################


def split_upper_lower_bound(upper_bound=None, lower_bound=None, class_uri=None, endpoint=None, raiseexception=None,
                            isnumericfilter=None):
    if upper_bound is None:
        raise Exception("split_upper_lower_bound> upper_bound should not be None")
    if lower_bound is None:
        raise Exception("split_upper_lower_bound> lower_bound should not be None")
    if class_uri is None:
        raise Exception("split_upper_lower_bound> class_uri should not be None")
    if endpoint is None:
        raise Exception("split_upper_lower_bound> endpoint should not be None")
    if raiseexception is None:
        raise Exception("split_upper_lower_bound> raiseexception should not be None")
    if isnumericfilter is None:
        raise Exception("split_upper_lower_bound> isnumericfilter should not be None")
    print("-----------  split_upper_lower_bound -----------")
    print("upper_bound: %d" % upper_bound)
    print("lower_bound: %d" % lower_bound)
    print("\n")
    if upper_bound - lower_bound > 2:
        split_point = int((upper_bound - lower_bound) / 2) + lower_bound
        upper_results = get_numerical_properties_for_class_abox_using_half_split(endpoint=endpoint,
                                                                                 class_uri=class_uri,
                                                                                 raiseexception=raiseexception,
                                                                                 lower_bound=lower_bound,
                                                                                 upper_bound=split_point,
                                                                                 first_time=False,
                                                                                 isnumericfilter=isnumericfilter)
        lower_results = get_numerical_properties_for_class_abox_using_half_split(endpoint=endpoint,
                                                                                 class_uri=class_uri,
                                                                                 raiseexception=raiseexception,
                                                                                 lower_bound=split_point,
                                                                                 upper_bound=upper_bound,
                                                                                 first_time=False,
                                                                                 isnumericfilter=isnumericfilter)
        return upper_results + lower_results
    else:
        raise Exception("The endpoint is so slow or the timeout period is very short to query")


def get_numerical_properties_for_class_abox_using_half_split(endpoint=None, class_uri=None,
                                                             upper_bound=None, lower_bound=1,
                                                             raiseexception=False, first_time=None, max_iter=15,
                                                             isnumericfilter=True):
    """
    :param endpoint:
    :param class_uri:
    :param raiseexception:
    :param lower_bound:
    :param upper_bound
    :return:
    """
    if class_uri is None:
        print("get_numerical_properties_for_class_abox_using_half_split> class_uri should not be None")
        return []
    if upper_bound is None:
        print("get_numerical_properties_for_class_abox_using_half_split> upper_bound should not be None")
        return []
    if first_time is None:
        print("get_numerical_properties_for_class_abox_using_half_split> first_time should not be None")
        return []
    # just to see what is going on
    print("==========  get_numerical_properties_for_class_abox_using_half_split =========")
    print("first time: %s" % str(first_time))
    print("upper_bound: %d" % upper_bound)
    print("lower_bound: %d" % lower_bound)
    print("\n")

    class_uri_stripped = get_url_stripped(class_uri)
    if first_time:
        if isnumericfilter:
            query = """
            SELECT ?p ?num
            WHERE{
                FILTER (?num > %d)
                {
                    SELECT ?p (count(distinct ?s) as ?num)
                    WHERE {
                        ?s a <%s>.
                        ?s ?p []
                        }
                        group by ?p
                }
                {
                    SELECT distinct (?p)
                    WHERE{
                        ?s ?p ?o
                        FILTER( isNumeric(?o))
                    }
                }
            }
            order by desc(?num)
            """ % (upper_bound, class_uri_stripped)
        else:
            query = """
            SELECT ?p ?num
            WHERE{
                FILTER (?num > %d)
                {
                    SELECT ?p (count(distinct ?s) as ?num)
                    WHERE {
                        ?s a <%s>.
                        ?s ?p []
                        }
                        group by ?p
                }
            }
            order by desc(?num)
            """ % (upper_bound, class_uri_stripped)

    else:
        if isnumericfilter:
            query = """
            SELECT ?p ?num
            WHERE{
                FILTER (?num >= %d && ?num <= %d)
                {
                    SELECT ?p (count(distinct ?s) as ?num)
                    WHERE {
                        ?s a <%s>.
                        ?s ?p []
                        }
                        group by ?p
                }
                {
                    SELECT distinct (?p)
                    WHERE{
                        ?s ?p ?o
                        FILTER( isNumeric(?o))
                    }
                }
            }
            order by desc(?num)
            """ % (lower_bound, upper_bound, class_uri_stripped)
        else:
            query = """
            SELECT ?p ?num
            WHERE{
                FILTER (?num >= %d && ?num <= %d)
                {
                    SELECT ?p (count(distinct ?s) as ?num)
                    WHERE {
                        ?s a <%s>.
                        ?s ?p []
                        }
                        group by ?p
                }
            }
            order by desc(?num)
            """ % (lower_bound, upper_bound, class_uri_stripped)
    try:
        print("will run the query")
        results = run_query(query=query, endpoint=endpoint, raiseexception=True)
        print("query returned")
        properties = [r['p']['value'] for r in results]
        print("fetching")
        if not first_time:
            print("returning properties")
            print("properties")
            print(properties)
            return properties
        else:  # first time
            print("returning firsttime")
            return properties + split_upper_lower_bound(upper_bound=upper_bound, lower_bound=lower_bound,
                                                        class_uri=class_uri_stripped, endpoint=endpoint,
                                                        raiseexception=raiseexception, isnumericfilter=isnumericfilter)
    except Exception as e:
        if "timed out" in str(e):
            if not first_time:
                return split_upper_lower_bound(upper_bound=upper_bound, lower_bound=lower_bound,
                                               class_uri=class_uri_stripped,
                                               endpoint=endpoint, raiseexception=raiseexception,
                                               isnumericfilter=isnumericfilter)
            else:  # first time
                if max_iter == 0:
                    if raiseexception:
                        raise Exception("reached iteration limit and the timeout still occurs")
                    else:
                        print("reached iteration limit and the timeout still occurs")
                        return []

                return get_numerical_properties_for_class_abox_using_half_split(endpoint=endpoint,
                                                                                class_uri=class_uri_stripped
                                                                                , upper_bound=upper_bound * 2,
                                                                                lower_bound=lower_bound,
                                                                                raiseexception=raiseexception,
                                                                                first_time=True,
                                                                                max_iter=max_iter - 1,
                                                                                isnumericfilter=isnumericfilter)
                # split_upper_lower_bound(upper_bound=upper_bound, lower_bound=lower_bound, class_uri=class_uri_stripped,
                #                         endpoint=endpoint, raiseexception=raiseexception)
        elif "'isNumeric'" in str(e) and first_time:
            print(
                "get_numerical_properties_for_class_abox_using_half_split> isNumeric is not supported, so we gonna ignore it")
            return get_numerical_properties_for_class_abox_using_half_split(endpoint=endpoint, class_uri=class_uri,
                                                                            upper_bound=upper_bound,
                                                                            lower_bound=lower_bound,
                                                                            raiseexception=raiseexception,
                                                                            first_time=first_time, max_iter=max_iter,
                                                                            isnumericfilter=False)
        else:
            if raiseexception:
                print("captured %s" % str(e))
                raise e
            else:
                print("get_numerical_properties_for_class_abox_using_half_split> an exception occurred: %s" % str(e))
                return []


def get_numerical_properties_for_class_abox(endpoint=None, class_uri=None, raiseexception=False):
    """
    a naive approach to get all numerical properties for a given class using the data itself A-BOX
    :param endpoint: endpoint
    :param class_uri: class uri for the class
    :return:
    """

    if class_uri is None:
        print("get_numerical_properties_for_class_abox> class_uri should not be None")
        return []
    class_uri_stripped = get_url_stripped(class_uri)
    query = """
        select ?p count(distinct ?s) as ?num where {
        ?s a <%s>.
        ?s ?p ?o
        FILTER(isNumeric(?o))
        }
        group by ?p
        order by desc(?num)
    """ % class_uri_stripped
    results = run_query(query=query, endpoint=endpoint, raiseexception=raiseexception)
    properties = [r['p']['value'] for r in results]
    return properties


def get_properties_for_class_abox(endpoint=None, class_uri=None, raiseexception=False):
    """
    a naive approach to get all numerical properties for a given class using the data itself A-BOX
    :param endpoint: endpoint
    :param class_uri: class uri for the class
    :return:
    """

    if class_uri is None:
        print("get_numerical_properties_for_class_abox> class_uri should not be None")
        return []
    class_uri_stripped = get_url_stripped(class_uri)
    query = """
        SELECT ?p (count(distinct ?s) as ?num)
        WHERE {
            ?s a <%s>.
            ?s ?p []
        }
        group by ?p
        order by desc(?num)
    """ % class_uri_stripped
    results = run_query(query=query, endpoint=endpoint, raiseexception=raiseexception)
    properties = [r['p']['value'] for r in results]
    return properties


################################################################
#                   Property Extraction T-BOX                   #
################################################################


def get_numerical_properties_for_class_tbox(endpoint=None, class_uri=None):
    """
    get all numerical properties for a given class using the domain and range (T-BOX)
    :param endpoint: endpoint
    :param class_uri: class uri for the class
    :return: properties
    """
    if class_uri is None:
        print("get_numerical_properties_for_class_tbox> class_uri should not be None")
        return []
    class_uri_stripped = get_url_stripped(class_uri)
    query = """
    select distinct ?pt where{
    ?pt rdfs:domain <%s>.
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#float>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#double>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#decimal>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#integer>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#nonPositiveInteger>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#negativeInteger>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#long>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#int>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#short>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#byte>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#nonNegativeInteger>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#unsignedLong>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#unsignedInt>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#unsignedShort>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#unsignedByte>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#positiveInteger>}
    }
    """ % class_uri_stripped
    results = run_query(query=query, endpoint=endpoint)
    properties = [r['pt']['value'] for r in results]
    return properties


def get_all_classes_properties_numerical(endpoint=None):
    """
    search for all class/property combinations with numerical objects. here we are relying on the defined
    structure using rdfs:range and rdfs:domain (TBOX) and not on the data level
    :param endpoint:
    :return: a list of class/property combinations. in case of no results or error, it will return []
    """
    if endpoint is None:
        print("get_all_classes_properties_numerical> endpoint should not be None")
        return []
    query = """
    select distinct ?pt ?c where{
    ?pt rdfs:domain ?c.
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#float>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#double>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#decimal>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#integer>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#nonPositiveInteger>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#negativeInteger>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#long>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#int>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#short>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#byte>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#nonNegativeInteger>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#unsignedLong>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#unsignedInt>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#unsignedShort>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#unsignedByte>} UNION
    {?pt rdfs:range <http://www.w3.org/2001/XMLSchema#positiveInteger>}
    }
    """
    results = run_query(query=query, endpoint=endpoint)
    class_property_uris = [(r['c']['value'], r['pt']['value']) for r in results]
    print("get_all_classes_properties_numerical> class_property_uris:")
    print(class_property_uris)
    return class_property_uris


#####################################################################
#                    Online Text Annotation                         #
#####################################################################


def clean_text(text):
    ctext = text.replace('"', '')
    ctext = ctext.replace("'", "")
    ctext = ctext.strip()
    return ctext


def get_entities_and_classes(subject_name, attributes, endpoint):
    """
    :param subject_name:
    :param attributes:
    :param endpoint: the SPARQL endpoint
    :return:
    """
    inner_qs = []
    csubject = clean_text(subject_name)
    for attr in attributes:
        cattr = clean_text(attr)
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
    results = run_query(query=query, endpoint=endpoint)
    try:
        entity_class_pair = [(r['s']['value'], r['c']['value']) for r in results]
    except:
        entity_class_pair = []
    return entity_class_pair


def get_entities_and_classes_naive(subject_name, endpoint):
    """
    assuming only in the form of name@en. To be extended to other languages and other types e.g. name^^someurltype
    :param subject_name:
    :return:
    """
    csubject = clean_text(subject_name)
    query = """
        select distinct ?s ?c where{
            ?s ?p "%s"@en.
            ?s a ?c
        }
    """ % csubject
    results = run_query(query=query, endpoint=endpoint)
    # entity_class_pair = [(r['s']['value'], r['c']['value']) for r in results]
    try:
        entity_class_pair = [(r['s']['value'], r['c']['value']) for r in results]
    except:
        entity_class_pair = []

    return entity_class_pair


def get_entities(subject_name, endpoint):
    """
    assuming only in the form of name@en. To be extended to other languages and other types e.g. name^^someurltype
    :param subject_name:
    :return:
    """
    query = """
        select distinct ?s where{
            ?s ?p "%s"@en
        }
    """ % (subject_name)
    results = run_query(query=query, endpoint=endpoint)
    entities = [r['s']['value'] for r in results]
    return entities


def get_classes(entity, endpoint, hierarchy):
    """
    :param entity:
    :param endpoint:
    :param hierarchy:
    :return:
    """
    if hierarchy:
        query = """
            select distinct ?c where{
            <%s> a ?cc.
            ?cc rdfs:subClassOf* ?c.
            }
        """ % entity
    else:
        query = """
            select distinct ?c where{
            <%s> a ?c
            }
        """ % entity
    results = run_query(query=query, endpoint=endpoint)
    classes = [r['c']['value'] for r in results]
    return classes


def get_classes_not_in(classes, endpoint):
    """
    This is to get more specific classes (e.g. given "thing", "soccer player", "person" it returns "soccer player")
    :param classes:
    :param endpoint:
    :return:
    """
    my_classes = ",".join(["<" + c + ">" for c in classes])
    query = """
        select ?ech where{
        ?ech a [].
        FILTER(?ech IN (%s)).
            MINUS{
                ?ec a [].
                FILTER (?ec NOT IN (%s)).
                ?ec rdfs:subClassOf+ ?ech.
            }
        }
    """ % (my_classes, my_classes)
    results = run_query(query=query, endpoint=endpoint)
    classes = [r['ech']['value'] for r in results]
    return classes


def get_classes_with_parents(classes, endpoint):
    """
    This to filter out classes that does not have parents
    :param classes:
    :param endpoint:
    :return:
    """
    my_classes = ",".join(["<" + c + ">" for c in classes])
    query = """
    select ?c where{
    ?c rdfs:subClassOf ?parent
    FILTER(?c IN (%s)).
    }
    """ % (my_classes)
    results = run_query(query=query, endpoint=endpoint)
    classes = [r['c']['value'] for r in results]
    return classes


def get_parents_of_class(class_name, endpoint):
    """
    get the parent class of the given class, get the first results in case of multiple ones
    :param class_name:
    :param endpoint:
    :return:
    """
    query = """
    select distinct ?c where{
    <%s> rdfs:subClassOf ?c.
    }
    """ % class_name
    results = run_query(query=query, endpoint=endpoint)
    classes = [r['c']['value'] for r in results]
    return classes


def get_children_of_class(class_name, endpoint):
    """
    get the children of a given class if any
    :param class_name:
    :param endpoint:
    :return:
    """
    query = """
    select distinct ?c where{
    ?c rdfs:subClassOf <%s>.
    }
    """ % class_name
    results = run_query(query=query, endpoint=endpoint)
    classes = [r['c']['value'] for r in results]
    return classes


# iteration 8
def get_classes_subjects_count(classes, endpoint):
    print("in get_classes_subjects_count")
    d = {}
    for c in classes:
        num = get_num_class_subjects(c, endpoint)
        d[c] = int(num)
    return d


def get_num_class_subjects(class_uri, endpoint):
    #print("count subject for class %s" % class_uri)
    query = """
    select count(?s) as ?num
    where {
    ?s a ?c.
    ?c rdfs:subClassOf* <%s>.
    }
    """ % class_uri
    results = run_query(query=query, endpoint=endpoint)
    return results[0]['num']['value']


#####################################################################
#                         Helper Functions                          #
#####################################################################


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
