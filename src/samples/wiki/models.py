# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import markdown  # http://pypi.python.org/pypi/Markdown

from django_zodb import models


# models.RootContainer - Define a 'root' object for database. This class
#                        defines __parent__ = __name__ = None
class Wiki(models.RootContainer):
    def pages(self):
        for pagename in sorted(self):
            yield self[pagename]

    def get_absolute_url(self):
        return "/wiki"

    # It's possible to change models.RootContainer settings using Meta
    # configurations. Here we will explicitly define the default values
    class Meta:
        database = 'default'  # Optional. Default: 'default'
        rootname = 'wiki'     # Optional. Default: RootClass.__name__.lower()


# models.Container - We will use Container to add support to subpages.
class Page(models.Model):
    def __init__(self, content="Empty Page."):
        super(Page, self).__init__()
        self.content = content

    def html(self):
        md = markdown.Markdown(
                safe_mode="escape",
                extensions=('codehilite', 'def_list', 'fenced_code'))
        return md.convert(self.content)

    @property
    def name(self):
        return self.__name__

    def get_absolute_url(self):
        return u"/".join((self.__parent__.get_absolute_url(), self.name))
