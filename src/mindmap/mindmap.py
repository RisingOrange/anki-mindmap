from abc import ABC

from ._vendor.brain_dump.graphviz import create_mindmap_img
from .anki_util import get_notes, note_text
from .config import cfg
from .tree import tree, tree_to_markdown, without_leaves
from .util import redirect_stderr_to_stdout

NOTE_TEXT_LENGTH_LIMIT = 80


class Mindmap(ABC):

    def save_as_img(self, output_file_path, theme, include_notes):
        tree = self.tree if include_notes else without_leaves(self.tree)
        with redirect_stderr_to_stdout():
            create_mindmap_img(tree_to_markdown(tree), output_file_path, theme)


class TagMindmap(Mindmap):

    def __init__(self, tag_prefix):
        self.tree = self._tag_tree(
            tag_prefix, text_length_limit=NOTE_TEXT_LENGTH_LIMIT)

    def _tag_tree(self, tag_prefix, root_name=None, text_length_limit=80):
        result = tree()

        notes = get_notes(f'"tag:{tag_prefix}*"')
        for note in notes:
            for tag in note.tags:
                if not tag.startswith(tag_prefix):
                    continue

                prefix_tag_depth = len(tag_prefix.split(
                    cfg('tag_seperator')))
                tag_parts = tag.split(cfg('tag_seperator'))[
                    prefix_tag_depth-1:]
                cur = result
                for p in tag_parts:
                    cur = cur[p]

                text = note_text(note, text_length_limit)
                if text is None:
                    continue
                cur[text] = tree()

        # add root node
        if root_name is not None:
            root = tree()
            root[root_name] = result
            result = root

        return result
