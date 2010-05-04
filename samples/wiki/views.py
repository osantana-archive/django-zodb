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


class PageViewer(views.Viewer):
    def __index__(self, request, context):
        page = {
            'title': context.title,
            'content': context.get_html(),
        }
        return render_to_response("page.html", page)

    def edit(self, request, context):
        page = {
            'title': context.title,
            'content': context.get_html(),
        }
        return render_to_response("edit.html", page)


# TODO
"""
    class Meta:
        model = Page
page_viewer = PageViewer(Page)

Traverse returns ->
  * context (model)
  * viewer  (viewer)
  * method  (method name or '' for index)
  * subpath (remaining path)

def page(request, path):
    root = Wiki()
    context, viewer = views.traverse_or_404(root, path)
    return viewer(request, context)

"""
