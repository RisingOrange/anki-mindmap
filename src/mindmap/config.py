from aqt import mw

config = mw.addonManager.getConfig(__name__)

def get_config_value(key):
    try:
        return config[key]
    except KeyError:
        return None