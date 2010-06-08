# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

from django.test import TestCase

class URIParseTests(TestCase):
    def _t(self, uri, **kwargs):
        from django_zodb.utils import parse_uri
        self.assertEquals(parse_uri(uri), kwargs)

    def test_uris(self):
        self._t("sc", scheme='sc')
        self._t("sc:", scheme='sc')
        self._t("sc://", scheme='sc')
        self._t("sc:host", scheme='sc', host='host')
        self._t("sc://host", scheme='sc', host='host')
        self._t("sc://user@", scheme='sc', user='user')
        self._t("sc:user@", scheme='sc', user='user')
        self._t("sc://user@host", scheme='sc', user='user', host='host')
        self._t("sc://user:pass@host", scheme='sc', user='user', password='pass',
                    host='host')
        self._t("sc:user:pass@host", scheme='sc', user='user', password='pass',
                    host='host')
        self._t("sc://user:pass@host:1234", scheme='sc', user='user', password='pass',
                    host='host', port=1234)
        self._t("sc://user:pass@host:1234/", scheme='sc', user='user', password='pass',
                    host='host', port=1234, path='/')
        self._t("sc://user:pass@host:1234/path", scheme='sc', user='user', password='pass',
                    host='host', port=1234, path='/path')
        self._t("sc://user:pass@host/path", scheme='sc', user='user', password='pass',
                    host='host', path='/path')
        self._t("sc://user:pass@host///path", scheme='sc', user='user', password='pass',
                    host='host', path='///path')
        self._t("sc://user:pass@host/path/", scheme='sc', user='user', password='pass',
                    host='host', path='/path/')

        self._t("cache://user:pass@host/path/", scheme='cache', user='user', password='pass',
                    host='host', path='/path/')
        self._t("cache://user:pass@host/path/", scheme='cache', user='user', password='pass',
                    host='host', path='/path/')

        self._t("file:///foo", scheme='file', path="/foo")
        self._t("file://user@/foo", user='user', scheme='file', path="/foo")
        self._t("file://foo/bar", scheme='file', host="foo", path="/bar")
        self._t("file:///foo@bar&baz&qux.quxx/bla:ble", scheme='file', path="/foo@bar&baz&qux.quxx/bla:ble")
        self._t("file:///foo@bar&baz&qux.quxx?bla=ble&bli", scheme='file', path="/foo@bar&baz&qux.quxx",
                    query={'bla': ['ble'], 'bli': ['']})
        self._t("file:///foo#bar/baz#frag", scheme="file", path="/foo#bar/baz", frag="frag")

        self._t("sc?foo", scheme='sc', query={"foo": ['']})
        self._t("sc:?foo", scheme='sc', query={"foo": ['']})
        self._t("sc:?foo=bar", scheme='sc', query={"foo": ['bar']})
        self._t("sc:?foo=bar&bar=baz", scheme='sc', query={"foo": ['bar'], "bar": ['baz']})
        self._t("sc:?foo=bar&foo=bar", scheme='sc', query={"foo": ['bar', 'bar']})
        self._t("sc://u:p@h:1/x?a=b",
                    scheme='sc',
                    user='u',
                    password='p',
                    host='h',
                    port=1,
                    path='/x',
                    query={'a': ['b']}
                    )
        self._t("sc://u@h:1/x?a=b",
                    scheme='sc',
                    user='u',
                    host='h',
                    port=1,
                    path='/x',
                    query={'a': ['b']}
                    )
        self._t("sc://u@:1/x?a=b",
                    scheme='sc',
                    user='u',
                    port=1,
                    path='/x',
                    query={'a': ['b']}
                    )
        self._t("sc://h:1/x?a=b", scheme='sc', host='h', port=1, path='/x', query={'a': ['b']})
        self._t("sc://:1/x?a=b", scheme='sc', port=1, path='/x', query={'a': ['b']})
        self._t("sc:///x?a=b", scheme='sc', path='/x', query={'a': ['b']})
        self._t("sc://?a=b", scheme='sc', query={'a': ['b']})
        self._t("mysql://test_user:test_pass@test_host?compress=1#test_dbname",
            scheme="mysql",
            user="test_user",
            password="test_pass",
            host="test_host",
            query={'compress': ['1']},
            frag="test_dbname",
        )

    def test_camel_case_to_underline(self):
        from django_zodb.utils import camel_case_to_underline as cc2u

        self.assertEquals(cc2u("Foo"), "foo")
        self.assertEquals(cc2u("foo"), "foo")
        self.assertEquals(cc2u("FooBar"), "foo_bar")
        self.assertEquals(cc2u("FooBarBaz"), "foo_bar_baz")
        self.assertEquals(cc2u("FooBarBazX"), "foo_bar_baz_x")
        self.assertEquals(cc2u("ISBNNumber"), "isbn_number")
        self.assertEquals(cc2u("XMod1"), "x_mod1")
        self.assertEquals(cc2u("Convert2ISBN"), "convert2_isbn")
        self.assertEquals(cc2u("Convert_2_ISBN"), "convert_2_isbn")
