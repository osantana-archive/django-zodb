# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from cStringIO import StringIO


from django_zodb.config import get_configuration_from_uri
from django_zodb.storage import get_storage


from ZODB.DB import DB

import ZConfig



class DatabaseError(Exception):
    pass


class Database(object):
    def __init__(self, _db):
        self._db = _db

    def close(self):
        self._db.close()


class DatabaseFactory(object):
    _args = (
        ('database_name', str, 'database_name', 'unnamed'),
        ('connection_cache_size', int, 'cache_size', 10000),
        ('connection_pool_size', int, 'pool_size', 7),
    )
    _zconfig_args = (
        ('path', str, 'path'),
        ('frag', str, 'frag', ''),
    )
    _schema_xml_template = """<schema>
        <import package="ZODB"/>
        <multisection type="ZODB.database" attribute="databases" />
    </schema>"""

    def __init__(self, config):
        self.config = config

    def _get_database_from_zconfig(self):
        settings = self.config.get_settings(self._zconfig_args)
        path = settings['path']
        frag = settings['frag']

        schema = ZConfig.loadSchemaFile(StringIO(self._schema_xml_template))
        config, _ = ZConfig.loadConfig(schema, path)
        for database in config.databases:
            if not frag or frag == database.name:
                break
        else:
            raise DatabaseError("No database named '%s' found" % (frag,))

        return Database(database.open())

    def get_database(self):
        if self.config.get('scheme') == 'zconfig':
            return self._get_database_from_zconfig()

        settings = self.config.get_settings(self._args)
        storage = get_storage(self.config)
        _db = DB(storage, **settings)
        return Database(_db)


def get_database_from_uri(uri):
    config = get_configuration_from_uri(uri)
    factory = DatabaseFactory(config)
    return factory.get_database()

def get_database_by_name(name, uri='default'):
    from django.conf import settings
    if not hasattr(settings, 'ZODB') or not settings.ZODB:
        raise DatabaseError("Missing 'settings.ZODB' configuration (or empty).")

    try:
        db = get_database_from_uri(settings.ZODB[name][uri])
    except KeyError:
        raise DatabaseError("No database '%s.%s' configuration in settings.ZODB" % (name, uri))
    return db
