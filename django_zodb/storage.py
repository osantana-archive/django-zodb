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

from django_zodb.config import get_configuration_from_uri, parse_bool, REQUIRED


# Utilities
log = logging.getLogger("django_zodb.storage")

# Storage Factories registry
class _FactoriesRegistry(object):
    def __init__(self):
        self.enabled = {}
        self.disabled = {}

    def enable(self, scheme, factory_class):
        self.enabled[scheme] = factory_class

    def disable(self, scheme, reason):
        self.disabled[scheme] = str(reason)

    def available(self):
        return self.enabled.keys()

    def get(self, scheme):
        return self.enabled[scheme]

    def disable_reason(self, scheme):
        return self.disabled[scheme]

factories = _FactoriesRegistry()

# Storage Factories
class StorageFactory(object):
    def __init__(self, config):
        self.demostorage = parse_bool(config.pop('demostorage', "false"))
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
        ('blobstorage_dir', str, 'base_directory'),
        ('blobstorage_layout', str, 'layout'),
    )
    def get_base_storage(self, **kwargs):
        return self._wrap_blob(self._storage(), **kwargs)
factories.enable("mem", MemoryFactory)


class FileFactory(StorageFactory):
    _storage = FileStorage
    _storage_args = (
        ('path', os.path.normpath, 'file_name', REQUIRED),
        ('create', parse_bool, 'create'),
        ('read_only', parse_bool, 'read_only'),
        ('quota', int, 'quota'),
        ('blobstorage_dir', str, 'base_directory'),
        ('blobstorage_layout', str, 'layout'),
    )
    def get_base_storage(self, **kwargs):
        arguments = {}
        if 'base_directory' in kwargs:
            arguments['base_directory'] = kwargs.pop("base_directory")
        if 'layout' in kwargs:
            arguments['layout'] = kwargs.pop("layout")
        arguments['storage'] = self._storage(**kwargs)
        return self._wrap_blob(**arguments)
factories.enable("file", FileFactory)


class ZEOFactory(StorageFactory):
    _storage = ClientStorage
    _storage_args = (
        ('host', str, 'host'),
        ('port', int, 'port'),
        ('path', str, 'path'),
        ('storage', str, 'storage'),
        ('cache_size', int, 'cache_size'),
        ('name', str, 'name'),
        ('client', str, 'client'),
        ('var', str, 'var'),
        ('min_disconnect_poll', int, 'min_disconnect_poll'),
        ('max_disconnect_poll', int, 'max_disconnect_poll'),
        ('wait', parse_bool, 'wait'),
        ('wait_timeout', int, 'wait_timeout'),
        ('read_only', parse_bool, 'read_only'),
        ('read_only_fallback', parse_bool, 'read_only_fallback'),
        ('username', str, 'username'),
        ('password', str, 'password'),
        ('realm', str, 'realm'),
        ('blobstorage_dir', str, 'blob_dir'),
        ('shared_blob_dir', parse_bool, 'shared_blob_dir'),
        ('drop_cache_rather_verify', parse_bool, 'drop_cache_rather_verify'),
        ('blob_cache_size', int, 'blob_cache_size'),
        ('blob_cache_size_check', int, 'blob_cache_size_check'),
    )

    def get_base_storage(self, **kwargs):
        host = kwargs.pop('host', None)
        port = kwargs.pop('port', 8090)
        path = kwargs.pop('path', None)
        if host and port:
            kwargs['addr'] = (host, port)
        elif path:
            kwargs['addr'] = path
        else:
            raise ValueError("Missing host:port address or path to socket to ZEO Server.")
        return self._storage(**kwargs)
factories.enable("zeo", ZEOFactory)


try:
    from django_zodb.relstorage.mysql import MySQLFactory
    factories.enable("mysql", MySQLFactory)
except ImportError, ex: # pragma: no cover
    factories.disable("mysql", ex)

try:
    from django_zodb.relstorage.postgresql import PostgreSQLFactory
    factories.enable("postgresql", PostgreSQLFactory)
except ImportError, ex: # pragma: no cover
    factories.disable("postgresql", ex)

try:
    from django_zodb.relstorage.oracle import OracleFactory
    factories.enable("oracle", OracleFactory)
except ImportError, ex: # pragma: no cover
    factories.disable("oracle", ex)

def get_storage(config):
    try:
        scheme = config.pop('scheme')
        factory = factories.get(scheme)
    except KeyError:
        raise ValueError('Invalid or Unknown scheme: %s' % (scheme,))

    storage = factory(config).get_storage()

    return storage

def get_storage_from_uri(uri):
    config = get_configuration_from_uri(uri)
    return get_storage(config)
