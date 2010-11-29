# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^(?P<path>.*)/?$', 'samples.wiki.views.page'),
)
