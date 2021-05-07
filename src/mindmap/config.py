from aqt import mw


def cfg(key):
    config = mw.addonManager.getConfig(__name__)
    try:
        return config[key]
    except KeyError:
        return None