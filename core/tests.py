# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from django.test import TestCase

class ResolversTests(TestCase):
    def test_get_mem_uri(self):
        from django_zodb.resolvers import get_db_from_uri
        db = get_db_from_uri("mem:")
        self.assertEquals(db.__class__.__name__, "MappingStorage")

    def test_fail_unknown_scheme(self):
        from django_zodb.resolvers import get_db_from_uri
        self.assertRaises(ValueError, get_db_from_uri, 'unknown:')
