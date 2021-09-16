import os
from functools import wraps
from urllib.parse import urlparse

from dcustructuredloggingflask.flasklogger import get_logging
from flask import Response, redirect, request
from gd_auth.exceptions import TokenExpiredException
from gd_auth.token import AuthToken, TokenBusinessLevel

from settings import config_by_name

# Creates logger settings
logger = get_logging()
config = config_by_name[os.getenv('sysenv', 'dev')]()


def do_login(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if config.WITHOUT_SSO:
            return f(*args, **kwargs)

        logger.debug('decorator args: {}'.format(args))
        logger.debug('decorator kwargs: {}'.format(kwargs))

        app_url = 'https://{}/login/?realm=jomax&app={}'.format(config.SSO_URL[8:], config.CMAPSERVICE_APP)
        auth_groups = config.AD_GROUP
        cn_whitelist = config.CN_WHITELIST
        token_authority = config.SSO_URL[8:]

        if not token_authority:  # bypass if no token authority is set
            return f(*args, **kwargs)

        token = request.headers.get('Authorization', '').strip()
        if token:
            logger.debug('Token: {}'.format(token))
            token = token.strip()
            if token.startswith('sso-jwt'):
                token = token[8:].strip()
            return validate_auth(token, token_authority, auth_groups, cn_whitelist)
        else:
            token = request.cookies.get('auth_jomax')
            logger.debug('Token: {}'.format(token))
            if validate_auth(token, token_authority, auth_groups, cn_whitelist):
                o = urlparse(request.full_path)
                return redirect('{}&path=/graphql?{}'.format(app_url, o.query))

        return f(*args, **kwargs)
    return wrapped


def validate_auth(token, token_authority, auth_groups, cn_whitelist):
    """
    Validates if the provided token belongs to the DCU AD group or CN is whitelisted with DCU depending on the type
    :param token : The auth token extracted from cookies or Auth header
    :param token_authority: Token Authority to be validated against. SSO in this case
    :param auth_groups: Whitelisted AD groups
    :param cn_whitelist: Whitelisted CNs
    :return: Response object or None
    """
    if not token:
        return Response('No JWT provided. Unauthorized. Please verify your token \n ', status=401)

    forbidden = Response('Forbidden. Please verify your token \n ', status=403)

    try:
        payload = AuthToken.payload(token)
        typ = payload.get('typ')
        parsed = AuthToken.parse(token, token_authority, 'CMAP Service', typ=typ)

        try:
            parsed.is_expired(TokenBusinessLevel.LOW)
        except TokenExpiredException:
            return Response('Expired JWT provided. Unauthorized. Please verify your token \n ', status=401)

        if typ == 'jomax':
            user_groups = set(parsed.payload.get('groups', []))
            logger.debug('{} trying to access CMAP with AD groups {}'.format(parsed.accountname, user_groups))
            if not user_groups.intersection(auth_groups):
                return forbidden
        elif typ == 'cert':
            logger.debug('{} trying to access CMAP'.format(parsed.subject.get('cn')))
            if parsed.subject.get('cn') not in cn_whitelist:
                return forbidden
        else:
            return forbidden
    except Exception as e:
        logger.fatal('Cant Parse Auth Token: {}'.format(e))
        return forbidden
