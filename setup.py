# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


from distutils.core import setup

setup(
    name='django-zodb',
    version='0.1',
    description='Using Django and ZODB together',
    author='Osvaldo Santana Neto',
    author_email='osantana@triveos.com',
    url='http://github.com/osantana/django-zodb',
    package_dir={'django_zodb': 'django_zodb'},
    packages=[
        'django_zodb',
        'django_zodb.management',
        'django_zodb.management.commands'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
