# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from persistent.mapping import PersistentMapping

from django_zodb.utils import url_quote


# TODO
class RootContainer(PersistentMapping):
    __name__ = None
    __parent__ = None



# Model Path
def _lineage(model):
    while model is not None:
        yield model
        try:
            model = model.__parent__
        except AttributeError:
            model = None

def _quote_segment(segment):
    if segment.__class__ is unicode: # isinstance slighly slower (~15%)
        return url_quote(segment.encode('utf-8'))
    return url_quote(segment)

def model_path(model, *elements):
    path = [location.__name__ or u'' for location in _lineage(model)]
    path.reverse()
    path.extend(elements)

    if not any(path):
        return u'/'

    return u'/'.join(_quote_segment(segment) for segment in path)
