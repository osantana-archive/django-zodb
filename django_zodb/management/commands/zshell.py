# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import code

from django.core.management.base import NoArgsCommand

from django_zodb.database import get_database_by_name

class Command(NoArgsCommand):
    help = "Runs a Python interactive interpreter and automatically import get_database_by_name() function."
    requires_model_validation = False

    def handle_noargs(self, **options):
        imported_objects = {'get_database_by_name': get_database_by_name}
        code.interact(local=imported_objects)
