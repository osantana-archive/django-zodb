# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from relstorage.storage import RelStorage

from django_zodb.storage import StorageFactory
from django_zodb.config import parse_bool, parse_tuple, IGNORE

class RelStorageFactory(StorageFactory):
    _storage = RelStorage
    _storage_args = (
        ('name', str, 'name', IGNORE),
        ('create', parse_bool, 'create', IGNORE),
        ('read_only', parse_bool, 'read_only', IGNORE),
        ('blobstorage_dir', str, 'blob_dir', IGNORE),
        ('poll_interval', int, 'poll_interval', IGNORE),
        ('keep_history', parse_bool, 'keep_history', IGNORE),
        ('replica_conf', str, 'replica_conf', IGNORE),
        ('replica_timeout', float, 'replica_timeout', IGNORE),
        ('pack_gc', parse_bool, 'pack_gc', IGNORE),
        ('pack_dry_run', parse_bool, 'pack_dry_run', IGNORE),
        ('pack_batch_timeout', float, 'pack_batch_timeout', IGNORE),
        ('pack_duty_cycle', float, 'pack_duty_cycle', IGNORE),
        ('pack_max_delay', float, 'pack_max_delay', IGNORE),
        ('cache_servers', parse_tuple, 'cache_servers', IGNORE),
        ('cache_module_name', str, 'cache_module_name', IGNORE),
        ('cache_prefix', str, 'cache_prefix', IGNORE),
        ('cache_local_mb', int, 'cache_local_mb', IGNORE),
        ('cache_delta_size_limit', int, 'cache_delta_size_limit', IGNORE),
        # ('cache', str, 'cache', None), # XXX: Is there an alternative to default relstorage.cache.StorageCache?
    )

    def get_base_storage(self, **options): # receive self._args
        create = options.pop("create")
        adapter = self.get_adapter(options)
        return self._storage(adapter, **options)
