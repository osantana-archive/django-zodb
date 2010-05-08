# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import urllib

from django.http import Http404


class TraversalError(Exception):
    pass

class ContextNotFound(TraversalError):
    pass

class MethodNotFound(TraversalError):
    pass

class ViewNotFound(TraversalError):
    pass

class _ViewRegistry(object):
    def __init__(self):
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
    def __init__(self, root, context, method_name=None, subpath=None):
        self.context = context
        if method_name:
            self.method_name = method_name
        else:
            self.method_name = "__index__"

        self.root = root
        self.subpath = subpath

    def __call__(self, request):
        try:
            view_method = getattr(self, self.method_name)
        except AttributeError:
            raise MethodNotFound("View %r does not exist." % self.method_name)

        return view_method(request, self.context)


def traverse_or_404(root, path, error_message="Not found."):
    try:
        return traverse(root, path)
    except ContextNotFound:
        raise Http404(error_message)

def get_response(request, root, path, error_message="Not found.", exception=Http404):
    try:
        view = traverse(root, path)
        return view(request)
    except TraversalError:
        raise exception(error_message)


# Portions of Zope and Repoze.BFG projects.
# http://svn.repoze.org/repoze.bfg/trunk/repoze/bfg/traversal.py
# http://svn.repoze.org/repoze.bfg/trunk/repoze/bfg/location.py
# See COPYING for license and copyright informations.
#
def split_path(path):
    "foo/bar//baz/../x%20y/%C3/ -> (u'foo', u'bar', u'x y', u'?')"

    path = path.strip('/')
    clean = []
    for segment in path.split('/'):
        segment = urllib.unquote(segment)
        if not segment or segment == '.':
            continue
        elif segment == '..':
            del clean[-1]
        else:
            try:
                segment = segment.decode('utf-8')
            except UnicodeDecodeError:
                raise TypeError('Could not decode path segment %r using the '
                                'UTF-8 decoding scheme' % segment)
            clean.append(segment)
    return tuple(clean)


# We'll need the functions below
def traverse(root, path):
    "traverse(root, 'foo/bar/baz/m1/m2/m3') -> view instance"

    path = split_path(path)
    model = root
    for i, segment in enumerate(path):
        # Stop
        if segment[:2] == '@@':
            ret = {
                'context': model,
                'view_method': segment[2:],
                'subpath': path[i + 1:],
                'traversed': path[:i + 1],
                'root': root
            }
            break

        # Is Leaf
        try:
            getitem = model.__getitem__
        except AttributeError:
            ret = {
                'context': model,
                'view_method': segment,
                'subpath': path[i + 1:],
                'traversed': path[:i + 1],
                'root': root
            }
            break

        # Get next model
        try:
            model = getitem(segment)
        except KeyError:
            ret = {
                'context': model,
                'view_method': segment,
                'subpath': path[i + 1:],
                'traversed': path[:i + 1],
                'root': root
            }
            break
    else:
        # Finished
        ret = {
            'context': model,
            'view_method': u'',
            'subpath': u'',
            'traversed': path,
            'root':root
        }

    view_class = registry.get_view_class(ret['context'])
    return view_class(**ret)



    # {
    # 'context': <baz object>,
    # 'root': <root object>,
    # 'view_method': 'm1',
    # 'subpath': '/m2/m3',
    # 'traversed': '/foo/bar'} || KeyError"""


# def lineage(model):
#     "generator(model, parent1, parent2, ...)"
#     while model is not None:
#         yield model
#         try:
#             model = model.__parent__
#         except AttributeError:
#             model = None
# def _model_path_list(model, *elements):
#     """Implementation detail shared by model_path and model_path_seq"""
#     path = [loc.__name__ or '' for loc in lineage(model)]
#     path.reverse()
#     path.extend(elements)
#     return path
# @memoize
# def quote_path_segment(segment):
#     if segment.__class__ is unicode: # isinstance slighly slower (~15%)
#         return url_quote(segment.encode('utf-8'))
#     return url_quote(segment)
# def find_model(model, path):
#     "find_model(root, path='/foo/bar/baz') -> baz object"
#     traverse_dict = traverse(model, path)
#     view_method = traverse_dict['view_method']
#     context = traverse_dict['context']
#     if view_method:
#         raise KeyError('%r has no subelement %s' % (context, view_method))
#     return context
# def model_path_seq(model, *elements):
#     """model_path_seq(baz_object, 'm1', 'm2', ...) ->
#     ('foo', 'bar', 'baz', 'm1', 'm2', ...)"""
#     return tuple(_model_path_list(model, *elements))
# def _join_path_seq(seq):
#     return seq and '/'.join(quote_path_segment(x) for x in seq) or '/'
# def model_path(model, *elements):
#     "join(model.path(), *elements)"
#     return _join_path_seq(model_path_seq(model, *elements))
