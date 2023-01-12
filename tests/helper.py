from main import app
from main.models.account import AccountModel

test_app = app.test_client()


def create_account(
    session,
    **kwargs,
):
    data = {}

    if kwargs:
        data.update(kwargs)

    account = AccountModel(**data)

    session.add(account)
    session.commit()

    return account


def post_data(
    token, url, data, origin=None, http_referer=None, content_type='application/json'
):
    headers = {}
    if token is not None:
        headers['Authorization'] = 'Bearer {}'.format(token)
    if origin:
        headers['origin'] = origin
    if http_referer:
        headers['referer'] = http_referer
    return test_app.post(url, headers=headers, data=data, content_type=content_type)


def put_data(token, url, data):
    headers = {}
    if token is not None:
        headers['Authorization'] = 'Bearer {}'.format(token)
    return test_app.put(
        url,
        headers=headers,
        data=data,
        content_type='application/json',
    )


def delete_data(token, url, data=None):
    headers = {}
    if token is not None:
        headers['Authorization'] = 'Bearer {}'.format(token)
    return test_app.delete(
        url,
        headers=headers,
        data=data,
        content_type='application/json',
    )


def get_data(token, url, ip=None, **kwargs):
    get_url = url
    first = True
    for key, value in list(kwargs.items()):
        if key != 'headers':
            try:
                if isinstance(value, list):
                    value = ','.join(map(str, value))
                else:
                    value = str(value)
            except UnicodeEncodeError:
                value = str(value)
            if first:
                get_url += '?' + key + '=' + value
            else:
                get_url += '&' + key + '=' + value
            first = False
    headers = {}
    if token is not None:
        headers['Authorization'] = 'Bearer {}'.format(token)
    if ip:
        headers['X-Forwarded-For'] = ip
    if 'headers' in kwargs:
        headers.update(kwargs['headers'])
    return test_app.get(get_url, headers=headers)
