# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from relstorage.adapters.mysql import MySQLAdapter
from relstorage.options import Options

from django_zodb.config import IGNORE, parse_bool
from django_zodb._rdbms import RelStorageFactory


class MySQLFactory(RelStorageFactory):
    _adapter = MySQLAdapter
    _adapter_args = (
        ('user', str, 'user', IGNORE),
        ('password', str, 'passwd', IGNORE),
        ('host', str, 'host', IGNORE),
        ('port', int, 'port', IGNORE),
        ('frag', str, 'db', ""),
        ('path', str, 'unix_socket', IGNORE),
        ('connect_timeout', int, 'connect_timeout', IGNORE),
        ('compress', parse_bool, 'compress', IGNORE),
        ('named_pipe', parse_bool, 'named_pipe', IGNORE),
        ('init_command', str, 'init_command', IGNORE),
        ('read_default_file', str, 'read_default_file', IGNORE),
        ('read_default_group', str, 'read_default_group', IGNORE),
        ('client_flag', int, 'client_flag', IGNORE),
        ('load_infile', int, 'load_infile', IGNORE),
        ('create', parse_bool, 'create', IGNORE),
    )

    def get_adapter(self, options):
        options = Options(**options)
        settings = self.config.get_settings(self._adapter_args)
        return self._adapter(options=options, **settings)
