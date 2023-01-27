import random
from typing import Any, Optional

from flask import Request

from main import config, core, pusher_client
from main.enums import PusherEvent
from main.libs.log import ServiceLogger

logger = ServiceLogger(__name__)


def parse_channel(channel_name: str) -> Optional[dict]:
    """
    Parse channel name to get channel information
    :param channel_name: Channel name formation is presence-{type}-{namespace} with:
        - type: projects
        - namespace: should be the same as PUSHER_CHANNEL_NAMESPACE config. Be used to
        isolate events for an environment in case there're multiple environments which
        share the same pusher project.
    :return: channel information
    """
    channel = channel_name.split('-')

    if channel[2] != config.PUSHER_CHANNEL_NAMESPACE:
        # Validate the channel namespace
        return None
    return {'type': channel[1]}


def authenticate(request: Request, account) -> Any:
    """
    Authenticate a client to make sure it has rights to join a pusher channel
    :param request: a flask request object
    :param member: a dict contains member id
    :return: pusher payload or none in case can not authenticate the client
    """
    channel = parse_channel(request.form['channel_name'])

    if not channel:
        return None

    try:
        # TODO (Thinh): Integrate member account type
        pusher_payload = pusher_client.authenticate(
            channel=request.form['channel_name'],
            socket_id=request.form['socket_id'],
            custom_data={
                'user_id': account.id,
            },
        )
    except Exception as e:
        logger.exception(message=str(e))
        return None

    if pusher_payload is None:
        logger.error(message='There was an error while authenticating with Pusher')
    else:
        return pusher_payload


def validate_webhook(request: Request) -> Any:
    """
    Validate a pusher webhook request.
    :param request: a flask request object that contains pusher webhook data.
    See this link for more details: https://pusher.com/docs/webhooks
    :return: request data or none if the request is invalid
    """
    key = request.headers['X-Pusher-Key']
    signature = request.headers['X-Pusher-Signature']

    try:
        response = pusher_client.validate_webhook(key, signature, request.get_data())
    except Exception as e:
        logger.exception(message=str(e))
        return None
    return response


def _get_projects_channel_name():
    return '-'.join(['presence', 'projects', config.PUSHER_CHANNEL_NAMESPACE])


def trigger_pusher(channel_name: str, event_type: str, data: Any) -> None:
    """
    Trigger a pusher event
    :param channel_name:
    :param event_type:
    :param data:
    :return:
    """
    try:
        logger.debug(message='Triggering pusher', data=locals())
        pusher_client.trigger(channel_name, event_type, data)
    except Exception:
        logger.exception(message='Pusher exception')


def _defer_trigger(channel_name: str, event_type: str, data: Any) -> None:
    """
    Defer the pusher event trigger later
    :param channel_name:
    :param event_type:
    :param data:
    :return:
    """
    info = channel_name.split('-')
    try:
        int(info[2])
        id = channel_name
    except ValueError:
        id = random.randint(0, config.EVENT_BUS_PARTITIONS)
    core.queue_deferred(
        trigger_pusher, channel_name, event_type, data, _queue='pusher', _key=id
    )


def trigger_rasa_status_changed(data: dict):
    _defer_trigger(_get_projects_channel_name(), PusherEvent.RASA_STATUS_CHANGED, data)


def trigger_async_task_status_changed(data: dict):
    logger.debug(message='trigger_async_task_status_changed', data=data)
    _defer_trigger(
        _get_projects_channel_name(), PusherEvent.ASYNC_TASK_STATUS_CHANGED, data
    )
