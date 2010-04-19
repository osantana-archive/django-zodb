Django-ZODB
===========

`Django-ZODB`_ is a simple `ZODB`_ database backend for `Django`_ Framework.

It's strongly inpired in `repoze.zodbconn`_.

**Warning**: This is a Work-in-Progress project, so, there is a big chance that
some future modifications will break your application.

Installation
------------

Django-ZODB requires the following packages:

* `Django`_ >= 1.1.1
* `ZODB`_ >= 3.9.3

If you need to store your data in a RDBMS system you will need to install the following
packages too:

* `RelStorage`_ — ZODB storage system that store pickles in a relational database (in a
  non-relational format).
* `MySQLdb`_ — required to connect `MySQL`_ database.
* `psycopg2`_ — required to connect `PostgreSQL`_ database.
* `cx_Oracle`_ - required to connect `Oracle`_ database.

Install from sources::

    $ python setup.py install

Or from PyPI (using easy_install)::

    $ easy_install -U django-zodb

Running tests
-------------

`Django-ZODB`_ uses Django standard test runner and we've split tests in X categories:

1. ``core`` - test only core functions and builtin memory-only storages.
2. ``file`` - only tests that write files on disk but doesn't require optional packages.
3. ``mysql`` - tests that requires ``RelStorage``, ``MySQLdb`` and MySQL server in localhost.
4. ``psycopg2`` - tests that requires ``RelStorage``, ``psycopg2`` and PostgreSQL server in
   localhost.
5. ``oracle`` - tests that requires ``RelStorage``, ``cx_Oracle`` and Oracle server in
   localhost.

To run tests::

    $ python manage.py test [test categories]

Getting Started
---------------

Configuration
~~~~~~~~~~~~~

You need to configure your `settings.py` like this::

    ZODB = {
        'db1': {
            'uri': 'file:///var/lib/sitedata.db?blob_dir=/var/lib/blobstorage_dir',
            'test': 'mem:',
        },
        'db2': {
            'uri': 'zconfig:///srv/www/zodb_media.conf',
            'test': 'file:///tmp/test.db?demostorage=true',
        },
        'db3': {
            'uri': 'mysql://user@passwd:localhost/relstorage_db',
            'test': 'postgresql://user@passwd:pg_test:5678/app1_db',
        },
        'db4': {
            'uri': 'zeo://localhost:7899',
            'test': 'zeo:///path/to/zeo.sock',
        },
    }


Opening a database
~~~~~~~~~~~~~~~~~~

To open a ZODB database you use::

    from django_zodb.db import open_database
    db = open_database('db1')

The ``open_database()`` function will use ``settings.ZODB['db1']['uri']`` to
stablish a database connection and return a ``django_zodb.db.Database`` object
that is only a wrapper of ``ZODB.Database`` instance.

If you pass an argument ``test=True`` to the ``open_database()`` it will use
``settings.ZODB['db1']['test']`` instead of ``settings.ZODB['db1']['uri']`` to
open database::

    from django_zodb.db import open_database
    db_test = open_database('db1', test=True)


Available URIs Schemes
~~~~~~~~~~~~~~~~~~~~~~

There is 7 available schemes to create a ZODB connection.

``mem:`` (``MappingStorage``)
'''''''''''''''''''''''''''''

XXX


``file:`` (``FileStorage``)
'''''''''''''''''''''''''''

XXX

``zconfig:`` (``ZCMLConfig``)
'''''''''''''''''''''''''''''

XXX

``zeo:`` (``ZEOStorage``)
'''''''''''''''''''''''''

XXX

.. * ``mysql:`` - RelStorage (mysql)
.. * ``postgresql:`` - RelStorage (pg)
.. * ``oracle:`` - RelStorage (oracle)
.. 1. This URIs uses `RelStorage`_ (that requires `MySQLdb`_ for MySQL connections
..   and `psycopg2`_ for `PostgreSQL`_ connections). RelStorage only provides drivers
..   for MySQL, PostgreSQL and Oracle drivers.



.. _Django-ZODB: http://triveos.github.com/django-zodb/
.. _ZODB: http://pypi.python.org/pypi/ZODB3
.. _Django: http://www.djangoproject.com/
.. _RelStorage: http://pypi.python.org/pypi/RelStorage/
.. _MySQLdb: http://pypi.python.org/pypi/MySQL-python/
.. _MySQL: http://www.mysql.com/
.. _psycopg2: http://pypi.python.org/pypi/psycopg2/
.. _PostgreSQL: http://www.postgresql.org/
.. _cx_Oracle: http://pypi.python.org/pypi/cx_Oracle/
.. _Oracle: http://www.oracle.com/
.. _repoze.zodbconn: http://docs.repoze.org/zodbconn/
