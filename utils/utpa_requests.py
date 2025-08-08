'''
'''
from datetime import datetime

import flask
import requests
from flask import request

from config import logger
from db.crud_utils.login_central_utils.login_central_read_queries import get_by_user_id


# from psql import log
# from data.user.user_model import User


def forward_request(forward_url, exchange_id):
    '''
    Forwards the request to the given url as an owner
    from a subscriber account by exchanging the auth token
    using the exchange id, i.e, owner's id.

    Parameters
    ----------
    forward_url: str
        The url to which the request must be forwarded.

    exchange_id: int
        The id whose auth token is to be found, i.e, owner.

    Returns
    -------
    response: dict
        It is the response from the forwarded url.
    '''
    logger.info(
        'The request is being forwarded, and user auth is being exchanged.'
    )
    exchange_id = int(exchange_id)
    exchanged_user = get_by_user_id(exchange_id)

    # headers = {key: value for key, value in request.headers.items()}
    headers = {}
    # Remove 'X-Owner-Id' from headers if it exists
    # headers.pop('X-Owner-Id', None)

    # Add the new Authorization header
    headers['Authorization'] = ' '.join([
        'Bearer',
        exchanged_user.authtoken
    ])

    logger.info(f'Request forwarded to user-{exchanged_user.id}'
             f'\n for method-{request.method}')

    files = request.files.items()
    dictionary_of_files = {k: (v.filename, v.stream, v.content_type)
                           for k, v in files if v.filename}
    request_json = None
    if request.content_type == 'application/json':
        request_json = request.json
    request_args = request.args.to_dict()

    if request.method in ('POST', 'PATCH', 'PUT', 'DELETE'):
        logger.info(f"Request forward_url: {forward_url} , headers: {headers} , request_json: {request_json} , request.form: {request.form} , dictionary_of_files: {dictionary_of_files} , request_args: {request_args}")
        f = getattr(requests, request.method.lower())

        response = f(url=forward_url,
                     headers=headers,
                     verify=False,
                     json=request_json,
                     data=request.form,
                     files=dictionary_of_files,
                     params=request_args, timeout=300)
        logger.info(f"Response from forward_url: {response}")
    elif request.method == 'GET':
        response: requests.Response = requests.get(url=forward_url,
                                                   headers=headers,
                                                   json=request_json,
                                                   verify=False,
                                                   params=request_args, timeout=300)

    else:
        raise ValueError("Unsupported HTTP method.")

    if 'text/html' in response.headers.get('Content-Type', (None,)):
        return response.content.decode()
    elif response.headers.get("Content-Type"):
        file = response.content
        content_type = response.headers.get("Content-Type")
        content_disposition = response.headers.get("Content-Disposition", None)
        response = flask.Response(
            file,
            mimetype=content_type,
            headers={
                "Content-Disposition": content_disposition,
                "Content-Type": content_type,
                "Server": "hidden"
            }
        )
        return response
    return response.json()


def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO format string
    raise TypeError(f"Type {type(obj)} not serializable")

