# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

import abc
import transaction

from persistent import Persistent
from persistent.mapping import PersistentMapping

from django_zodb.utils import url_quote, camel_case_to_underline
from django_zodb.database import get_connection


class BaseRoot(abc.ABCMeta):
    def __new__(mcs, name, bases, attrs):
        new_class = super(BaseRoot, mcs).__new__(mcs, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, BaseRoot)]
        if not parents:
            return new_class

        meta = attrs.pop("Meta", None)
        new_class.__database__ = getattr(meta, "database", "default")
        new_class.__rootname__ = getattr(meta, "rootname", camel_case_to_underline(name))
        return new_class


class Model(Persistent):
    __name__ = None
    __parent__ = None


class Root(Model, metaclass=BaseRoot):
    pass


class Container(PersistentMapping):
    __name__ = None
    __parent__ = None

    def __setitem__(self, key, value):
        PersistentMapping.__setitem__(self, key, value)
        value.__parent__ = self
        value.__name__ = key

    def __delitem__(self, key):
        self[key].__parent__ = None
        PersistentMapping.__delitem__(self, key)


class RootContainer(Container, metaclass=BaseRoot):
    pass


def _setuproot(root):
    return root


def get_root(rootclass, setup=_setuproot, commit=True, *args, **kwargs):
    try:
        database = rootclass.__database__
        rootname = rootclass.__rootname__
    except AttributeError:
        raise TypeError("%r must implements Root interface." % (rootclass,))

    zodbroot = get_connection(database).root()

    if rootname not in zodbroot:
        zodbroot[rootname] = setup(rootclass(*args, **kwargs))
        if commit:
            transaction.commit()

    return zodbroot[rootname]


def _lineage(model):
    while model is not None:
        yield model
        try:
            model = model.__parent__
        except AttributeError:
            model = None


def _quote_segment(segment):
    if segment.__class__ is str:  # isinstance slighly slower (~15%)
        return url_quote(segment.encode('utf-8'))
    return url_quote(segment)


def model_path(model, prepend=None, *elements):
    path = [location.__name__ or '' for location in _lineage(model)]
    path.reverse()
    path.extend(elements)

    if any(path):
        ret = '/'.join(_quote_segment(segment) for segment in path)
    else:
        ret = '/'

    if prepend is not None:
        return str(prepend) + ret

    return ret
