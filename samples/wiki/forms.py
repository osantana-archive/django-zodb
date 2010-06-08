# -*- coding: utf-8 -*-
#
# django-zodb sample - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from django import forms


class PageEditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)
