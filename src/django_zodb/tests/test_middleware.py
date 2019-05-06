# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from django.test import TestCase


class MiddlewareTests(TestCase):
    def setUp(self):
        import django.conf
        if hasattr(django.conf.settings, 'ZODB'):
            del django.conf.settings._wrapped.ZODB
        django.conf.settings._wrapped.ZODB = {'default': ['mem://']}

    def test_commit_enabled(self):
        import transaction
        from django_zodb.models import get_root
        from samples.wiki.models import Wiki

        response = self.client.post("/wiki/FrontPage/edit", { 'content': 'value_commited' }, follow=True)
        assert response.status_code == 200

        transaction.abort() # force removal of uncommited changes

        self.assertEqual('value_commited', get_root(Wiki)['FrontPage'].content)

    def test_commit_disabled(self):
        import transaction
        from django_zodb.models import get_root
        from samples.wiki.models import Wiki
        from django_zodb.middleware import TransactionMiddleware

        TransactionMiddleware.disable()
        response = self.client.post("/wiki/FrontPage/edit", { 'content': 'value_uncommited' }, follow=True)
        transaction.abort() # force removal of uncommited changes
        TransactionMiddleware.enable()

        self.assertNotEqual('value_uncommited', get_root(Wiki)['FrontPage'].content)


