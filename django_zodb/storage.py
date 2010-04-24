# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

import os


from ZODB.MappingStorage import MappingStorage
from ZODB.DemoStorage import DemoStorage
from ZODB.blob import BlobStorage
from ZODB.FileStorage.FileStorage import FileStorage

from ZEO.ClientStorage import ClientStorage



from django_zodb.config import get_configuration_from_uri

MB = 1024**2

def parse_bool(value):
    if isinstance(value, basestring):
        return value.lower() not in [ 'no', 'n', 'false', '0' ]

class StorageFactory(object):
    def __init__(self, config):
        self.settings = config.get_settings(self._args)
        self.demostorage = config.pop('demostorage', False)

    def _wrap_blob(self, storage, blob_dir, blob_layout):
        if blob_dir:
            return BlobStorage(blob_dir, storage, blob_layout)
        return storage

    def get_base_storage(self, *args, **kwargs):
        raise NotImplemented("Abstract class") # pragma: no cover abstract method code

    def get_storage(self):
        storage = self.get_base_storage(**self.settings)
        if self.demostorage:
            storage = DemoStorage(base=storage)
        return storage


class MemoryFactory(StorageFactory):
    _args = (
        ('blobstorage_dir', str, 'blob_dir', ""),
        ('blobstorage_layout', str, 'blob_layout', "automatic"),
    )
    def get_base_storage(self, blob_dir, blob_layout):
        return self._wrap_blob(MappingStorage(), blob_dir, blob_layout)

class FileFactory(StorageFactory):
    _args = (
        ('path', os.path.normpath, 'filename'),
        ('create', parse_bool, 'create', False),
        ('read_only', parse_bool, 'readonly', False),
        ('quota', int, 'quota', None),
        ('blobstorage_dir', str, 'blob_dir', ''),
        ('blobstorage_layout', str, 'blob_layout', "automatic"),
    )
    def get_base_storage(self, filename, create, readonly, quota, blob_dir, blob_layout):
        storage = FileStorage(
                    file_name=filename,
                    create=create,
                    read_only=readonly,
                    quota=quota)
        return self._wrap_blob(storage, blob_dir, blob_layout)

class ZEOFactory(StorageFactory):
    _args = (
        # uri_arg_name, type_, storage_arg_name, (optional)default
        ('host', str, 'host', None),
        ('port', int, 'port', 8100),
        ('path', str, 'path', None),

        ('storage', str, 'storage', '1'),
        ('cache_size', int, 'cache_size', 20*MB),
        ('name', str, 'name', ''),
        ('client', str, 'client', None),
        # ('debug', parse_bool, 'debug', 0), repoze.zodbconn but ZODB use it.
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


class MySQLFactory(StorageFactory):
    pass

class PostgreSQLFactory(StorageFactory):
    pass

FACTORIES = {
    'mem': MemoryFactory,
    'memory': MemoryFactory,
    'file': FileFactory,
    'zeo': ZEOFactory,
    'postgresql': PostgreSQLFactory,
    'mysql': MySQLFactory,
}

def get_storage(config):
    try:
        scheme = config.pop('scheme')
        factory = FACTORIES[scheme]
    except KeyError:
        raise ValueError('Invalid or Unknown scheme: %s' % (scheme,))

    storage = factory(config).get_storage()

    return storage

def get_storage_from_uri(uri):
    config = get_configuration_from_uri(uri)
    return get_storage(config)
