import json
try:
    with open("./config.json", "r") as config_file:
        config = json.load(config_file)
except (TypeError, ValueError, IOError):
    config = {}

configs = {}
sources = []

for source in config["sources"]:
    try:
        EXT_SERVER_DEBUG = bool(config.get("debug", True))
    except (TypeError, ValueError):
        EXT_SERVER_DEBUG = True

    NAME = source.get("name")
    DOOR_NUMBER = source.get("number")
    EXT_SERVER_URL = source.get("url")
    OPEN_DELAY = source.get("open_delay")
    SIGNAL_TYPE = source.get("signal_type")
    # SUBSCRIPTION_URL = source.get("websocket", "ws://stat.faceis.ru/api/subscribe")

    LUNA_TOKEN = source.get("token")
    # SUBSCRIPTION_TOKENS = [LUNA_TOKEN,]
    LUNA_SCORE_THRESHOLD = source.get("threshold", 0.7)
    source_conf = {'SOURCE_NAME': NAME, 'DOOR_NUMBER': DOOR_NUMBER, 'EXT_SERVER_URL': EXT_SERVER_URL,
                   'LUNA_SCORE_THRESHOLD': LUNA_SCORE_THRESHOLD,
                   'LUNA_TOKEN': LUNA_TOKEN, 'EXT_SERVER_DEBUG': EXT_SERVER_DEBUG, 'OPEN_DELAY': OPEN_DELAY, 
                   'SIGNAL_TYPE': SIGNAL_TYPE}
    # print(source_conf)
    sources.append(source_conf)

configs['SUBSCRIPTION_URL'] = config['websocket']
configs['SOURCES'] = sources
configs['LUNA_LOGIN'] = config['luna_login']
configs['LUNA_PASSWORD'] = config['luna_password']
