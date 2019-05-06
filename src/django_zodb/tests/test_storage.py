# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import os

from django.test import TestCase

from testutils.tools import remove_db_files, TEMP_DIR_URI, TEMP_DIR

from django_zodb.storage import factories

class StorageTests(TestCase):
    def setUp(self):
        remove_db_files()

    def tearDown(self):
        remove_db_files()

    def test_fail_unknown_scheme(self):
        from django_zodb.storage import get_storage_from_uri
        self.assertRaises(ValueError, get_storage_from_uri, 'unknown:')

    def test_disabled_reason(self):
        factories.disable("disabled", "reason")
        self.assertEqual(factories.disable_reason("disabled"), "reason")
        del factories.disabled['disabled'] # cleanup

    def test_mem_storage(self):
        from django_zodb.storage import get_storage_from_uri
        storage = get_storage_from_uri("mem://")
        self.assertEqual(storage.__class__.__name__, "MappingStorage")
        storage.close()

    def test_mem_storage_demo(self):
        from django_zodb.storage import get_storage_from_uri
        storage = get_storage_from_uri("mem://?demostorage")
        self.assertEqual(storage.__class__.__name__, "DemoStorage")
        storage.close()

    def test_file_storage(self):
        from django_zodb.storage import get_storage_from_uri
        storage = get_storage_from_uri("file://%stest34.db?database_name=file" % TEMP_DIR_URI)
        self.assertEqual(storage.__class__.__name__, "FileStorage")
        self.assertRaises(TypeError, lambda: storage.fshelper.temp_dir)
        storage.close()
        remove_db_files()

    def test_fail_file_storage_with_invalid_arguments_1(self):
        from django_zodb.storage import get_storage_from_uri
        self.assertRaises(ValueError, get_storage_from_uri, "file://%stest76.db?create=true&read_only=true" % TEMP_DIR_URI)

    def test_fail_file_storage_with_invalid_arguments_2(self):
        from django_zodb.storage import get_storage_from_uri
        self.assertRaises(TypeError, get_storage_from_uri, "file://?error=1")

    def test_fail_file_storage_with_invalid_arguments_3(self):
        from django_zodb.storage import get_storage_from_uri
        self.assertRaises(ValueError, get_storage_from_uri, "file:///foo/bar?path=error")

    def test_fail_file_storage_with_invalid_arguments_4(self):
        from django_zodb.storage import get_storage_from_uri
        self.assertRaises(TypeError, get_storage_from_uri, "file://%stest355.db?quota=not_int" % TEMP_DIR_URI)

    def test_file_storage_with_blob(self):
        from django_zodb.storage import get_storage_from_uri
        uri = "file://%stest645.db?blob_dir=%sblobdir" % (TEMP_DIR_URI, TEMP_DIR_URI)
        storage = get_storage_from_uri(uri)
        self.assertEqual(storage.__class__.__name__, "FileStorage")
        self.assertEqual(storage.getName(), "%stest356.db" % TEMP_DIR)
        self.assertEqual(storage.fshelper.temp_dir, "%sblobdir/tmp" % TEMP_DIR)
        storage.close()

        self.assertTrue(os.path.isdir('%sblobdir' % TEMP_DIR))
        self.assertTrue(os.path.isdir('%sblobdir/tmp' % TEMP_DIR))
        self.assertTrue(os.path.exists('%sblobdir/.layout' % TEMP_DIR_URI))
        self.assertEqual(open('%sblobdir/.layout' % TEMP_DIR_URI).read().strip(), 'bushy')

    def _fake_factories(self, uri):
        from django_zodb.config import get_configuration_from_uri
        from django_zodb.storage import factories

        config = get_configuration_from_uri(uri)
        scheme = config.pop("scheme")
        factory_class = factories.get(scheme)

        ret = {}
        def _fake_adapter(self, **kwargs):
            del kwargs['options']
            ret['adapter'] = kwargs
            return "FakeAdapter"
        def _fake_storage(self, **kwargs):
            kwargs.pop('adapter', None)
            ret['storage'] = kwargs
            return "FakeStorage"
        factory_class._adapter = _fake_adapter
        factory_class._storage = _fake_storage

        factory_class(config).get_storage()

        return ret

    def test_zeo_storage_with_host(self):
        uri = "zeo://localhost/ignored_path?blob_dir=%sblobdir&wait=true&wait_timeout=1" % TEMP_DIR_URI
        self.assertEqual(self._fake_factories(uri), {
            'storage': {
                'addr': ('localhost', 8090),
                'blob_dir': '%sblobdir' % TEMP_DIR_URI,
                'wait_timeout': 1,
                'wait': True,
            },
        })

    def test_zeo_storage_with_sock(self):
        uri = "zeo://%szeo.zdsock?blob_dir=%sblobdir&wait=true&wait_timeout=1" % (TEMP_DIR_URI, TEMP_DIR_URI)
        self.assertEqual(self._fake_factories(uri), {
            'storage': {
                'addr': "%szeo.zdsock" % TEMP_DIR_URI,
                'blob_dir': "%sblobdir" % TEMP_DIR_URI,
                'wait_timeout': 1,
                'wait': True,
            },
        })

    def test_fail_zeo_storage_without_host_and_sock(self):
        self.assertRaises(ValueError, self._fake_factories, "zeo://")

    def _enabled(self, scheme):
        enabled = scheme in factories.available()
        if not enabled:
            msg = "%s test disabled. Reason: %s" % (scheme, factories.disable_reason(scheme))
            import warnings
            warnings.warn(msg, UserWarning)
        return enabled

    def test_mysql_storage(self):
        if not self._enabled('mysql'):
            return

        uri = "mysql://"\
              "test_user:test_pass@"\
              "test_host"\
              "?compress=1&create=false&read_only=true&blob_dir=/tmp"\
              "&cache_servers=cache1,cache2,cache3"\
              "#test_dbname"

        self.assertEqual(self._fake_factories(uri), {
            'adapter': {
                'user':     'test_user',
                'passwd':   'test_pass',
                'host':     'test_host',
                'db':       'test_dbname',
                'compress': True,
            },
            'storage': {
                'read_only': True,
                'blob_dir':  '/tmp',
                'create':    False,
                'cache_servers': ('cache1', 'cache2', 'cache3'),
            },
        })

    def test_postgresql_storage(self):
        if not self._enabled('postgresql'):
            return

        uri = "postgresql://"\
              "test_user:test_pass@"\
              "test_host"\
              "?create=false"\
              "#test_dbname"

        self.assertEqual(self._fake_factories(uri), {
            'adapter': {
                'dsn': 'dbname=test_dbname host=test_host password=test_pass user=test_user',
            },
            'storage': {
                'create':    False,
            },
        })

    # def test_oracle_storage(self):
    #     if not self._enabled('oracle'):
    #         return
    #
    #     uri = "oracle://"\
    #           "test_user:test_pass@"\
    #           "?dsn=user1/pass1@dsn&twophase=true"
    #
    #     self.assertEquals(self._fake_factories(uri), {
    #         'adapter': {
    #             'user': 'test_user',
    #             'password': 'test_pass',
    #             'dsn': 'user1/pass1@dsn',
    #             'twophase': True,
    #         },
    #         'storage': {
    #             'create': True,
    #         },
    #     })
