# coding: utf-8

import requests
from requests.exceptions import ConnectTimeout, ReadTimeout, ConnectionError
from flask import abort, request

from citadel.config import DEBUG, AUTH_AUTHORIZE_URL, AUTH_GET_USER_URL
from citadel.ext import sso
from citadel.libs.cache import cache, ONE_DAY


_DEBUG_USER_DICT = {
    'id': 10056,
    'name': 'liuyifu',
    'real_name': 'timfeirg',
    'email': 'test@test.com',
    'privilege': 1,
    'token': 'token',
    'pubkey': '',
}


@cache(ttl=ONE_DAY)
def get_current_user_via_auth(token):
    try:
        resp = requests.get(AUTH_AUTHORIZE_URL, headers={'X-Neptulon-Token': token}, timeout=5)
    except (ConnectTimeout, ConnectionError, ReadTimeout):
        abort(408, 'error when getting user from neptulon')

    status_code = resp.status_code
    if status_code != 200:
        abort(status_code)

    return User.from_dict(resp.json())


@cache(ttl=ONE_DAY)
def get_user_via_auth(token, identifier):
    try:
        resp = requests.get(AUTH_GET_USER_URL,
                            headers={'X-Neptulon-Token': token},
                            params={'identifier': identifier},
                            timeout=5)
    except (ConnectTimeout, ConnectionError, ReadTimeout):
        abort(408, 'error when getting user from neptulon')

    status_code = resp.status_code
    if status_code != 200:
        abort(status_code)

    return User.from_dict(resp.json())


def get_current_user():
    if DEBUG:
        return User.from_dict(_DEBUG_USER_DICT)

    token = request.headers.get('X-Neptulon-Token') or request.values.get('X-Neptulon-Token')
    if token:
        return get_current_user_via_auth(token)
    resp = sso.get('me')
    return User.from_dict(resp.data)


def get_user(identifier):
    if DEBUG:
        return User.from_dict(_DEBUG_USER_DICT)

    token = request.headers.get('X-Neptulon-Token') or request.values.get('X-Neptulon-Token')
    if token:
        return get_user_via_auth(token, identifier)
    resp = sso.get('user/%s' % identifier)
    return resp.data and User.from_dict(resp.data) or None


def get_users(start=0, limit=20, q=None):
    if DEBUG:
        return [User.from_dict(_DEBUG_USER_DICT)]

    data = {'start': start, 'limit': limit}
    if q:
        data.update({'q': q})

    resp = sso.get('users', data)
    return [User.from_dict(d) for d in resp.data if d]


class User(object):

    def __init__(self, id, name, email, realname, privilege, token='', pubkey=''):
        self.id = id
        self.name = name
        self.email = email
        self.realname = realname
        self.privilege = privilege
        self.token = token
        self.pubkey = pubkey

    @classmethod
    def from_dict(cls, info):
        if not info or not isinstance(info, dict):
            return None
        return cls(info['id'], info['name'], info['email'], info['real_name'],
                   info['privilege'], info.get('token', ''), info.get('pubkey', ''))

    @classmethod
    def get(cls, id):
        return get_user(id)
