from abc import ABC

from aqt import mw

from ._vendor.brain_dump.graphviz import create_mindmap_img
from .anki_util import get_notes, note_text
from .config import cfg
from .tree import tree, tree_to_markdown, without_leaves
from .util import redirect_stderr_to_stdout

NOTE_TEXT_LENGTH_LIMIT = 80


class Mindmap(ABC):

    def save_as_img(self, output_file_path, theme, include_notes):
        # XXX without_leaves also removes nodes that have no displayable notes
        tree = self.tree if include_notes else without_leaves(self.tree)
        with redirect_stderr_to_stdout():
            create_mindmap_img(tree_to_markdown(tree), output_file_path, theme)

    def _paths(self):
        return [
            path
            for path in self.all_paths
            if self._starts_with_root_path(path)
        ]

    def _create_tree(self):
        result = tree()
        for path in self._paths():
            # traversing the tree adds nodes along the way
            subtree = self._traverse_tree(result, path)

            for note in get_notes(f'"{self.query_term}:{path}"'):
                text = note_text(note, NOTE_TEXT_LENGTH_LIMIT)

                if text is not None:
                    subtree[text] = tree()

        return result

    def _traverse(self, path):
        return self._traverse_tree(self, path)

    def _traverse_tree(self, tree, path):
        path_wh_root = self._without_root_path(path)
        parts = path_wh_root.split(self.seperator)
        cur = tree
        for p in parts:
            cur = cur[p]
        return cur

    def _starts_with_root_path(self, path):
        prefix_parts = self.root_path.split(self.seperator)
        path_parts = path.split(self.seperator)
        for a, b in zip(prefix_parts, path_parts):
            if a != b:
                return False
        return True

    def _without_root_path(self, path):
        root_depth = len(self.root_path.split(self.seperator))
        return self.seperator.join(path.split(self.seperator)[root_depth-1:])


class TagMindmap(Mindmap):

    def __init__(self, tag_prefix):
        self.root_path = tag_prefix
        self.all_paths = mw.col.tags.all()
        self.seperator = cfg('tag_seperator')
        self.query_term = 'tag'
        self.tree = self._create_tree()


class DeckMindmap(Mindmap):

    def __init__(self, deck_prefix):
        self.root_path = deck_prefix
        self.all_paths = mw.col.decks.allNames()
        self.seperator = '::'
        self.query_term = 'deck'
        self.tree = self._create_tree()
