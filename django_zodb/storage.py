# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import os
import logging

from ZODB.MappingStorage import MappingStorage
from ZODB.DemoStorage import DemoStorage
from ZODB.blob import BlobStorage
from ZODB.FileStorage.FileStorage import FileStorage

from ZEO.ClientStorage import ClientStorage

from django_zodb.config import get_configuration_from_uri, parse_bool, IGNORE



# Utilities
MB = 1024 ** 2
log = logging.getLogger("django_zodb.storage")

# Storage Factories registry
FACTORIES = {}

def register(scheme, factory_class):
    FACTORIES[scheme] = factory_class

def get_available_storages():
    return FACTORIES.keys()

def get_storage_factory(scheme):
    return FACTORIES[scheme]

# Storage Factories
class StorageFactory(object):
    def __init__(self, config):
        self.demostorage = config.pop('demostorage', False)
        self.config = config

    def _wrap_blob(self, storage, **kwargs):
        if 'base_directory' not in kwargs:
            return storage
        return BlobStorage(storage=storage, **kwargs)

    def get_base_storage(self, *args, **kwargs):
        raise NotImplemented("Abstract class") # pragma: no cover abstract method code

    def get_storage(self):
        settings = self.config.get_settings(self._storage_args)
        storage = self.get_base_storage(**settings)
        if self.demostorage:
            storage = DemoStorage(base=storage)
        return storage


class MemoryFactory(StorageFactory):
    _storage = MappingStorage
    _storage_args = (
        ('blobstorage_dir', str, 'base_directory', IGNORE),
        ('blobstorage_layout', str, 'layout', IGNORE),
    )
    def get_base_storage(self, **kwargs):
        return self._wrap_blob(self._storage(), **kwargs)
register("mem", MemoryFactory)


class FileFactory(StorageFactory):
    _storage = FileStorage
    _storage_args = (
        ('path', os.path.normpath, 'file_name'),
        ('create', parse_bool, 'create', IGNORE),
        ('read_only', parse_bool, 'read_only', IGNORE),
        ('quota', int, 'quota', IGNORE),
        ('blobstorage_dir', str, 'base_directory', IGNORE),
        ('blobstorage_layout', str, 'layout', IGNORE),
    )
    def get_base_storage(self, **kwargs):
        arguments = {}
        if 'base_directory' in kwargs:
            arguments['base_directory'] = kwargs.pop("base_directory")
        if 'layout' in kwargs:
            arguments['layout'] = kwargs.pop("layout")
        arguments['storage'] = self._storage(**kwargs)
        return self._wrap_blob(**arguments)
register("file", FileFactory)


class ZEOFactory(StorageFactory):
    _storage_args = (
        ('host', str, 'host', None),
        ('port', int, 'port', 8100),
        ('path', str, 'path', None),
        ('storage', str, 'storage', '1'),
        ('cache_size', int, 'cache_size', 20*MB),
        ('name', str, 'name', ''),
        ('client', str, 'client', None),
        ('var', str, 'var', None),
        ('min_disconnect_poll', int, 'min_disconnect_poll', 1),
        ('max_disconnect_poll', int, 'max_disconnect_poll', 30),
        ('wait', parse_bool, 'wait', None),
        ('wait_timeout', int, 'wait_timeout', None),
        ('read_only', parse_bool, 'read_only', 0),
        ('read_only_fallback', parse_bool, 'read_only_fallback', 0),
        ('username', str, 'username', ''),
        ('password', str, 'password', ''),
        ('realm', str, 'realm', None),
        ('blob_dir', str, 'blob_dir', None),
        ('shared_blob_dir', parse_bool, 'shared_blob_dir', False),
        ('drop_cache_rather_verify', parse_bool, 'drop_cache_rather_verify', False),
        ('blob_cache_size', int, 'blob_cache_size', None),
        ('blob_cache_size_check', int, 'blob_cache_size_check', 10),
    )

    def get_base_storage(self, **kwargs):
        host = kwargs.pop('host')
        port = kwargs.pop('port')
        path = kwargs.pop('path')
        kwargs['addr'] = (host, port) if host else path
        return ClientStorage(**kwargs)
register("zeo", ZEOFactory)

try:
    from _rdbms.mysql import MySQLFactory
    register("mysql", MySQLFactory)
except ImportError:
    log.info("MySQL support disabled.")

try:
    from _rdbms.postgresql import PostgreSQLFactory
    register("postgresql", PostgreSQLFactory)
except ImportError:
    log.info("PostgreSQL support disabled.")

try:
    from _rdbms.oracle import OracleFactory
    register("oracle", OracleFactory)
except ImportError:
    log.info("Oracle support disabled.")


def get_storage(config):
    try:
        scheme = config.pop('scheme')
        factory = get_storage_factory(scheme)
    except KeyError:
        raise ValueError('Invalid or Unknown scheme: %s' % (scheme,))

    storage = factory(config).get_storage()

    return storage

def get_storage_from_uri(uri):
    config = get_configuration_from_uri(uri)
    return get_storage(config)
