# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import os
ROOTDIR = os.path.dirname(os.path.realpath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = "oaaukuyaziazhiazih78156178gziuziz"

ZODB = {
    'default': ['file://' + ("/" if not ROOTDIR.startswith("/") else "") + os.path.join(ROOTDIR, "wiki_db.fs").replace("\\", "/")],
}

ROOT_URLCONF = 'samples.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(ROOTDIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]



MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django_zodb.middleware.TransactionMiddleware',
)


INSTALLED_APPS = (
    'django_zodb',
    'samples.wiki',
)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    },
}


