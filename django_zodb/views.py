# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

from django.http import Http404

# TODO: To implement...

class TraversalError(Exception):
    pass

class ContextNotFound(TraversalError):
    pass

class ViewMethodNotFound(TraversalError):
    pass


class Context(object):
    def __init__(self, model, method, subpath):
        self.model = model
        self.method = method
        self.subpath = subpath


class Viewer(object):
    def __init__(self, context, method_name, subpath):
        self.context = context
        if method_name:
            self.method_name = method_name
        else:
            self.method_name = "__index__"

    def __call__(self, request):
        try:
            view_method = getattr(self, self.method_name)
        except AttributeError:
            raise ViewMethodNotFound("View '%s' not implemented." % \
                    (context.method,))

        return view_method(request, self.context, self.subpath)

def traverse(root, path):
    pass

def traverse_or_404(root, path, error_message="Not found."):
    try:
        return traverse(root, path)
    except ContextNotFound:
        raise Http404(error_message)

def get_response(request, root, path, error_message="Not found.", exception=Http404):
    try:
        viewer = traverse(root, path)
        return viewer(request)
    except TraversalError, ex:
        raise error(ex)
