# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import code

from django.core.management.base import NoArgsCommand

from django_zodb import db

class Command(NoArgsCommand):
    help = "Runs a Python interactive interpreter and automatically import ZODB as db object."
    requires_model_validation = False

    def handle_noargs(self, **options):
        db.disable_commit()
        imported_objects = {'db': db}
        code.interact(local=imported_objects)
