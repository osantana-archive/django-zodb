# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from relstorage.adapters.oracle import OracleAdapter
from relstorage.options import Options

from django_zodb.relstorage import RelStorageFactory

# TODO: add support and tests to oracle
class OracleFactory(RelStorageFactory):
    _adapter = OracleAdapter
    _adapter_args = ()
    # user, password, dsn, twophase=False, options=None

    def get_adapter(self, options):
        raise NotImplemented("TODO")

        options = Options(**options)
        settings = self.config.get_settings(self._adapter_args)
        return self._adapter(options=options, **settings)
