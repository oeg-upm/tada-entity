import random
import string


def random_string(length=4):
    return ''.join(random.choice(string.lowercase) for i in range(length))
