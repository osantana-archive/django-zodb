# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

from django.test import TestCase

from .test_models import ROOT, FakeContainer

class ViewsTests(TestCase):
    def tearDown(self):
        from django_zodb import views
        views.registry.clean()

    def eq(self, a, b, *args, **kwargs):
        return self.assertEqual(a, b, *args, **kwargs)

    def raise_(self, err, func, *args, **kwargs):
        return self.assertRaises(err, func, *args, **kwargs)

    def test_split_path(self):
        from django_zodb.views import split_path as sp
        self.eq(repr(sp("foo/bar/baz")), "('foo', 'bar', 'baz')")
        self.eq(repr(sp("/foo/bar/baz")), "('foo', 'bar', 'baz')")
        self.eq(repr(sp("foo/bar/baz/")), "('foo', 'bar', 'baz')")
        self.eq(repr(sp("/foo/bar/baz/")), "('foo', 'bar', 'baz')")
        self.eq(repr(sp("/foo/b%20r/baz/")), "('foo', 'b r', 'baz')")
        self.eq(repr(sp("/foo/b%20r///baz/")), "('foo', 'b r', 'baz')")
        self.eq(repr(sp("/foo/b%20r/./baz/")), "('foo', 'b r', 'baz')")
        self.eq(repr(sp("/foo/b%20r/./baz/.")), "('foo', 'b r', 'baz')")
        self.eq(repr(sp("/foo/b%20r/../baz/")), "('foo', 'baz')")
        self.eq(repr(sp("/foo/b%20r/../baz/..")), "('foo',)")
        self.eq(repr(sp("/foo/bar/b%C3%BDz/")), "('foo', 'bar', 'býz')")
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

        _eq(tr(ROOT, ""), root=ROOT, ctx=ROOT, mn="", sp=(), tr=())
        _eq(tr(ROOT, "foo"), root=ROOT, ctx=ROOT['foo'], mn="", sp=(), tr=('foo',))
        _eq(tr(ROOT, "/notfound/"), root=ROOT, ctx=ROOT, mn="notfound", sp=(), tr=('notfound',))
        _eq(tr(ROOT, "./foo"), root=ROOT, ctx=ROOT['foo'], mn="", sp=(), tr=('foo',))
        _eq(tr(ROOT, "/foo"), root=ROOT, ctx=ROOT['foo'], mn="", sp=(), tr=('foo',))
        _eq(tr(ROOT, "/foo/bar"), root=ROOT, ctx=ROOT['foo']['bar'], mn="", sp=(), tr=('foo', 'bar'))
        _eq(tr(ROOT, "/foo/bar/baz"), root=ROOT, ctx=ROOT['foo']['bar'], mn="baz", sp=(), tr=('foo', 'bar', 'baz'))
        _eq(tr(ROOT, "/foo/bar/baz/subpath/1/2"), root=ROOT, ctx=ROOT['foo']['bar'], mn="baz", sp=('subpath', '1', '2'), tr=('foo', 'bar', 'baz'))
        _eq(tr(ROOT, "/@@foo/bar/baz/"), root=ROOT, ctx=ROOT, mn="foo", sp=('bar', 'baz'), tr=('@@foo',))
        _eq(tr(ROOT, "/foo/@@bar/baz/"), root=ROOT, ctx=ROOT['foo'], mn="bar", sp=('baz',), tr=('foo', '@@bar'))
        _eq(tr(ROOT, "/foo/bar/@@baz/subpath/1/2"), root=ROOT, ctx=ROOT['foo']['bar'], mn="baz", sp=('subpath', '1', '2'), tr=('foo', 'bar', '@@baz'))
        _eq(tr(ROOT, "/foo/bar/baz/@@subpath/1/2"), root=ROOT, ctx=ROOT['foo']['bar'], mn="baz", sp=('@@subpath', '1', '2'), tr=('foo', 'bar', 'baz'))
        _eq(tr(ROOT, "/foo/qux/"), root=ROOT, ctx=ROOT['foo']['qux'], mn="", sp=(), tr=('foo', 'qux'))
        _eq(tr(ROOT, "/foo/qux/quxx"), root=ROOT, ctx=ROOT['foo']['qux']['quxx'], mn="", sp=(), tr=('foo', 'qux', 'quxx'))
        _eq(tr(ROOT, "/foo/qux/quxx/quxxx"), root=ROOT, ctx=ROOT['foo']['qux']['quxx'], mn="quxxx", sp=(), tr=('foo', 'qux', 'quxx', 'quxxx'))
        _eq(tr(ROOT, "/foo/qux/quxx/quxxx/sub"), root=ROOT, ctx=ROOT['foo']['qux']['quxx'], mn="quxxx", sp=('sub',), tr=('foo', 'qux', 'quxx', 'quxxx'))
        _eq(tr(ROOT['foo'], "/foo"), root=ROOT['foo'], ctx=ROOT['foo'], mn="foo", sp=(), tr=('foo',))

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
        self.eq(response, "baz response: 'request' subpath: 'subpath/1'")

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
        self.assertEqual(t.root, "root")
        self.assertEqual(t.method_name, "")

        t['bla'] = 'ble'
        self.assertEqual(t.bla, 'ble')
        self.assertEqual(t['bla'], 'ble')

        t.foo = "bar"
        self.assertEqual(t.foo, 'bar')
        self.assertEqual(t['foo'], 'bar')

        self.assertEqual(sorted(t.items()), [
            ('bla', 'ble'),
            ('context', None),
            ('foo', 'bar'),
            ('method_name', ''),
            ('root', 'root'),
            ('subpath', ()),
            ('traversed', ())
        ])
