import tempfile

from ._vendor.brain_dump.graphviz import create_solarized_mindmap_img
from .anki_util import get_notes, note_and_tag_tree
from .util import redirect_stderr_to_stdout


NOTE_TEXT_LENGTH_LIMIT = 80


def tree_to_md(tree, level=0):
    indent = '    '
    return ''.join([
        f'{indent * level}{key.strip()}\n' +
        tree_to_md(value, level+1)
        for key, value in tree.items()
    ])


def create_mindmap(tag_prefix, output_file_path, only_tags=True):
    notes = get_notes(f'"tag:{tag_prefix}*"')
    tree = note_and_tag_tree(notes, tag_prefix=tag_prefix,
                             only_tags=only_tags, text_length_limit=NOTE_TEXT_LENGTH_LIMIT)
    tree_md = tree_to_md(tree)

    tmp_md_file = tempfile.NamedTemporaryFile()
    with open(tmp_md_file.name, 'w') as f:
        f.write(tree_md)

    with redirect_stderr_to_stdout():
        create_solarized_mindmap_img(
            tmp_md_file.name, output_file_path)

    tmp_md_file.close()
