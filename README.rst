Django-ZODB
===========

`Django-ZODB`_ is a simple `ZODB`_ database backend for `Django`_ Framework.

It's strongly inpired in `repoze.zodbconn`_.

.. Warning:: This is a Work-in-Progress project, so, there is a big chance that
   some future modifications will break your application.

Installation
------------

Django-ZODB requires the following packages:

* `Django`_ 1.1.1 or newer
* `ZODB`_ 3.10.0a2 or newer

If you need to store your data in a RDBMS system you will need to install the
following packages too:

* `RelStorage`_ 1.4.0b3 or newer — ZODB storage system that store pickles in a
  relational database (in a non-relational format).
* `MySQLdb`_ 1.2.3c1 or newer — required to connect `MySQL`_ database.
* `psycopg2`_ 2.2.0rc1 or newer — required to connect `PostgreSQL`_ database.
* `cx_Oracle`_ 5.0.3 or newer — required to connect `Oracle`_ database.

Install from sources::

    $ python setup.py install

Or from PyPI (using easy_install)::

    $ easy_install -U django-zodb

Running tests
-------------

Install coverage_ if you need test coverage informations::

    $ easy_install -U coverage

To run tests::

    $ python manage.py test

Configuration
-------------

You need to configure your ``settings.py`` like this::

    ZODB = {
        'default': [
            'mysql://user@passwd:localhost/relstorage_db?database_name=app',
            'postgresql://user@passwd:pg_test:5678/app1_db',
        ],
        'test':      [ 'mem://', 'mem://?database_name=catalog' ],
        'legacy_db': [ 'zconfig:///srv/www/zodb_media.conf' ],
        'user_dir':  [
            'zeo://main_db.intranet:7899?database_name=main',
            'zeo://catalog.intranet:7898?database_name=catalog'
        ],
        'old_app':   [
            'file:///var/lib/sitedata.db?blob_dir=/var/lib/blobstorage_dir'
        ],
    }

You can find a list of schemes and connection adapters in `Connection Schemes`_.

Creating sample application
===========================

I strongly believe in "learn by doing" strategy, so, let's create a sample
Wiki application that stores their pages in ZODB.

I suggest the reading of the following tutorials and articles if you don't know
ZODB or the Traversal Algorithm (that we will use in our tutorial):

* `ZODB Tutorial`_
* `ZODB Programming Guide`_
* `Traversal`_ chapter at `Repoze.BFG documentation`_.

Starting Django Project and Application
---------------------------------------

We will start a project called ``intranet`` with a Django application called
``wiki``::

    $ django-admin.py startproject intranet
    $ cd intranet
    intranet $ python manage.py startapp wiki

Now we need to modify our ``settings.py`` to include this new application and
configure our database connections::

    #!/usr/bin/env python
    # settings.py

    import os
    ROOTDIR = os.path.dirname(os.path.realpath(__file__))

    # No relational database...
    DATABASE_ENGINE = 'sqlite3'
    DATABASE_NAME = ':memory:'

    # append the following lines:
    ZODB = {
        'default': ['file://' + os.path.join(ROOTDIR, 'wiki_db.fs')],
    }

    # ... other Django configurations ...

    INSTALLED_APPS = (
        'wiki',
    )

Let's create our model classes. We will need a "root" object that will store our
objects (let's name it ``Wiki``) and a model to store the wiki pages itself
(``Page``)::

    #!/usr/bin/env python
    # wiki/models.py


    from django_zodb import models


    # models.RootContainer - Define a 'root' object for database. This class
    #                        defines __parent__ = __name__ = None
    class Wiki(models.RootContainer):

        # It's possible to change models.RootContainer settings using Meta
        # configurations. Here we will explicitly define the default values
        class Meta:
            database = 'default' # Optional. Default: 'default'
            root_name = 'wiki'   # Optional. Default: RootClass.__name__.lower()


    # models.Container - We will use Container to add support to subpages.
    class Page(models.Container):
        def __init__(self, content="Empty Page."):
            self.content = content


We've a configured application and models. It's time to map an URL to our view
function::

    #!/usr/bin/env python
    # urls.py

    # ... Django default URL configurations ...

    urlpatterns = patterns('',
        # ... other URL mappings ...
        (r'^(?P<path>.*)/?$', 'wiki.views.page'),
    )

And ``wiki/views.py``::

    #!/usr/bin/env python
    # views.py

    from django.shortcuts import render_to_response

    from django_zodb import views

    from wiki.models import Wiki, Page

    class PageView(views.View):
        def __index__(self, request, context, subpath):
            return render_to_response("page.html", {'context': context})

    views.registry.register(Page, PageView)

    def page(request, path):
        return views.get_response(request, root=Wiki(), path=path)

Traversal
---------

From `Repoze.BFG documentation`_:

    Traversal is a context finding mechanism. It is the act of finding a context and
    a view name by walking over an object graph, starting from a root object, using
    a request object as a source of path information.

Django-ZODB implements the traversal algorithm in function
``django_zodb.views.traverse()`` that receive two arguments:

* ``root`` — an instance of Root model.
* ``path`` — a string with the path to be traversed.

And return a callable ``views.Viewer`` object that receive ``request`` as argument
and returns a ``HttpResponse()``::

    def view_function(request, path):
        viewer = traverse(root, path)
        return viewer(request)


The module `django_zodb.views` also provides a utility function that raises an
``Http404()`` when the ``path`` points to a non-existent model object. You can
use this function to replace the following code structure::

        from django_zodb import views

        try:
            context, view_name = traverse(root, path)
        except django.views.ContextNotFound:
            raise Http404("Page '%s' not found." % (path,))

With a simple function call::

        from django_zodb.views import traverse_or_404

        context, view_name = traverse_or_404(root, path, "Object not found.")

You can read more about about traversal at `Repoze.BFG documentation`_

.. Connection Schemes:

Connection Schemes
------------------

You can specify a ZODB connection using a URI. This URI is composed of the
following arguments::

    scheme://username:password@host:port/path?arg1=foo&arg2=bar#fraction

Depending on the chosen scheme some of these arguments are required and
others optional.

Database and Connection settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Arguments related to database connection settings. These arguments are optional
and must be passed as query argument in URI (eg. ``?database_name=db&...``).

* ``database_name`` — ``str`` — database name used by ZODB.
* ``connection_cache_size`` — ``int`` — size (in bytes) of database cache.
* ``connection_pool_size`` — ``int`` — size of connection pool.

These arguments are passed to ``ZODB.DB.DB()`` constructor.

Memory Storage ``mem:`` (``ZODB.MappingStorage``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns an in-memory storage. It's basically a Python ``dict()`` object.

Valid URIs::

    mem
    mem:
    mem://
    mem?database_name=memory

Optional Arguments
''''''''''''''''''

* See `Demo storage argument`_.
* See `Blob storage arguments`_.

File Storage ``file:`` (``ZODB.FileStorage``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a database stored in a file. You need to specify an absolute path to the
database file.

Valid URIs::

    file:///tmp/Data.fs
    file:///tmp/main.db?database_name=file

Invalid URIs::

    file://subdir/Data.fs

Required Arguments
''''''''''''''''''

* ``path`` — ``str`` — absolute path to file where database will be stored.

Optional Arguments
''''''''''''''''''

* ``create`` — ``bool`` — create database file if does not exist. Default:
  ``create=True``.
* ``read_only`` – ``bool`` — open storage only for reading. Default:
  ``read_only=False``.
* ``quota`` — ``int`` — storage quota. Default: disabled (``quota=None``).

* See `Demo storage argument`_.
* See `Blob storage arguments`_.

``zconfig:`` (``ZODB.DB.DB``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns database (or databases) specified in ZCML configuration file.

.. Note:: This scheme has some small differences with other schemes because it
   returns a DB object instead of a Storage. It's a problem only in cases where
   you are creating the connection 'by hand' instead of use a higher level API.

URIs Examples::

    zconfig:///my/app/zodb_config.zcml
    zconfig:///my/app/zodb_config.zcml#main

Required Arguments
''''''''''''''''''

* ``path`` (``str``) - absolute path to file where database will be stored.

Optional Arguments (and default values)
'''''''''''''''''''''''''''''''''''''''

* ``#fragment=''`` (``str``) - Get only an specific database. By default
  (``''``) get only the first database specified in configuration file. We
  don't use a query argument (``&arg=...``) to specify database name to
  keep compatibility with `repoze.zodbconn`_.

``zeo:`` (``ZEO.ClientStorage.ClientStorage``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a connection to a ZEO server.

TODO


``mysql:`` (``RelStorage``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a database stored in a MySQL relational server. This scheme uses
`RelStorage`_ to establish connection.

URIs Examples::

    mysql://user:password@host:3306?compress=true#mysql_db_name
    mysql:///tmp/mysql.sock#local_database
    mysql://localhost#database

TODO

``postgresql`` (``RelStorage``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. Warning:: Not Implemented yet.


.. _`Demo storage argument`:

Demo storage argument
~~~~~~~~~~~~~~~~~~~~~

XXX

.. _`Blob storage arguments`:

Blob storage arguments
~~~~~~~~~~~~~~~~~~~~~~

XXX

TODO
----

::

    - Implement models and views modules (++++)
    - Finish 'samples.wiki' application (++)
    - Update tutorial to reflect 'samples.wiki' source code (+)
    - Add a "narrative" API reference in README.rst (or use docstrings?) (++)

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
.. _coverage: http://pypi.python.org/pypi/coverage/
.. _repoze.zodbconn: http://docs.repoze.org/zodbconn/
.. _ZODB Tutorial: http://www.zodb.org/documentation/tutorial.html
.. _ZODB programming guide: http://www.zodb.org/documentation/guide/index.html
.. _Traversal: http://docs.repoze.org/bfg/current/narr/traversal.html
.. _Repoze.BFG documentation: http://docs.repoze.org/bfg/1.3/
