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

    def get_view(self, context):
        try:
            return self.views[context.__class__]
        except KeyError:
            raise ViewNotFound("No registered view for %r" % context)

registry = _ViewRegistry()


class TraverseResult(object):
    def __init__(self, **kwargs):
        self._results = {
            'root': None,
            'context': None,
            'method_name': u"",
            'subpath': (),
            'traversed': (),
        }
        self._results.update(kwargs)

    def __setattr__(self, attr, value):
        if attr == "_results":
            super(TraverseResult, self).__setattr__(attr, value)
        else:
            self._results[attr] = value

    def __getattr__(self, attr):
        try:
            return self._results[attr]
        except KeyError:
            return getattr(self._results, attr)

    def __setitem__(self, key, value):
        self._results[key] = value

    def __getitem__(self, key):
        return self._results[key]


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


def traverse(root, path):
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

    result = TraverseResult(
        context=context,
        method_name=segment,
        subpath=path[i + 1:],
        traversed=path[:i + 1],
        root=root,
    )
    return result


def get_response(request, root, path):
    result = traverse(root, path)
    view = registry.get_view(result.context)
    return view(request, result)


def get_response_or_404(request, root, path):
    try:
        return get_response(request, root, path)
    except TraversalError, ex:
        raise Http404("%r not found (%s)." % (path, ex))


class View(object):
    def __call__(self, request, result):
        method_name = result.pop("method_name") or "__index__"
        try:
            method = getattr(self, method_name)
        except AttributeError:
            raise MethodNotFound("View %r does not exist." % method_name)
        return method(request, **result)
