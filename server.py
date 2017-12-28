import json
import logging

import requests
import websocket
import settings

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

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

    # If similarity threshold was set - check if we need to skip this match
    if settings.LUNA_SCORE_THRESHOLD and settings.LUNA_SCORE_THRESHOLD < face.get('similarity', 0):
        return

    # Prepare external service message
    args = {
        "login": settings.EXT_SERVER_LOGIN,
        "password": settings.EXT_SERVER_PASSWORD,
        "terminal": settings.EXT_SERVER_TERMINAL, # Where should we get this?
        "organisationId": settings.EXT_SERVER_ORGANIZATION,
        "value": face.get('user_data') # Where should we get this?
    }
    # And now send it
    response = requests.post(settings.EXT_SERVER_URL, json=args)

    if settings.EXT_SERVER_DEBUG:
        logger.info('='*80)
        logger.info('Sent request')
        logger.info(response.request.body)
        logger.info('-'*80)
        logger.info('Reveived response')
        logger.info('-'*80)
        logger.info(response.content)
        logger.info('='*80)

    if not response.ok:
        logger.error("Error {} while sending request to external server. Enable debug logging to see full response".format(response.status_code))
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

    ws = websocket.WebSocketApp("{}?auth_token={}&event_type=match".format(settings.SUBSCRIPTION_URL, settings.LUNA_TOKEN),
                                on_message=process_message,
                                on_error=process_error,
                                on_close=process_close)

    # Serving with ping to prevent connection close
    ws.run_forever(ping_interval=10)
