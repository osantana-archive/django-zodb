# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from relstorage.adapters.postgresql import PostgreSQLAdapter
from relstorage.options import Options

from django_zodb.storage.rdbms import RelStorageFactory


class PostgreSQLFactory(RelStorageFactory):
    _adapter = PostgreSQLAdapter
    _adapter_args = (
        ('frag', str, 'dbname'),
        ('host', str, 'host'),
        ('port', int, 'port'),
        ('user', str, 'user'),
        ('password', str, 'password'),
        ('sslmode', str, 'sslmode'),
        ('connect_timeout', int, 'connect_timeout'),
    )

    def get_adapter(self, options):
        options = Options(**options)
        settings = self.config.get_settings(self._adapter_args)
        args = []
        for key in sorted(settings.keys()):
            args.append("%s=%s" % (key, settings[key]))
        dsn = " ".join(args)
        return self._adapter(dsn=dsn, options=options)
