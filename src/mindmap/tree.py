from collections import defaultdict


def tree(dictionary=None):
    return defaultdict(tree) if dictionary is None else defaultdict(tree, dictionary)


def tree_to_markdown(tree, level=0):
    indent = '    '
    return ''.join([
        f'{indent * level}{key.strip()}\n' +
        tree_to_markdown(subtree, level+1)
        for key, subtree in tree.items()
    ])
