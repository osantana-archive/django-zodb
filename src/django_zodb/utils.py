# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import re
from urllib.parse import parse_qs

# http://stackoverflow.com/questions/1175208/
FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')


def camel_case_to_underline(name):
    conv1 = FIRST_CAP_RE.sub(r'\1_\2', name)
    return ALL_CAP_RE.sub(r'\1_\2', conv1).lower()


def parse_uri(uri):

    def _push(ret, key, buf, next_key=None):
        if not buf:
            return next_key or key, []
        ret[key] = ''.join(buf)
        return next_key or key, []

    ret = {}
    has_dslash = "://" in uri
    has_user = bool(re.search(':(//)?[^:@?/#&\s]+:?@', uri))
    if "#" in uri:
        uri, frag = uri.rsplit("#", 1)
        ret['frag'] = frag

    key = 'scheme'
    buf = []
    for character in uri:
        if character == ":":
            if key == 'scheme':
                key, buf = _push(ret, key, buf)
                if has_dslash:
                    key = 'dslash1'
                elif has_user:
                    key = 'user'
                else:
                    key = 'host'
                continue
            elif key == 'user':
                key, buf = _push(ret, key, buf, 'password')
                continue
            elif key == 'host':
                key, buf = _push(ret, key, buf, 'port')
                continue

        if character == "/":
            if key == 'dslash1':
                key = 'dslash2'
                continue
            if key == 'dslash2':
                if has_user:
                    key = 'user'
                else:
                    key = 'host'
                continue

            if key not in ['path', 'query']:
                key, buf = _push(ret, key, buf, 'path')

        if character == "@":
            if key in ['user', 'password']:
                key, buf = _push(ret, key, buf, 'host')
                continue

        if character == "?":
            if key != "query":
                key, buf = _push(ret, key, buf, 'query')
                continue

        buf.append(character)

    # append remaining chars in buffer
    if buf:
        ret[key] = ''.join(buf)

    # sanitize
    if 'port' in ret:
        ret['port'] = int(ret['port'])
    if 'query' in ret:
        ret['query'] = parse_qs(ret['query'], keep_blank_values=True)

    return ret


# Repoze.BFG url_quote()
always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')
_safemaps = {}
_must_quote = {}


def url_quote(url_orig, safe=''):
    cachekey = (safe, always_safe)
    try:
        safe_map = _safemaps[cachekey]
        if not _must_quote[cachekey].search(url_orig):
            return url_orig
    except KeyError:
        safe += always_safe
        _must_quote[cachekey] = re.compile(r'[^%s]' % safe)
        safe_map = {}
        for i in range(256):
            char = chr(i)
            safe_map[char] = (char in safe) and char or ('%%%02X' % i)
        _safemaps[cachekey] = safe_map
    res = [safe_map[char] for char in url_orig]
    return ''.join(res)
