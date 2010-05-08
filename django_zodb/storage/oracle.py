# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from relstorage.adapters.oracle import OracleAdapter
from relstorage.options import Options

from django_zodb.config import parse_bool
from django_zodb.storage.rdbms import RelStorageFactory


class OracleFactory(RelStorageFactory):
    _adapter = OracleAdapter
    _adapter_args = (
        ('user', str, 'user'),
        ('password', str, 'password'),
        ('dsn', str, 'dsn'),
        ('twophase', parse_bool, 'twophase'),
    )

    def get_adapter(self, options):
        options = Options(**options)
        settings = self.config.get_settings(self._adapter_args)
        return self._adapter(options=options, **settings)
