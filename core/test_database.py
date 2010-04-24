# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from django.test import TestCase


from testutils.tools import remove_db_files, start_zeo, get_tool_path, turn_off_log


turn_off_log("ZODB.FileStorage")
turn_off_log("ZEO.zrpc")

class DatabaseTests(TestCase):
    def test_fail_unknown_scheme(self):
        from django_zodb.database import get_database_from_uri
        self.assertRaises(ValueError, get_database_from_uri, 'unknown:')

    def test_mem_database(self):
        from django_zodb.database import get_database_from_uri
        db = get_database_from_uri("mem://?connection_pool_size=100&database_name=foo")
        self.assertEquals(db._db.getName(), 'MappingStorage')
        self.assertTrue('foo' in db._db.databases)
        db.close()

    def test_zconfig_database_1(self):
        from django_zodb.database import get_database_from_uri
        db = get_database_from_uri("zconfig://" + get_tool_path('zconfig.zcml') + "#temp2")
        self.assertTrue('temp2' in db._db.databases)
        db.close()

    def test_zconfig_database_2(self):
        from django_zodb.database import get_database_from_uri
        db = get_database_from_uri("zconfig://" + get_tool_path('zconfig.zcml'))
        self.assertTrue('temp1' in db._db.databases)
        db.close()

    def test_fail_zconfig_unknown_database(self):
        from django_zodb.database import get_database_from_uri, DatabaseError
        uri = "zconfig://" + get_tool_path('zconfig.zcml') + "#unknown"
        self.assertRaises(DatabaseError, get_database_from_uri, uri)

    def test_fail_not_configured_db_1(self):
        import django.conf
        if hasattr(django.conf.settings, 'ZODB'):
            reload(django.conf)

        from django_zodb.database import get_database_by_name, DatabaseError
        self.assertRaises(DatabaseError, get_database_by_name, 'db1')

        django.conf.settings.ZODB = {}
        self.assertRaises(DatabaseError, get_database_by_name, 'db1')

    def test_fail_not_configured_db_2(self):
        import django.conf
        if hasattr(django.conf.settings, 'ZODB'):
            reload(django.conf)

        from django_zodb.database import get_database_by_name, DatabaseError
        django.conf.settings.ZODB = {'db1': {'default': 'mem://',},}
        self.assertRaises(DatabaseError, get_database_by_name, 'db2')

    def test_open_default_database(self):
        import django.conf
        if hasattr(django.conf.settings, 'ZODB'):
            reload(django.conf)

        django.conf.settings.ZODB = {
            'db1': {
                'default': 'file:///tmp/test.db',
            },
        }

        from django_zodb.database import get_database_by_name
        db = get_database_by_name('db1')
        db.close()