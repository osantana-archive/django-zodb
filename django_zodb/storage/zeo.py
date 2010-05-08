# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from ZEO.ClientStorage import ClientStorage

from django_zodb.config import parse_bool
from django_zodb.storage.base import AbstractStorageFactory


class ZEOFactory(AbstractStorageFactory):
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
