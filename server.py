import json
import logging
import ssl
import requests
import sys
import websocket
import time
from requests import HTTPError
from settings import configs as settings
from base64 import b64encode

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def listen_ws(sources):
    tokens = ','.join([source["LUNA_TOKEN"] for source in sources['SOURCES']])
    # auth = {'Authorization': 'Basic ZGVtb0BkZW1vLmRlbW86REVNT19URVNU'}
    base64auth = str(b64encode(bytes('{}:{}'.format(sources['LUNA_LOGIN'],
                                                    sources['LUNA_PASSWORD']), 'utf-8')).decode('utf-8'))
    print(base64auth)
    auth = {'Authorization': 'Basic ' + base64auth}
    print("{}?observe={}&event_type=match".format(sources["SUBSCRIPTION_URL"], tokens))
    ws = websocket.WebSocketApp(
        "{}?observe={}&event_type=match".format(sources["SUBSCRIPTION_URL"], tokens),
        on_message=process_message,
        on_error=process_error,
        on_close=process_close,
        header=auth)
    ws.run_forever(ping_interval=10, sslopt={"cert_reqs": ssl.CERT_NONE})


def process_message(ws, message):
    """
    :param ws: websocket instance. Can be used to send response or close, but not required currently
    :param message: message content. String
    :return: remote service response content or None
    """

    # We are waiting for valid json from LUNA
    try:
        data = json.loads(message)
    except (TypeError, ValueError) as ex:
        # So if it's not  - exit
        logger.error('Fail to parse JSON body')
        logger.exception(ex)
        return

    # Also we need to check if response contain candidates results
    if not "result" in data or not "candidates" in data["result"]:
        # So if it's not  - exit
        logger.error('Response have no candidates')
        logger.info(data)
        # So if it's not  - exit
        return

    # Get first candidate with highest score
    face = data["result"]["candidates"][0]
    token = data["authorization"]
    # print(token)

    source_settings = custom_settings[token["token_id"]]

    # If similarity threshold was set - check if we need to skip this match
    if source_settings['LUNA_SCORE_THRESHOLD'] and source_settings['LUNA_SCORE_THRESHOLD'] > face.get('similarity', 0):
        logger.info("Similarity {} does not pass threshold {}".format(face.get('similarity', 0), source_settings['LUNA_SCORE_THRESHOLD']))
        return

    # Prepare external service message
    args = {
        "cs{}".format(source_settings['DOOR_NUMBER']): source_settings['SIGNAL_TYPE']#,
        # "password": settings.EXT_SERVER_PASSWORD,
        # "terminal": settings.EXT_SERVER_TERMINAL, # Where should we get this?
        # "organisationId": settings.EXT_SERVER_ORGANIZATION,
        #"who": face.get('user_data') # Where should we get this?
    }
    print(args)
    # And now send it
    try:
        #response = requests.post(source_settings['EXT_SERVER_URL'], params=args)
        response = requests.get(source_settings['EXT_SERVER_URL'], params=args)
        time.sleep(int(source_settings['OPEN_DELAY']))
        args = {"cs{}".format(source_settings['DOOR_NUMBER']): int(not source_settings['SIGNAL_TYPE'])}
        print(args)
        response = requests.get(source_settings['EXT_SERVER_URL'], params=args)
    except HTTPError as ex:
        print("Error sending request")
        logger.error("Error sending request")
        logger.exception(ex)
        return
    except Exception as ex:
        print("Unexpected exception")
        logger.error("Unexpected exception")
        logger.exception(ex)
        return

    if source_settings['EXT_SERVER_DEBUG']:
        logger.info('='*80)
        logger.info('Sent request')
        logger.info(response.request.body)
        logger.info('-'*80)
        logger.info('Reveived response')
        logger.info('-'*80)
        logger.info(response.content)
        logger.info('='*80)

    if not response.ok:
        logger.error("Error {} while sending request to external server. "
                     "Enable debug logging to see full response".format(response.status_code))
        logger.debug(response.content)
    return response.content


def process_error(ws, error):
    # Log all errors
    logger.error(error)


def process_close(ws):
    # log connection closed
    logger.info("Connection {} closed".format(ws))


if __name__ == "__main__":
    # When started as script - connect to server and serve until connection will be dropped
    sources = settings
    custom_settings = {}
    for source in sources['SOURCES']:
        custom_settings[source['LUNA_TOKEN']] = source
    listen_ws(sources)



