# -*- coding: utf-8 -*-
#
# django-zodb sample - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

import re

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

import transaction
from django_zodb import views
from django_zodb import models

from samples.wiki.models import Wiki, Page
from samples.wiki.forms import PageEditForm

wikiwords = re.compile(ur"\b([A-Z]\w+([A-Z]+\w+)+)")


class WikiView(views.View):
    def __index__(self, request, context, root, subpath, traversed):
        return HttpResponseRedirect("FrontPage")

    def add(self, request, context, root, subpath, traversed):
        try:
            name = subpath[0]
        except IndexError:
            return HttpResponseRedirect("/wiki/")

        if request.method == "POST":
            form = PageEditForm(request.POST)
            if form.is_valid():
                page = Page(form.cleaned_data['content'])
                root[name] = page
                return HttpResponseRedirect(page.get_absolute_url())
        else:
            form = PageEditForm()

        page_data = {
            'name': name,
            'cancel_link': "javascript:history.go(-1)",
            'form': form,
        }
        return render_to_response("edit.html", page_data)
views.registry.register(model=Wiki, view=WikiView())


class PageView(views.View):
    def __index__(self, request, context, root, subpath, traversed):
        content = context.html()

        def check(match):
            word = match.group(1)
            if word in root:
                page = root[word]
                view_url = page.get_absolute_url()
                return '<a href="%s">%s</a>' % (view_url, word)
            else:
                add_url = models.model_path(root, "/wiki", "add", word)
                return '<a href="%s">%s</a>' % (add_url, word)

        content = wikiwords.sub(check, content)

        page_data = {
            'context': context,
            'content': content,
            'edit_link': context.get_absolute_url() + "/edit",
            'root': root,
        }
        return render_to_response("page.html", page_data)

    def edit(self, request, context, root, subpath, traversed):
        context_path = models.model_path(context, prepend="/wiki")

        if request.method == "POST":
            form = PageEditForm(request.POST)
            if form.is_valid():
                context.content = form.cleaned_data['content']
                return HttpResponseRedirect(context_path)
        else:
            form = PageEditForm(initial={'content': context.content})

        page_data = {
            'name': context.name,
            'context': context,
            'cancel_link': context_path,
            'form': form,
        }
        return render_to_response("edit.html", page_data)
views.registry.register(model=Page, view=PageView())


def create_frontpage(root):
    frontpage = Page()
    root["FrontPage"] = frontpage
    return root


def page(request, path):
    root = models.get_root(Wiki, setup=create_frontpage)
    return views.get_response_or_404(request, root=root, path=path)
