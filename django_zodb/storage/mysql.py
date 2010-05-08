# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from relstorage.adapters.mysql import MySQLAdapter
from relstorage.options import Options

from django_zodb.config import parse_bool
from django_zodb.storage.rdbms import RelStorageFactory


class MySQLFactory(RelStorageFactory):
    _adapter = MySQLAdapter
    _adapter_args = (
        ('host', str, 'host'),
        ('user', str, 'user'),
        ('password', str, 'passwd'),
        ('frag', str, 'db'),
        ('port', int, 'port'),
        ('path', str, 'unix_socket'),
        ('connect_timeout', int, 'connect_timeout'),
        ('compress', parse_bool, 'compress'),
        ('named_pipe', parse_bool, 'named_pipe'),
        ('init_command', str, 'init_command'),
        ('read_default_file', str, 'read_default_file'),
        ('read_default_group', str, 'read_default_group'),
        ('client_flag', int, 'client_flag'),
        ('load_infile', int, 'load_infile'),
    )

    def get_adapter(self, options):
        options = Options(**options)
        settings = self.config.get_settings(self._adapter_args)
        return self._adapter(options=options, **settings)
