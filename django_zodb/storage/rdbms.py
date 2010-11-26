# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from relstorage.storage import RelStorage

from django_zodb.storage.base import AbstractStorageFactory
from django_zodb.config import parse_bool, parse_tuple


class RelStorageFactory(AbstractStorageFactory):
    _storage = RelStorage
    _storage_args = (
        ('name', str, 'name'),
        ('read_only', parse_bool, 'read_only'),
        ('blob_dir', str, 'blob_dir'),
        ('shared_blob_dir', bool, 'shared_blob_dir'),
        ('blob_cache_size', int, 'blob_cache_size'),
        ('blob_cache_size_check', int, 'blob_cache_size_check'),
        ('blob_cache_chunk_size', int, 'blob_cache_chunk_size'),
        ('keep_history', parse_bool, 'keep_history'),
        ('replica_conf', str, 'replica_conf'),
        ('replica_timeout', float, 'replica_timeout'),
        ('poll_interval', int, 'poll_interval'),
        ('pack_gc', parse_bool, 'pack_gc'),
        ('pack_dry_run', parse_bool, 'pack_dry_run'),
        ('pack_batch_timeout', float, 'pack_batch_timeout'),
        ('pack_duty_cycle', float, 'pack_duty_cycle'),
        ('pack_max_delay', float, 'pack_max_delay'),
        ('cache_servers', parse_tuple, 'cache_servers'),
        ('cache_module_name', str, 'cache_module_name'),
        ('cache_prefix', str, 'cache_prefix'),
        ('cache_local_mb', int, 'cache_local_mb'),
        ('cache_delta_size_limit', int, 'cache_delta_size_limit'),
        ('commit_lock_timeout', int, 'commit_lock_timeout'),
        ('commit_lock_id', int, 'commit_lock_id'),
        ('strict_tpc', bool, 'strict_tpc'),
        ('create', parse_bool, 'create'),
    )

    def get_adapter(self, *args, **kwargs):
        raise NotImplemented("Abstract class: %r, %r" % (args, kwargs))  # pragma: no cover abstract method code

    def get_base_storage(self, **options):
        create = options.pop("create", True)  # HACK: missing in relstorage.options.Options(?)
        adapter = self.get_adapter(options)
        options['create'] = create
        options['adapter'] = adapter
        return self._storage(**options)
