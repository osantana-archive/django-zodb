# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from django.test import TestCase


from testutils.tools import get_tool_uri_path, turn_off_log, TEMP_DIR_URI


turn_off_log("ZODB.FileStorage")
turn_off_log("ZEO.zrpc")

class DatabaseTests(TestCase):

    def test_fail_unknown_scheme(self):
        from django_zodb.database import get_database_from_uris
        self.assertRaises(ValueError, get_database_from_uris, ['unknown:'])

    def test_mem_database(self):
        from django_zodb.database import get_database_from_uris
        db = get_database_from_uris(["mem://"])
        self.assertEqual("unnamed", db.database_name)
        self.assertTrue("unnamed" in db.databases)
        self.assertEqual("MappingStorage", db.getName())

    def test_mem_demo_database(self):
        from django_zodb.database import get_database_from_uris
        db = get_database_from_uris(["mem://?demostorage=true"])
        self.assertEqual("unnamed", db.database_name)
        self.assertTrue("unnamed" in db.databases)
        self.assertEqual("DemoStorage('MappingStorage', 'MappingStorage')", db.getName())

    def test_fail_multi_db_same_name(self):
        from django_zodb.database import get_database_from_uris
        self.assertRaises(ValueError, get_database_from_uris, ["mem://", "mem://"])

    def test_multi_db(self):
        from django_zodb.database import get_database_from_uris
        db = get_database_from_uris(["mem://", "mem://?database_name=catalog"])
        self.assertEqual("unnamed", db.database_name)
        self.assertTrue("unnamed" in db.databases)
        self.assertTrue("catalog" in db.databases)
        self.assertEqual("MappingStorage", db.getName())

    def test_zconfig_database_1(self):
        from django_zodb.database import get_database_from_uris
        db = get_database_from_uris(["zconfig://" + get_tool_uri_path('zconfig.zcml') + "#temp2"])
        self.assertFalse("temp1" in db.databases)
        self.assertTrue("temp2" in db.databases)

    def test_zconfig_database_2(self):
        from django_zodb.database import get_database_from_uris
        db = get_database_from_uris(["zconfig://" + get_tool_uri_path('zconfig.zcml')])
        self.assertTrue("temp1" in db.databases)
        self.assertFalse("temp2" in db.databases)

    def test_fail_zconfig_unknown_database(self):
        from django_zodb.database import get_database_from_uris
        uri = "zconfig://" + get_tool_uri_path('zconfig.zcml') + "#unknown"
        self.assertRaises(ValueError, get_database_from_uris, [uri])

    def test_fail_not_configured_db_1(self):

        from django_zodb.database import get_database_by_name
        self.assertRaises(ValueError, get_database_by_name, 'db1')

        with self.settings(ZODB={}):
            self.assertRaises(ValueError, get_database_by_name, 'db1')

        with self.settings(ZODB={'db1': ['mem://']}):
            self.assertRaises(ValueError, get_database_by_name, 'db2')

    def test_open_file_database(self):
        with self.settings(ZODB={'db1': ['file://%stest123.db' % TEMP_DIR_URI]}):
            from django_zodb.database import get_database_by_name
            db = get_database_by_name('db1')
            self.assertEqual("unnamed", db.database_name)
            self.assertTrue("unnamed" in db.databases)
            self.assertTrue(db.getName().endswith("test123.db"))
