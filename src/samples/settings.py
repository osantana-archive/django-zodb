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

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ':memory:'

ZODB = {
    'default': ['file://' + os.path.join(ROOTDIR, "wiki_db.fs")],
}

ROOT_URLCONF = 'samples.urls'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django_zodb.middleware.TransactionMiddleware',
)

TEMPLATE_DIRS = (os.path.join(ROOTDIR, "templates"),)

INSTALLED_APPS = (
    'django_zodb',
    'samples.wiki',
)


