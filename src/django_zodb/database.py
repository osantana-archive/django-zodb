# -*- coding: utf}-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from cStringIO import StringIO

from ZODB.DB import DB
import ZConfig

from django_zodb.config import get_configuration_from_uri, REQUIRED
from django_zodb.storage import get_storage


class DatabaseError(Exception):
    pass


class DatabaseFactory(object):
    _args = (
        ('database_name', str, 'database_name'),
        ('connection_cache_size', int, 'cache_size'),
        ('connection_pool_size', int, 'pool_size'),
    )
    _zconfig_args = (
        ('path', str, 'path', REQUIRED),
        ('frag', str, 'frag'),
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
        frag = settings.get('frag', '')

        schema = ZConfig.loadSchemaFile(StringIO(self._schema_xml_template))
        config, _ = ZConfig.loadConfig(schema, path)
        for database in config.databases:
            if not frag or frag == database.name:
                return database.open()
        else:
            raise ValueError("Database %r not found." % frag)

    def __call__(self):
        if self.config.get('scheme') == 'zconfig':
            return self._get_database_from_zconfig()

        settings = self.config.get_settings(self._args)
        storage = get_storage(self.config)
        return DB(storage, **settings)


def get_database_from_uris(uris):
    databases = {}
    ret = None
    for uri in uris:
        config = get_configuration_from_uri(uri)
        db_factory = DatabaseFactory(config)
        db = db_factory()
        for name in db.databases:
            if name in databases:
                raise ValueError("database_name %r already in databases." % name)
        databases.update(db.databases)
        db.databases = databases
        if ret is None:
            ret = db
    return ret


def get_database_by_name(name):
    from django.conf import settings
    if not hasattr(settings, 'ZODB') or not settings.ZODB:
        raise ValueError("Missing or empty settings.ZODB configuration.")

    try:
        return get_database_from_uris(settings.ZODB[name])
    except KeyError:
        raise ValueError("Database %r not found in settings.ZODB." % name)


class _ConnectionPool(object):
    def __init__(self):
        self._connections = {}

    def get_connection(self, name):
        if name not in self._connections:
            database = get_database_by_name(name)
            self._connections[name] = database.open()
        return self._connections[name]

connections = _ConnectionPool()


def get_connection(name):
    return connections.get_connection(name)
