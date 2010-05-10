# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

from django.test import TestCase

class FakeContainer(dict):
    __name__ = None
    def set(self, key, value):
        self[key] = value
        value.__name__ = key
        value.__parent__ = self

class FakeModel(object):
    pass

ROOT = FakeContainer()
ROOT.set('foo', FakeContainer())
ROOT['foo'].set('bar', FakeContainer())
ROOT['foo'].set('qux', FakeContainer())
ROOT['foo']['qux'].set('quxx', FakeModel())
ROOT.set(u'úñíçõdê', FakeContainer())

# class ModelsTests(TestCase):
#     def eq(self, a, b, *args, **kwargs):
#         return self.assertEquals(a, b, *args, **kwargs)
#
#     def raise_(self, err, func, *args, **kwargs):
#         return self.assertRaises(err, func, *args, **kwargs)
#
#     def test_model_path(self):
#         from django_zodb import models
#
#         self.assertEquals(models.model_path(ROOT['foo']['qux']['quxx']), "/foo/qux/quxx")
#         self.assertEquals(models.model_path(ROOT), u"/")
#         self.assertEquals(models.model_path(ROOT[u'úñíçõdê']), u"/%C3%BA%C3%B1%C3%AD%C3%A7%C3%B5d%C3%AA")
