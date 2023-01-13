# TODO: to be open sourced
import json

import requests

from main.config import config

HEADERS = {'Content-Type': 'application/json'}


def send_task(task):
    if task.get('delay') is None or task.get('delay') == 0:
        return requests.post(
            config.EVENT_BUS_URL, headers=HEADERS, data=json.dumps(task)
        )
    return requests.post(
        config.EVENT_BUS_DELAYED_URL, headers=HEADERS, data=json.dumps(task)
    )
