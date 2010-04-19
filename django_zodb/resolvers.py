# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from urlparse import urlparse


class MemoryResolver(object):
    def __call__(self, netloc, path, query):
        pass

class FileResolver(object):
    def __call__(self, netloc, path, query):
        pass

RESOLVERS = {
    'mem': MemoryResolver(),
    'file': FileResolver(),
    'zeo': ZeoResolver(),
    'zconfig': ZConfigResolver(),
    'postgresql': RelStorageResolver('postgresql'),
    'mysql': RelStorageResolver('mysql'),
}

def get_resolver(scheme):
    try:
        return RESOLVER[scheme]
    except KeyError:
        raise ValueError('Unknown connection scheme: %s' % (scheme,))
