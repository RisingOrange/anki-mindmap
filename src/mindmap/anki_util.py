import re

from aqt import mw

from .config import cfg
from .util import strip_html_tags


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
    if not result:  # NOTE if there is only an image on the front, the card will not appear on the map
        return None

    return result


def get_notes(search_string):
    note_ids = mw.col.find_notes(search_string)
    result = [mw.col.getNote(id_) for id_ in note_ids]
    return result


def tags_that_have_subtags():
    tags = _filter_out_leaves(mw.col.tags.all(), cfg('tag_seperator'))
    return _prefixes(tags, cfg('tag_seperator'))


def decks_that_have_subdecks():
    DECK_SEPERATOR = '::'
    deck_names = _filter_out_leaves(mw.col.decks.allNames(), DECK_SEPERATOR)
    return _prefixes(deck_names, DECK_SEPERATOR)


def _filter_out_leaves(strings, seperator):
    return [
        string
        for string in strings
        if seperator in string
    ]


def _prefixes(strings, seperator):
    return set((
        seperator.join(
            tag.split(seperator)[:i])
        for tag in strings
        for i in range(1, len(tag.split(seperator)))
    ))
