import re

from aqt import mw

from .config import cfg
from .util import strip_html_tags


def note_text(note, length_limit=80):
    try:
        model_name = note.model()['name']
        if model_name == 'Cloze' or model_name.startswith('Cloze-'):
            result = note['Text']
        elif 'Front' in note.keys():
            result = note['Front']
        else:
            return None
    except KeyError:
        return None

    result = result.replace('\n', ' ')
    result = result.replace('<div>', '<div> ')
    result = result.replace('</div>', '</div> ')
    result = result.replace('<br>', ' ')
    result = result.replace('<br />', ' ')
    result = result.replace('<br/>', ' ')
    result = strip_html_tags(result)
    result = re.sub('{{c\d+:.+?}}', '(...)', result)
    result = result.strip()
    if len(result) > length_limit:
        result = result[:length_limit] + '[...]'
    if not result:  # NOTE if there is only an image on the front, the card will not appear on the map
        return None

    return result


def get_notes(search_string):
    return [ 
        mw.col.getNote(id) 
        for id in mw.col.find_notes(search_string)
    ]


def all_tags():
    return _all_partial_paths(mw.col.tags.all(), cfg('tag_seperator'))


def all_tags_that_have_subtags():
    return _all_partial_paths(mw.col.tags.all(), cfg('tag_seperator'), omit_leafs=True)


def _all_partial_paths(paths, seperator, omit_leafs=False):
    return set((
        seperator.join(string.split(seperator)[:i])
        for string in paths
        for i in range(1, len(string.split(seperator)) + (1 if not omit_leafs else 0))
    ))
