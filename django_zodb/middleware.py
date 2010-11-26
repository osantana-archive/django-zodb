# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

import transaction


class TransactionMiddleware(object):
    enabled = True

    def process_exception(self, request, exception):  # pylint:disable-msg=W0613
        if self.enabled:
            transaction.abort()

    def process_response(self, request, response):  # pylint:disable-msg=W0613
        if self.enabled:
            transaction.commit()
        return response

    @classmethod
    def disable(cls):
        cls.enabled = False

    @classmethod
    def enable(cls):
        cls.enabled = True
