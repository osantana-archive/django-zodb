# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from django_zodb import models

# models.RootContainer - Define a 'root' object for database. This class
#                        defines __parent__ = __name__ = None
class Wiki(models.RootContainer):
    # It's possible to change models.RootContainer settings using Meta
    # configurations. Here we will explicitly define the default values
    class Meta:
        database = 'default' # Optional. Default: 'default'
        root_name = 'wiki'   # Optional. Default: RootClass.__name__.lower()


# models.Container - We will use Container to add support to subpages.
class Page(models.PersistentMapping):
    def __init__(self, content="Empty Page."):
        self.content = content


# TODO:
# import markdown # http://pypi.python.org/pypi/Markdown
#     def get_content_html(self):
#         md = markdown.Markdown(
#                 safe_mode="escape",
#                 extensions=('codehilite', 'def_list', 'fenced_code'))
#         return md.convert(self.content)

