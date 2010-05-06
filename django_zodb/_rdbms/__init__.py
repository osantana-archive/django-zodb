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
    _args = (
        ('name', str, 'name', None),
        ('read_only', parse_bool, 'read_only', False),
        ('blobstorage_dir', str, 'blob_dir', None),
        ('poll_interval', int, 'poll_interval', 0),
        ('keep_history', parse_bool, 'keep_history', True),
        ('replica_conf', str, 'replica_conf', None),
        ('replica_timeout', float, 'replica_timeout', 600.0),
        ('pack_gc', parse_bool, 'pack_gc', True),
        ('pack_dry_run', parse_bool, 'pack_dry_run', False),
        ('pack_batch_timeout', float, 'pack_batch_timeout', 5.0),
        ('pack_duty_cycle', float, 'pack_duty_cycle', 0.5),
        ('pack_max_delay', float, 'pack_max_delay', 20.0),
        ('cache_servers', parse_tuple, 'cache_servers', ()),
        ('cache_module_name', str, 'cache_module_name', 'memcache'),
        ('cache_prefix', str, 'cache_prefix', ''),
        ('cache_local_mb', int, 'cache_local_mb', 10),
        ('cache_delta_size_limit', int, 'cache_delta_size_limit', 10000),
        ('commit_lock_timeout', int, 'commit_lock_timeout', 30),
        ('commit_lock_id', int, 'commit_lock_id', 0),
    )

    def get_adapter(self):
        pass

    def get_base_storage(self, **kwargs): # receive _args
        adapter = self.get_adapter()
        return RelStorage(adapter, **kwargs)

# import relstorage
# from relstorage.relstorage import RelStorage
# kwds = args_to_kwds(args)
# if args['db_type'] == 'mysql':
#     from relstorage.adapters.mysql import MySQLAdapter
#     adapter = MySQLAdapter(**kwds)
# elif args['db_type'] == 'postgresql':
#     from relstorage.adapters.postgresql import PostgreSQLAdapter
#     adapter = PostgreSQLAdapter(**kwds)
# elif args['db_type'] == 'oracle':
#     from relstorage.adapters.oracle import OracleAdapter
#     adapter = OracleAdapter(**kwds)
# else:
#     err_msg = 'unknown database type: %s' % args['db_type']
#     raise NotImplementedError, err_msg
# storage = RelStorage(adapter)
