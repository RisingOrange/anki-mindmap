import re
import sys
from collections import defaultdict
from contextlib import contextmanager
from html.parser import HTMLParser
from io import StringIO

from aqt import mw

from .config import cfg


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_html_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def note_and_tag_tree(notes, tag_prefix=None, only_tags=False, root_name=None, text_length_limit=80):
    def tree(): return defaultdict(tree)

    result = tree()

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

            if not only_tags:
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


def note_text(note, length_limit=80):
    if note.model()['name'].startswith('Basic'):
        result = note['Front']
    elif note.model()['name'].startswith('Cloze'):
        result = note['Text']
    else:
        return None
    result = result.replace('\n', ' ')
    result = result.replace('<div>', '<div> ')
    result = result.replace('</div>', '</div> ')
    result = result.replace('<br>', ' ')
    result = strip_html_tags(result)
    result = re.sub('{{c\d+:.+?}}', '(...)', result)
    result = result.strip()
    if len(result) > length_limit:
        result = result[:length_limit] + '[...]'
    if not result:  # NOTE if there is only on image on the front, the card will not appear on the map
        return None

    return result


def get_notes(search_string):
    note_ids = mw.col.find_notes(search_string)
    result = [mw.col.getNote(id_) for id_ in note_ids]
    return result


def tag_prefixes():
    tags = [tag for tag in mw.col.tags.all(
    ) if get_config_value('get_config_value('tag_seperator')') in tag]
    tag_prefixes = set((
        get_config_value('get_config_value('tag_seperator')').join(
            tag.split(get_config_value('get_config_value('tag_seperator')'))[:i])
        for tag in tags
        for i in range(1, len(tag.split(get_config_value('get_config_value('tag_seperator')'))))
    ))
    return tag_prefixes


class DevNull:
    def write(self, msg):
        pass


@contextmanager
def redirect_stderr_to_stdout():
    stderr = sys.stderr
    sys.stderr = sys.stdout
    try:
        yield None
    finally:
        sys.stderr = stderr
