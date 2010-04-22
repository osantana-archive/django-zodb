# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import re
from urlparse import parse_qs

_URI_CACHE = {}

def parse_uri(uri, local_schemes=('file',)):
    if (uri, local_schemes) in _URI_CACHE:
        return _URI_CACHE[(uri, local_schemes)]

    def _push(ret, key, buf, next_key=None):
        if not buf:
            return next_key or key, []
        ret[key] = ''.join(buf)
        return next_key or key, []

    ret = {}
    has_dslash = "://" in uri
    has_username = bool(re.search(':(//)?[a-z0-9-]+:?@', uri))
    if "#" in uri:
        uri, frag = uri.rsplit("#", 1)
        ret['frag'] = frag

    key = 'scheme'
    buf = []
    for ch in uri:
        if ch == ":":
            if key == 'scheme':
                key, buf = _push(ret, key, buf)
                if has_dslash:
                    key = 'dslash1'
                elif has_username:
                    key = 'username'
                else:
                    key = 'hostname'
                continue
            elif key == 'username':
                key, buf = _push(ret, key, buf, 'password')
                continue
            elif key == 'hostname':
                key, buf = _push(ret, key, buf, 'port')
                continue

        if ch == "/":
            if key == 'dslash1':
                key = 'dslash2'
                continue
            if key == 'dslash2':
                if ret['scheme'] in local_schemes:
                    key = 'path'
                elif has_username:
                    key = 'username'
                else:
                    key = 'hostname'
                continue

            if key not in ['path', 'query']:
                key, buf = _push(ret, key, buf, 'path')

        if ch == "@":
            if key in ['username', 'password']:
                key, buf = _push(ret, key, buf, 'hostname')
                continue

        if ch == "?":
            if key != "query":
                key, buf = _push(ret, key, buf, 'query')
                continue

        # if ch == "#"
        #     key, buf = _push(ret, key, buf, 'frag')
        #     continue

        buf.append(ch)

    # append remaining chars in buffer
    if buf:
        ret[key] = ''.join(buf)

    # sanitize
    if 'port' in ret:
        ret['port'] = int(ret['port'])
    if 'query' in ret:
        ret['query'] = parse_qs(ret['query'], keep_blank_values=True)

    _URI_CACHE[(uri, local_schemes)] = ret
    return ret
