# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from relstorage.adapters.mysql import MySQLAdapter

from django_zodb._rdbms import RelStorageFactory

class MySQLFactory(RelStorageFactory):
    _adapter_args = ()

    def get_adapter(self):
        options = self.config.get_settings(self._adapter_args)
        print "get_adapter() options:", options
        return MySQLAdapter(**options)
