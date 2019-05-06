# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

from django.urls import re_path

import samples.wiki.views

urlpatterns = [
     re_path(r'^(?P<path>.*)/?$', samples.wiki.views.page)
]
