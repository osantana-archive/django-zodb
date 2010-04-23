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

    def _remove_files(self):
        filelist = (
            '/tmp/test.db',
            '/tmp/test.db.lock',
            '/tmp/test.db.index',
            '/tmp/test.db.tmp',
            '/tmp/blobdir',
        )
        for filename in filelist:
            if os.path.isdir(filename):
                shutil.rmtree(filename)
            if os.path.exists(filename):
                os.remove(filename)

    def test_file_storage(self):
        from django_zodb.storage import get_storage_from_uri
        storage = get_storage_from_uri("file:///tmp/test.db")
        self.assertEquals(storage.__class__.__name__, "FileStorage")
        storage.close()
        self._remove_files()

    def test_fail_file_storage_with_invalid_arguments_1(self):
        from django_zodb.storage import get_storage_from_uri
        self.assertRaises(ValueError, get_storage_from_uri, "file:///tmp/test.db?create=true&read_only=true")

    def test_fail_file_storage_with_invalid_arguments_2(self):
        from django_zodb.storage import get_storage_from_uri
        self.assertRaises(TypeError, get_storage_from_uri, "file://?error")

    def test_file_storage_with_blob(self):
        from django_zodb.storage import get_storage_from_uri
        storage = get_storage_from_uri("file:///tmp/test.db?blobstorage_dir=/tmp/blobdir&blobstorage_layout=bushy")
        self.assertEquals(storage.__class__.__name__, "FileStorage")
        storage.close()

        self.assertTrue(os.path.isdir('/tmp/blobdir'))
        self.assertTrue(os.path.isdir('/tmp/blobdir/tmp'))
        self.assertTrue(os.path.exists('/tmp/blobdir/.layout'))
        self.assertEqual(open('/tmp/blobdir/.layout').read().strip(), 'bushy')

        self._remove_files()
