# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

import os

from django.test import TestCase

from testutils.tools import remove_db_files, start_zeo

class StorageTests(TestCase):
    def test_fail_unknown_scheme(self):
        from django_zodb.storage import get_storage_from_uri
        self.assertRaises(ValueError, get_storage_from_uri, 'unknown:')

    def test_mem_storage(self):
        from django_zodb.storage import get_storage_from_uri
        storage = get_storage_from_uri("mem://")
        self.assertEquals(storage.__class__.__name__, "MappingStorage")
        storage.close()

    def test_mem_storage_demo(self):
        from django_zodb.storage import get_storage_from_uri
        storage = get_storage_from_uri("mem://?demostorage")
        self.assertEquals(storage.__class__.__name__, "DemoStorage")
        storage.close()

    def test_file_storage(self):
        from django_zodb.storage import get_storage_from_uri
        storage = get_storage_from_uri("file:///tmp/test.db")
        self.assertEquals(storage.__class__.__name__, "FileStorage")
        self.assertRaises(TypeError, lambda: storage.fshelper.temp_dir)
        storage.close()
        remove_db_files()

    def test_fail_file_storage_with_invalid_arguments_1(self):
        from django_zodb.storage import get_storage_from_uri
        self.assertRaises(ValueError, get_storage_from_uri, "file:///tmp/test.db?create=true&read_only=true")

    def test_fail_file_storage_with_invalid_arguments_2(self):
        from django_zodb.storage import get_storage_from_uri
        self.assertRaises(TypeError, get_storage_from_uri, "file://?error=1")

    def test_fail_file_storage_with_invalid_arguments_3(self):
        from django_zodb.storage import get_storage_from_uri
        self.assertRaises(ValueError, get_storage_from_uri, "file:///foo/bar?path=error")

    def test_file_storage_with_blob(self):
        from django_zodb.storage import get_storage_from_uri
        storage = get_storage_from_uri("file:///tmp/test.db?blobstorage_dir=/tmp/blobdir&blobstorage_layout=bushy")
        self.assertEquals(storage.__class__.__name__, "FileStorage")
        self.assertEquals(storage.getName(), "/tmp/test.db")
        self.assertEquals(storage.fshelper.temp_dir, "/tmp/blobdir/tmp")
        storage.close()

        self.assertTrue(os.path.isdir('/tmp/blobdir'))
        self.assertTrue(os.path.isdir('/tmp/blobdir/tmp'))
        self.assertTrue(os.path.exists('/tmp/blobdir/.layout'))
        self.assertEqual(open('/tmp/blobdir/.layout').read().strip(), 'bushy')
        remove_db_files()

    def test_zeo_storage_with_host(self):
        from django_zodb.storage import get_storage_from_uri
        zeo = start_zeo()
        storage = get_storage_from_uri("zeo://localhost/foobar?blob_dir=/tmp/blobdir&wait=true&wait_timeout=1")
        self.assertEquals(storage.__class__.__name__, "ClientStorage")
        zeo.terminate()
        remove_db_files()

    def test_zeo_storage_with_sock(self):
        from django_zodb.storage import get_storage_from_uri
        zeo = start_zeo('sock')
        storage = get_storage_from_uri("zeo:///tmp/zeo.zdsock?blob_dir=/tmp/blobdir&wait=true&wait_timeout=1")
        self.assertEquals(storage.__class__.__name__, "ClientStorage")
        storage.close()
        zeo.terminate()
        remove_db_files()
