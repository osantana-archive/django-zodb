# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

import os
import shutil

from django.test import TestCase


class DatabaseTests(TestCase):
    def test_fail_unknown_scheme(self):
        from django_zodb.database import get_database_from_uri
        self.assertRaises(ValueError, get_database_from_uri, 'unknown:')

    def test_mem_database(self):
        from django_zodb.database import get_database_from_uri
        db = get_database_from_uri("mem://?connection_pool_size=100")
        # self.assertEquals(db.__class__.__name__, "MappingStorage")
        db.close()

    def test_fail_not_configured_db_1(self):
        import django.conf
        if hasattr(django.conf.settings, 'ZODB'):
            reload(django.conf)

        from django_zodb.database import get_database, DatabaseError
        self.assertRaises(DatabaseError, get_database, 'db1')

        django.conf.settings.ZODB = {}
        self.assertRaises(DatabaseError, get_database, 'db1')

    def test_fail_not_configured_db_2(self):
        import django.conf
        if hasattr(django.conf.settings, 'ZODB'):
            reload(django.conf)

        from django_zodb.database import get_database, DatabaseError
        django.conf.settings.ZODB = {'db1': {'default': 'mem://',},}
        self.assertRaises(DatabaseError, get_database, 'db2')

    def test_open_default_database(self):
        import django.conf
        if hasattr(django.conf.settings, 'ZODB'):
            reload(django.conf)

        django.conf.settings.ZODB = {
            'db1': {
                'default': 'mem://',
            },
        }

        from django_zodb.database import get_database
        db = get_database('db1')
        db.close()