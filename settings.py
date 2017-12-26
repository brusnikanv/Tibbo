import json
try:
    with open("./config.json", "r") as config_file:
        config = json.load(config_file)
except (TypeError, ValueError, IOError):
    config = {}

EXT_SERVER_LOGIN = config.get("login", "admin")
EXT_SERVER_PASSWORD = config.get("password", "password")
EXT_SERVER_ORGANIZATION = config.get("organization", "1")
EXT_SERVER_URL = config.get("url", "http://127.0.0.1:8081")
SUBSCRIPTION_URL = config.get("websocket", "ws://stat.faceis.ru/api/subscribe")

LUNA_TOKEN = config.get("token", "96b9a4bf-f449-4e69-aae4-54195c7fe1da")
SUBSCRIPTION_TOKENS = [LUNA_TOKEN,]

LUNA_SCORE_THRESHOLD = config.get("threshold", 0)
