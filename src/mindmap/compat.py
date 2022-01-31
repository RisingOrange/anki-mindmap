import anki
from aqt import mw


def add_compat_aliases_to_anki():
    add_compat_alias(anki.utils, "is_mac", "isMac")
    add_compat_alias(anki.utils, "is_win", "isWin")


def add_compat_aliases_to_aqt():
    add_compat_alias(mw.col, "get_note", "getNote")


def add_compat_alias(namespace, new_name, old_name):
    if new_name not in list(namespace.__dict__.keys()):
        setattr(namespace, new_name, getattr(namespace, old_name))
        return True

    return False
