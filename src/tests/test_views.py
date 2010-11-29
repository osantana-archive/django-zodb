# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

from django.test import TestCase

from test_models import ROOT, FakeContainer

class ViewsTests(TestCase):
    def tearDown(self):
        from django_zodb import views
        views.registry.clean()

    def eq(self, a, b, *args, **kwargs):
        return self.assertEquals(a, b, *args, **kwargs)

    def raise_(self, err, func, *args, **kwargs):
        return self.assertRaises(err, func, *args, **kwargs)

    def test_split_path(self):
        from django_zodb.views import split_path as sp
        self.eq(repr(sp("foo/bar/baz")), "(u'foo', u'bar', u'baz')")
        self.eq(repr(sp("/foo/bar/baz")), "(u'foo', u'bar', u'baz')")
        self.eq(repr(sp("foo/bar/baz/")), "(u'foo', u'bar', u'baz')")
        self.eq(repr(sp("/foo/bar/baz/")), "(u'foo', u'bar', u'baz')")
        self.eq(repr(sp("/foo/b%20r/baz/")), "(u'foo', u'b r', u'baz')")
        self.eq(repr(sp("/foo/b%20r///baz/")), "(u'foo', u'b r', u'baz')")
        self.eq(repr(sp("/foo/b%20r/./baz/")), "(u'foo', u'b r', u'baz')")
        self.eq(repr(sp("/foo/b%20r/./baz/.")), "(u'foo', u'b r', u'baz')")
        self.eq(repr(sp("/foo/b%20r/../baz/")), "(u'foo', u'baz')")
        self.eq(repr(sp("/foo/b%20r/../baz/..")), "(u'foo',)")
        self.eq(repr(sp("/foo/bar/b%C3%BDz/")), "(u'foo', u'bar', u'b\\xfdz')")
        self.raise_(TypeError, sp, "/foo/bar/b%C3%00z/")

    def test_traverse_result(self):
        from django_zodb.views import traverse as tr

        def _eq(res, **kw):
            self.eq(res.root, kw['root'], "root: %r != %r" % (res.root, kw['root']))
            self.eq(res.context, kw['ctx'], "ctx: %r != %r" % (res.context, kw['ctx']))
            self.eq(res.method_name, kw['mn'], "mn: %r != %r" % (res.method_name, kw['mn']))
            self.eq(type(res.method_name), type(kw['mn']))
            self.eq(res.subpath, kw['sp'], "sp: %r != %r" % (res.subpath, kw['sp']))
            self.eq(type(res.subpath), tuple)
            self.eq(res.traversed, kw['tr'], "tr: %r != %r" % (res.traversed, kw['tr']))
            self.eq(type(res.traversed), tuple)

        _eq(tr(ROOT, ""), root=ROOT, ctx=ROOT, mn=u"", sp=(), tr=())
        _eq(tr(ROOT, "foo"), root=ROOT, ctx=ROOT['foo'], mn=u"", sp=(), tr=(u'foo',))
        _eq(tr(ROOT, "/notfound/"), root=ROOT, ctx=ROOT, mn=u"notfound", sp=(), tr=(u'notfound',))
        _eq(tr(ROOT, "./foo"), root=ROOT, ctx=ROOT['foo'], mn=u"", sp=(), tr=(u'foo',))
        _eq(tr(ROOT, "/foo"), root=ROOT, ctx=ROOT['foo'], mn=u"", sp=(), tr=(u'foo',))
        _eq(tr(ROOT, "/foo/bar"), root=ROOT, ctx=ROOT['foo']['bar'], mn=u"", sp=(), tr=(u'foo', u'bar'))
        _eq(tr(ROOT, "/foo/bar/baz"), root=ROOT, ctx=ROOT['foo']['bar'], mn=u"baz", sp=(), tr=(u'foo', u'bar', u'baz'))
        _eq(tr(ROOT, "/foo/bar/baz/subpath/1/2"), root=ROOT, ctx=ROOT['foo']['bar'], mn=u"baz", sp=(u'subpath', u'1', u'2'), tr=(u'foo', u'bar', u'baz'))
        _eq(tr(ROOT, "/@@foo/bar/baz/"), root=ROOT, ctx=ROOT, mn=u"foo", sp=(u'bar', u'baz'), tr=(u'@@foo',))
        _eq(tr(ROOT, "/foo/@@bar/baz/"), root=ROOT, ctx=ROOT['foo'], mn=u"bar", sp=(u'baz',), tr=(u'foo', u'@@bar'))
        _eq(tr(ROOT, "/foo/bar/@@baz/subpath/1/2"), root=ROOT, ctx=ROOT['foo']['bar'], mn=u"baz", sp=(u'subpath', u'1', u'2'), tr=(u'foo', u'bar', u'@@baz'))
        _eq(tr(ROOT, "/foo/bar/baz/@@subpath/1/2"), root=ROOT, ctx=ROOT['foo']['bar'], mn=u"baz", sp=(u'@@subpath', u'1', u'2'), tr=(u'foo', u'bar', u'baz'))
        _eq(tr(ROOT, "/foo/qux/"), root=ROOT, ctx=ROOT['foo']['qux'], mn=u"", sp=(), tr=(u'foo', u'qux'))
        _eq(tr(ROOT, "/foo/qux/quxx"), root=ROOT, ctx=ROOT['foo']['qux']['quxx'], mn=u"", sp=(), tr=(u'foo', u'qux', u'quxx'))
        _eq(tr(ROOT, "/foo/qux/quxx/quxxx"), root=ROOT, ctx=ROOT['foo']['qux']['quxx'], mn=u"quxxx", sp=(), tr=(u'foo', u'qux', u'quxx', u'quxxx'))
        _eq(tr(ROOT, "/foo/qux/quxx/quxxx/sub"), root=ROOT, ctx=ROOT['foo']['qux']['quxx'], mn=u"quxxx", sp=(u'sub',), tr=(u'foo', u'qux', u'quxx', u'quxxx'))
        _eq(tr(ROOT['foo'], "/foo"), root=ROOT['foo'], ctx=ROOT['foo'], mn=u"foo", sp=(), tr=(u'foo',))

    def test_get_response_or_404_model(self):
        from django_zodb import views

        class _ContainerView(views.View):
            def __index__(self, request, context, root, subpath, traversed):
                return "__index__ response: %r" % request
        views.registry.register(model=FakeContainer, view=_ContainerView())

        response = views.get_response_or_404("request", ROOT, "/foo/bar")
        self.eq(response, "__index__ response: 'request'")

    def test_get_response_or_404_method_1(self):
        from django_zodb import views

        class _ContainerView(views.View):
            def __index__(self, request, context, root, subpath, traversed):
                return "__index__ response: %r" % request
            def baz(self, request, context, root, subpath, traversed):
                return "baz response: %r" % request
        views.registry.register(model=FakeContainer, view=_ContainerView())

        response = views.get_response_or_404("request", ROOT, "/foo/bar/baz")
        self.eq(response, "baz response: 'request'")

    def test_get_response_or_404_method_2(self):
        from django_zodb import views

        class _ContainerView(views.View):
            def __index__(self, request, context, root, subpath, traversed):
                return "__index__ response: %r" % request
            def baz(self, request, context, root, subpath, traversed):
                return "baz response: %r subpath: %r" % (request, "/".join(subpath))
        views.registry.register(model=FakeContainer, view=_ContainerView())

        response = views.get_response_or_404("request", ROOT, "/foo/bar/baz/subpath/1")
        self.eq(response, "baz response: 'request' subpath: u'subpath/1'")

    def test_fail_get_response_or_404_view_not_found(self):
        from django_zodb import views
        from django.http import Http404

        self.raise_(Http404, views.get_response_or_404, "request", ROOT, "/foo/bar")

    def test_fail_get_response_or_404_method_not_found(self):
        from django_zodb import views
        from django.http import Http404

        class _ContainerView(views.View):
            def __index__(self, request, context, root, subpath, traversed):
                return "__index__ response: %r" % request
        views.registry.register(model=FakeContainer, view=_ContainerView())

        self.assertRaises(Http404, views.get_response_or_404, "request", ROOT, "/foo/bar/baz")

    def test_view_results(self):
        from django_zodb import views

        t = views.TraverseResult(root="root")
        self.assertEquals(t.root, "root")
        self.assertEquals(t.method_name, u"")

        t['bla'] = 'ble'
        self.assertEquals(t.bla, 'ble')
        self.assertEquals(t['bla'], 'ble')

        t.foo = "bar"
        self.assertEquals(t.foo, 'bar')
        self.assertEquals(t['foo'], 'bar')

        self.assertEquals(sorted(t.items()), [
            ('bla', 'ble'),
            ('context', None),
            ('foo', 'bar'),
            ('method_name', u''),
            ('root', 'root'),
            ('subpath', ()),
            ('traversed', ())
        ])
