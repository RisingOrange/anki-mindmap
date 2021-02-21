from aqt import mw

config = mw.addonManager.getConfig(__name__)

def cfg(key):
    try:
        return config[key]
    except KeyError:
        return None