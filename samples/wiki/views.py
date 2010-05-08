# -*- coding: utf-8 -*-
#
# django-zodb sample - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

from django.shortcuts import render_to_response

from django_zodb import views

from samples.wiki.models import Wiki, Page

class WikiView(views.View):
    def __index__(self, request, context):
        return render_to_response("page.html", {'context': context})

views.registry.register(WikiView, Wiki)


class PageView(views.View):
    def __index__(self, request, context):
        return render_to_response("page.html", {'context': context})

views.registry.register(Page, PageView)

def page(request, path):
    return views.get_response(request, root=Wiki(), path=path)
