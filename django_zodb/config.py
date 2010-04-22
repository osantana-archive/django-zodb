# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from django_zodb.utils import parse_uri


DATABASE_SETTINGS = (
    # key, type, default
    ('database_name', str, 'unnamed'),
    ('connection_cache_size', int, 10000),
    ('connection_pool_size', int, 7),
)

class Configuration(object):
    def __init__(self, uri):
        self.storage_settings = self._parse_uri(uri)
        self.db_settings = self._get_db_settings(self.storage_settings)

    def _parse_uri(self, uri):
        settings = parse_uri(uri)
        if 'query' in settings:
            query = settings.pop('query')
            for key, values in query.items():
                value = values[-1] # only last argument
                if value == '':    # ?arg1&arg2&...
                    settings['query.' + key] = '1'
                else:
                    settings['query.' + key] = value
        return settings

    def _get_db_settings(self, settings):
        ret = {}
        for key, type_, default in DATABASE_SETTINGS:
            if key in settings:
                ret[key] = type_(settings.pop(key))
            else:
                ret[key] = default
        return ret

def get_configuration_from_uri(uri):
    return Configuration(uri)
