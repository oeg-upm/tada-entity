import random
import string


ENDPOINT = "http://dbpedia.org/sparql"

def random_string(length=4):
    return ''.join(random.choice(string.lowercase) for i in range(length))
