import random
import string
import os

# ENDPOINT = "http://dbpedia.org/sparql"
ENDPOINT = os.environ['endpoint']


def random_string(length=4):
    return ''.join(random.choice(string.lowercase) for i in range(length))
