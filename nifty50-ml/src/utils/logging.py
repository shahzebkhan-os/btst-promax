import json
import logging

logger = logging.getLogger("nifty50")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def log_json(**kwargs):
    logger.info(json.dumps(kwargs))
