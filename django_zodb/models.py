# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

from persistent.mapping import PersistentMapping

class RootContainer(PersistentMapping):
    __name__ = None
    __parent__ = None

