from collections import defaultdict


def tree(dictionary=None):
    return defaultdict(tree) if dictionary is None else defaultdict(tree, dictionary)


def without_leaves(a_tree):
    return tree({
        key: without_leaves(subtree)
        for key, subtree in a_tree.items()
        if len(subtree) > 0
    })


def tree_to_markdown(tree, level=0):
    indent = '    '
    return ''.join([
        f'{indent * level}{key.strip()}\n' +
        tree_to_markdown(subtree, level+1)
        for key, subtree in tree.items()
    ])
