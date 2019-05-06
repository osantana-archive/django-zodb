# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

from django.urls import re_path, include

import samples.wiki.urls

urlpatterns = [
    re_path(r'^wiki/', include(samples.wiki.urls)),
]

