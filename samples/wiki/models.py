# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

import markdown2 # http://pypi.python.org/pypi/Markdown

from django_zodb import models

# models.Root      - Define a 'root' object for database
# models.Container - Implements a dict()-like interface.
class Wiki(models.Root, models.Container):

    # It's possible to change models.Root defaults using
    # Meta configurations.
    class Meta:
        database = 'default' # Optional. Default: 'default'
        root_name = 'wiki'   # Optional. Default: RootClass.__name__.lower()


class Page(models.Container):
    def __init__(self, title, content="Empty Page."):
        self.title = title
        self.content = content

    def get_content_html(self):
        md = markdown2.Markdown(
                safe_mode="escape",
                extensions=('codehilite', 'def_list', 'fenced_code'))
        return md.convert(self.content)

