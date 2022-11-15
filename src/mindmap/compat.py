import anki
from anki.notes import Note
from aqt import mw


def add_compat_aliases_to_anki():
    add_compat_alias(anki.utils, "is_mac", "isMac")
    add_compat_alias(anki.utils, "is_win", "isWin")
    add_compat_alias(Note, "note_type", "model")


def add_compat_aliases_to_aqt():
    add_compat_alias(mw.col, "get_note", "getNote")


def add_compat_alias(namespace, new_name, old_name):
    if new_name not in dir(namespace):
        setattr(namespace, new_name, getattr(namespace, old_name))
        return True

    return False
