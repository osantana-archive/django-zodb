# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

from django.test import TestCase

from django_zodb import models

class FakeContainer(models.Container):
    def set(self, key, value):
        self[key] = value
        value.__name__ = key
        value.__parent__ = self

class FakeModel(models.Model):
    pass

ROOT = FakeContainer()
ROOT.set('foo', FakeContainer())
ROOT['foo']['bar'] = FakeContainer()
ROOT['foo']['qux'] = FakeContainer()
ROOT['foo']['qux']['quxx'] = FakeModel()
ROOT.set(u'úñíçõdê', FakeContainer())

from django_zodb import models

class MyRoot(models.Root):
    def __init__(self, attr):
        self.attr = attr

class ModelsTests(TestCase):
    def eq(self, a, b, *args, **kwargs):
        return self.assertEquals(a, b, *args, **kwargs)

    def raise_(self, err, func, *args, **kwargs):
        return self.assertRaises(err, func, *args, **kwargs)

    def _set_zodb(self, dic):
        import django.conf
        django.conf.settings._wrapped.ZODB = dic

    def test_model_path(self):
        self.assertEquals(models.model_path(ROOT['foo']['qux']['quxx']), "/foo/qux/quxx")
        self.assertEquals(models.model_path(ROOT), u"/")
        self.assertEquals(models.model_path(ROOT[u'úñíçõdê']), u"/%C3%BA%C3%B1%C3%AD%C3%A7%C3%B5d%C3%AA")
        self.assertEquals(models.model_path(ROOT['foo'], prepend="x"), u"x/foo")

    def test_root(self):
        self._set_zodb({"default": ["mem://"]})

        root1 = models.get_root(MyRoot, attr="1")
        root2 = models.get_root(MyRoot, attr="2")

        self.assertEquals(id(root1), id(root2))
        self.assertEquals(root1.attr, root2.attr)
        self.assertEquals(root1.__name__, None)
        self.assertEquals(root1.__parent__, None)

    def test_remove_model(self):
        container = FakeContainer()

        ROOT['new'] = container
        self.assertEquals(ROOT['new'], container)
        self.assertEquals(container.__parent__, ROOT)

        del ROOT['new']
        self.assertEquals(container.__parent__, None)

    def test_invalid_root(self):
        self._set_zodb({"default": ["mem://"]})

        class InvalidRoot(object):
            pass

        self.assertRaises(TypeError, models.get_root, InvalidRoot)
