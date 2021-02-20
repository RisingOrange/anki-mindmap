import subprocess

from aqt import mw

from .util import get_notes, note_and_tag_tree

ONLY_TAGS = True
GV_ENGINE = 'twopi'

MD_FILEPATH = 'tree.md'

NOTE_TEXT_LENGTH_LIMIT = 80


def tree_to_md(tree, level=0):
    indent = '    '
    return ''.join([
        f'{indent * level}{key.strip()}\n' +
        tree_to_md(value, level+1)
        for key, value in tree.items()
    ])


def main(deck_name):
    notes = get_notes(f'"deck:{deck_name}"', mw.col)
    tag_prefix = deck_name.split('::')[-1]
    tree = note_and_tag_tree(notes, tag_prefix=tag_prefix,
                             only_tags=ONLY_TAGS, text_length_limit=NOTE_TEXT_LENGTH_LIMIT)
    tree_md = tree_to_md(tree)

    with open(MD_FILEPATH, 'w+') as f:
        f.write(tree_md)

    # create png using graphviz_md2png
    subprocess.call(['graphviz_md2png', MD_FILEPATH, '--layout', GV_ENGINE])
