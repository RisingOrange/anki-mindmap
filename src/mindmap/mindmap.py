from abc import ABC


from ._vendor.brain_dump.graphviz import create_mindmap_img
from .anki_util import all_tags, get_notes, note_text
from .config import cfg
from .tree import tree
from .util import redirect_stderr_to_stdout

NOTE_TEXT_LENGTH_LIMIT = 80


class Mindmap(ABC):

    def save_as_img(self, output_file_path, theme, include_notes):
        with redirect_stderr_to_stdout():
            create_mindmap_img(
                self._to_markdown(include_notes),
                output_file_path,
                theme
            )

    def _initialize_tree(self):
        result = tree()
        for path in self._paths():
            self._traverse_tree(result, path)

        return result

    def _initialize_notes_by_path(self):
        return {
            path:
            get_notes(f'"{self.query_term}:{path}*"')
            for path in self._paths()
        }

    def _percentage_of_notes_by_path(self, path):
        notes_total_amount = len(self.notes_by_path[self.root_path])
        cur_path_amount = len(self.notes_by_path[self._with_root_path(path)])
        return cur_path_amount / notes_total_amount

    def _to_markdown(self, include_notes):
        return self._tree_to_markdown(self.tree, include_notes)

    def _tree_to_markdown(self, tree, include_notes, level=0, path=''):
        indent = '    ' * level

        def new_path(key):
            return path + self.seperator + key if path else key

        if include_notes and len(tree) == 0:
            return '\n'.join([
                f'{indent}{note_text(note).strip()} 0'
                for note in self.notes_by_path[self._with_root_path(path)]
                if note_text(note).strip()
            ])
        else:
            return '\n'.join([
                (f'{indent}{key.strip()} {self._percentage_of_notes_by_path(new_path(key))}\n' +
                self._tree_to_markdown(
                    subtree, include_notes, level+1, new_path(key))
                ).strip('\n')
                for key, subtree in tree.items()
                if key.strip()
            ])

    def _paths(self):
        return [
            path for path in self.all_paths
            if self._starts_with_root_path(path)
        ]

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
        root_parts = self.root_path.split(self.seperator)
        path_parts = path.split(self.seperator)

        if len(path_parts) < len(root_parts):
            return False

        return all([
            a == b
            for a, b in
            zip(root_parts, path_parts)
        ])

    def _without_root_path(self, path):
        root_depth = len(self.root_path.split(self.seperator))
        return self.seperator.join(path.split(self.seperator)[root_depth-1:])

    def _with_root_path(self, path):
        path_from_root = self.seperator.join(path.split(self.seperator)[1:])
        return self.root_path + (self.seperator + path_from_root if path_from_root else '')


class TagMindmap(Mindmap):

    def __init__(self, tag_prefix):
        self.root_path = tag_prefix
        self.seperator = cfg('tag_seperator')
        self.all_paths = all_tags()
        self.query_term = 'tag'
        self.tree = self._initialize_tree()
        self.notes_by_path = self._initialize_notes_by_path()
