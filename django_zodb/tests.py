# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from django.test import TestCase
from django_zodb import db

class SimpleTest(TestCase):
    cleaned = False
    def setUp(self):
        if not self.cleaned:
            db.zap(confirm="Yes, I know what I'm doing.")
            self.cleaned = True
        self.root = db.root

    def tearDown(self):
        self.root = None

    def test_empty_database(self):
        self.assertEquals(len(self.root), 0)

    def test_basic_connection(self):
        self.assertRaises(KeyError, lambda: self.root['key1'])

    def test_basic_rollback(self):
        self.root['key1'] = 1
        db.rollback()
        self.assertRaises(KeyError, lambda: self.root['key1'])

    def test_basic_commit(self):
        self.root['key2'] = 1
        db.enable_commit()
        db.commit()
        self.cleaned = False
        db.close()

        new_root = db.root
        self.assertEquals(new_root['key2'], 1)

    def test_disabled_commit(self):
        db.disable_commit()
        self.root['key2'] = 1
        db.commit()
        db.close()

        new_root = db.root
        self.assertRaises(KeyError, lambda: new_root['key2'])
