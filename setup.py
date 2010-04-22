# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

import os

from setuptools import setup, find_packages

from django_zodb.version import __version__

long_description = file(
    os.path.join(
        os.path.dirname(__file__),
            'README.rst'
        )
).read()

setup(
    name='django-zodb',
    version=__version__,
    description='Using Django and ZODB together',
    long_description=long_description,
    author='Osvaldo Santana Neto',
    author_email='osantana@triveos.com',
    license="BSD",
    url='http://triveos.github.com/django-zodb/',
    download_url='http://github.com/triveos/django-zodb/tarball/master',
    package_dir={'django_zodb': 'django_zodb'},
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'ZODB3>=3.9.3',
        'repoze.zodbconn>=0.10',
        'Django>=1.1.1',
    ],
    extras_require={
        'MySQL': ['mysql-python'],
        'PostgreSQL': ['psycopg2'],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

