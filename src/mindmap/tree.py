from collections import defaultdict


def tree(dictionary=None):
    return defaultdict(tree) if dictionary is None else defaultdict(tree, dictionary)
