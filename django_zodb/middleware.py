# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from django_zodb import db

class TransactionMiddleware(object):
    def process_request(self, request):
        pass

    def process_exception(self, request, exception): #pylint:disable-msg=W0613
        db.rollback()
        
    def process_response(self, request, response): #pylint:disable-msg=W0613
        db.commit()
        return response
