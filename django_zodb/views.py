# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import urllib

from django.http import Http404


# Exceptions
class TraversalError(Exception):
    pass

class MethodNotFound(TraversalError):
    pass

class ViewNotFound(TraversalError):
    pass


class _ViewRegistry(object):
    def __init__(self):
        self.views = {}

    def clean(self):
        self.views = {}

    def register(self, model, view):
        self.views[model] = view

    def get_view_class(self, context):
        try:
            return self.views[context.__class__]
        except KeyError:
            raise ViewNotFound("No registered view for %r" % context)

registry = _ViewRegistry()



class View(object):
    def __init__(self, traverse_result):
        self.root = traverse_result.root
        self.context = traverse_result.context

        if traverse_result.method_name:
            self.method_name = traverse_result.method_name
        else:
            self.method_name = "__index__"

        self.subpath = traverse_result.subpath
        self.traversed = traverse_result.traversed

    def __call__(self, request):
        try:
            method = getattr(self, self.method_name)
        except AttributeError:
            raise MethodNotFound("View %r does not exist." % self.method_name)
        return method(request)


class TraverseResult(object):
    def __init__(self):
        self.root = None
        self.context = None
        self.method_name = ""
        self.subpath = ()
        self.traversed = ()



def split_path(path):
    path = path.strip('/')
    clean = []
    for segment in path.split('/'):
        segment = urllib.unquote(segment)
        if not segment or segment == '.':
            continue
        elif segment == '..':
            clean.pop()
        else:
            try:
                clean.append(segment.decode('utf-8'))
            except UnicodeDecodeError:
                raise TypeError('Could not decode path segment %r using the '
                                'UTF-8 decoding scheme' % segment)
    return tuple(clean)

def traverse_result(root, path):
    result = TraverseResult()
    path = split_path(path)

    context = root
    i = 0
    for i, segment in enumerate(path):
        if segment.startswith('@@'):
            segment = segment[2:]
            break

        try:
            getitem = context.__getitem__
        except AttributeError:
            break

        try:
            context = getitem(segment)
        except (TypeError, IndexError, KeyError):
            break
    else:
        segment = u""

    result.context = context
    result.method_name = segment
    result.subpath = path[i + 1:]
    result.traversed = path[:i + 1]
    result.root = root
    return result


def traverse(root, path):
    result = traverse_result(root, path)
    view_class = registry.get_view_class(result.context)
    return view_class(result)


# Shortcut
def get_response(request, root, path, error_message="Not found.", exception=Http404):
    try:
        view = traverse(root, path)
        return view(request)
    except TraversalError:
        raise exception(error_message)
