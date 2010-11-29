# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from django_zodb.utils import parse_uri

REQUIRED = True


def parse_bool(value):
    return value and value.lower()[0] not in 'nf0'


def parse_tuple(values):
    return tuple(value.strip() for value in values.split(","))


class Configuration(object):
    def __init__(self, uri):
        self.configuration = self._parse_uri(uri)

    def _parse_uri(self, uri):
        config = parse_uri(uri)
        query = config.pop('query', {})
        for key, values in query.items():
            if key in config:
                raise ValueError("Cannot override %r argument." % key)
            value = values[-1]  # only last argument
            if value == '':     # ?arg1&arg2&... == ?arg1=1&arg2=1&...
                config[key] = '1'
            else:
                config[key] = value
        return config

    # (uri_arg_name, type_, storage_arg_name, required)
    def get_settings(self, specs):
        ret = {}

        for spec in specs:

            if len(spec) == 3:
                spec = spec + (not REQUIRED,)

            key, type_, arg, required = spec
            try:
                value = self.configuration.pop(key)
                ret[arg] = type_(value)
            except KeyError:
                if required:
                    raise TypeError("Missing argument %r" % key)
            except (ValueError, TypeError):
                raise TypeError("Invalid argument %r" % key)

        return ret

    def pop(self, key, default=None):
        return self.configuration.pop(key, default)

    def get(self, key, default=None):
        return self.configuration.get(key, default)


def get_configuration_from_uri(uri):
    return Configuration(uri)
