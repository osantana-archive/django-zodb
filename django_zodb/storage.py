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

from django_zodb.config import get_configuration_from_uri


def parse_bool(value):
    if isinstance(value, basestring):
        return value.lower() not in [ 'no', 'n', 'false', '0' ]

class StorageFactory(object):
    _args = (
        # uri_arg_name, type_, storage_arg_name, (optional)default
    )
    def __init__(self, settings):
        self.settings = self._sanitize_settings(settings)
        self.storage_stack = [
            self.get_base_storage,
            self.get_demo_storage,
            self.get_blob_storage,
        ]

    def _sanitize_settings(self, settings):
        ret = {}

        for record in self._args:
            if len(record) > 3:
                key, type_, arg, default = record
                required = False
            else:
                key, type_, arg = record
                required = True

            try:
                ret[arg] = type_(settings[key])
            except (KeyError, ValueError, TypeError):
                if required:
                    raise TypeError("Missing or invalid argument '%s'" % (key,))
                ret[arg] = default
        return ret

    def get_base_storage(self, base_storage):
        raise NotImplemented("Abstract class")

    def get_demo_storage(self, base_storage):
        if not self.settings.get('demostorage', False):
            return base_storage
        return DemoStorage(base=base_storage)

    def get_blob_storage(self, base_storage):
        blob_dir = self.settings.get('blobstorage_dir', '')
        if not blob_dir:
            return base_storage

        blob_layout = self.settings.get('blobstorage_layout', 'automatic')
        return BlobStorage(blob_dir, base_storage, blob_layout)

    def get_storage(self, base_storage=None):
        storage = base_storage
        for wrapper in self.storage_stack:
            storage = wrapper(storage)
        return storage

class MemoryFactory(StorageFactory):
    def get_base_storage(self, base_storage):
        return MappingStorage()

class FileFactory(StorageFactory):
    _args = (
        # uri_arg_name, type_, storage_arg_name, (optional)default
        ('path', os.path.normpath, 'file_name'),
        ('query.create', parse_bool, 'create', False),
        ('query.read_only', parse_bool, 'read_only', False),
        ('query.quota', int, 'quota', None),
    )
    def get_base_storage(self, base_storage):
        return FileStorage(**self.settings)

class ZEOFactory(StorageFactory):
    pass

class ZConfigFactory(StorageFactory):
    pass

class RelStorageFactory(StorageFactory):
    pass

class MySQLFactory(StorageFactory):
    pass

class PostgreSQLFactory(StorageFactory):
    pass

FACTORIES = {
    'mem': MemoryFactory,
    'memory': MemoryFactory,
    'file': FileFactory,
    'zeo': ZEOFactory,
    'zeoclient': ZEOFactory,
    'zconfig': ZConfigFactory,
    'postgres': PostgreSQLFactory,
    'postgresql': PostgreSQLFactory,
    'mysql': MySQLFactory,
}

def get_storage(settings):
    scheme = settings['scheme']
    try:
        factory = FACTORIES[scheme]
    except KeyError:
        raise ValueError('Invalid or Unknown scheme: %s' % (scheme,))

    storage = factory(settings).get_storage()

    return storage

def get_storage_from_uri(uri):
    config = get_configuration_from_uri(uri)
    return get_storage(config.storage_settings)
