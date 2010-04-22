# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

import os

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

    def test_file_storage(self):
        from django_zodb.storage import get_storage_from_uri
        storage = get_storage_from_uri("file:///tmp/test.db")
        self.assertEquals(storage.__class__.__name__, "FileStorage")
        storage.close()
        os.system("rm -f /tmp/test.db*")

    def test_fail_file_storage_with_invalid_arguments(self):
        from django_zodb.storage import get_storage_from_uri
        self.assertRaises(ValueError, get_storage_from_uri, "file:///tmp/test.db?create=true&read_only=true")
