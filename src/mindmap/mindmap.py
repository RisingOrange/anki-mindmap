import json
from collections import defaultdict
from pathlib import Path

from ._vendor.brain_dump.graphviz import create_mindmap_img
from .anki_util import all_tags, get_notes, note_text
from .config import cfg
from .progress_widget import get_progress_widget
from .tree import tree
from .util import redirect_stderr_to_stdout

NOTE_TEXT_LENGTH_LIMIT = 80


class TagMindmap:

    def __init__(self, tag_prefix):
        self.root_path = tag_prefix
        self.seperator = cfg('tag_seperator')
        self.all_paths = all_tags()
        self.query_term = 'tag'
        self.tree = self._initialize_tree()
        self.notes_by_path = self._initialize_notes_by_path()

    # saving to file
    def save_as_img(self, output_file_path, theme, include_notes, max_depth=None):
        markdown = self._to_markdown(include_notes, max_depth)

        widget, callback = get_progress_widget(len(markdown.split('\n')))

        with redirect_stderr_to_stdout():
            try:
                create_mindmap_img(
                    markdown,
                    output_file_path,
                    theme,
                    callback,
                    pydot_program=cfg('path_to_dot')
                )
            except Exception as e:
                if e.args and e.args[0] == 'user cancelled':
                    print('user cancelled drawing')
                else:
                    raise e
            finally:
                widget.close()

    def save_as_jsmind(self, output_file_path, include_notes):
        jsmind = self._to_mindjs(include_notes=include_notes)
        jsmind_json = json.dumps(jsmind)
        with open(Path(__file__).parent / 'jsmind/jsmind_template.html') as f:
            template = f.read()

        result = template.replace('$PLACEHOLDER$', jsmind_json)
        with open(output_file_path, 'w') as f:
            f.write(result)

    def _to_markdown(self, include_notes, max_depth):
        return self._tree_to_markdown(self.tree, include_notes, max_depth=max_depth)

    def _tree_to_markdown(self, tree, include_notes, level=0, path='', max_depth=None):

        def new_path(key):
            return path + self.seperator + key if path else key

        indent = '    ' * level

        if include_notes and (len(tree) == 0 or level > max_depth):
            return '\n'.join([
                f'{indent}{note_text(note).strip()} 0'
                for note in self.notes_by_path[self._with_root_path(path)]
                if note_text(note)
            ])

        if max_depth is not None and level > max_depth:
            return ""

        return '\n'.join([
            (f'{indent}{key.strip()} {self._percentage_of_notes_by_path(new_path(key))}\n' +
                self._tree_to_markdown(
                    subtree, include_notes, level+1, new_path(key), max_depth=max_depth)
             ).strip('\n')
            for key, subtree in tree.items()
            if key.strip()
        ])

    def _to_mindjs(self, topic=None, tree=None, depth=-1, include_notes=False, path=''):

        if topic is None:
            self._to_mindjs_id = 0

            data = self._to_mindjs(list(self.tree.keys())[
                                   0], list(self.tree.values())[0], 0, include_notes)
            return {
                "meta": {
                    "name": "jsMind remote",
                    "author": "hizzgdev@163.com",
                    "version": "0.2"
                },
                "format": "node_tree",
                "data": data
            }

        def new_path(key):
            return path + self.seperator + key if path else key

        def new_node(depth=depth):
            result = {
                "id": str(self._to_mindjs_id),
                "topic": topic,
                "expanded": depth == 0,
                "children": list(),
                "direction": "right"
            }
            self._to_mindjs_id += 1
            return result

        result = new_node()

        if len(tree) == 0 and include_notes:
            for note in self.notes_by_path[self._with_root_path(path)]:

                text = note_text(note)
                if not text:
                    continue

                note = new_node(depth=depth+1)
                note["topic"] = text
                result["children"].append(note)

        for topic, subtree in tree.items():
            result["children"].append(self._to_mindjs(
                topic, subtree, depth+1, include_notes, new_path(topic)))

        return result

    # building the tree and note data
    def _initialize_tree(self):
        result = tree()
        for path in self._paths():
            self._traverse_tree(result, path)

        return result

    def _initialize_notes_by_path(self):
        notes = get_notes(f'"{self.query_term}:{self.root_path}*"')
        result = defaultdict(list)

        result[self.root_path] = notes

        for note in notes:
            for path in note.tags:
                if not self._starts_with_root_path(path):
                    continue

                relative_path = path[len(self.root_path):]
                while relative_path:
                    result[self.root_path + relative_path].append(note)
                    relative_path = relative_path.rsplit(
                        self.seperator, maxsplit=1)[0]

        return result

    def _percentage_of_notes_by_path(self, path):
        cur_path_amount = len(self.notes_by_path[self._with_root_path(path)])
        notes_total_amount = len(self.notes_by_path[self.root_path])

        if notes_total_amount == 0:
            return 0
        return cur_path_amount / notes_total_amount

    # paths, traversal
    def _paths(self):
        return reversed(sorted([
            path for path in self.all_paths
            if self._starts_with_root_path(path)
        ], key=lambda x: x.lower()))

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
        return path == self.root_path or path.startswith(self.root_path + self.seperator)

    def _without_root_path(self, path):
        # if root_path is a::b and path is a::b::c the result is b::c
        root_depth = len(self.root_path.split(self.seperator))
        return self.seperator.join(path.split(self.seperator)[root_depth-1:])

    def _with_root_path(self, path):
        # if root path is a::b and path is b::c the result is a::b::c
        path_from_root = self.seperator.join(path.split(self.seperator)[1:])
        return self.root_path + (self.seperator + path_from_root if path_from_root else '')
