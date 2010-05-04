Django-ZODB
===========

`Django-ZODB`_ is a simple `ZODB`_ database backend for `Django`_ Framework.

It's strongly inpired in `repoze.zodbconn`_.

.. Warning:: This is a Work-in-Progress project, so, there is a big chance that
   some future modifications will break your application.

Installation
------------

Django-ZODB requires the following packages:

* `Django`_ 1.1.1
* `ZODB`_ 3.9.3

If you need to store your data in a RDBMS system you will need to install the
following packages too:

* `RelStorage`_ — ZODB storage system that store pickles in a relational
  database (in a non-relational format).
* `MySQLdb`_ — required to connect `MySQL`_ database.
* `psycopg2`_ — required to connect `PostgreSQL`_ database.
* `cx_Oracle`_ — required to connect `Oracle`_ database.

Install from sources::

    $ python setup.py install

Or from PyPI (using easy_install)::

    $ easy_install -U django-zodb

Running tests
-------------

`Django-ZODB`_ uses Django standard test runner and we've split tests in X
categories:

1. ``core_tests`` — test only core functions and builtin memory-only storages.
2. ``db_mysql_tests`` — tests that requires ``RelStorage``, ``MySQLdb`` and MySQL
   server in localhost.
3. ``db_psycopg2_tests`` — tests that requires ``RelStorage``, ``psycopg2`` and
   PostgreSQL server in localhost.
4. ``db_oracle_tests`` — tests that requires ``RelStorage``, ``cx_Oracle`` and Oracle
   server in localhost.

To run tests::

    $ python manage.py test [test categories*]


Configuration
-------------

You need to configure your `settings.py` like this::

    ZODB = {
        'default': [
            'mysql://user@passwd:localhost/relstorage_db?database_name=main_app',
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

You need to define a URI to specify what database you will connect. The basic
URI structure is::

    scheme://username:password@host:port/path?query_arg1=foo&query_arg2=bar#fraction

You can find a list of schemes and connection adapters in `Connection Schemes`_.

Creating sample application
===========================

I believe the best way to learn something is by developing something. So, let's
create the "Hello World" application of the Web: a simple Wiki for our
intranet using ZODB to store data.

Recommended Reading
-------------------

If you don't know ZODB and/or the Traversal algorithm I strongly recommend to
read the following documents:

* `ZODB Tutorial`_
* `ZODB Programming Guide`_
* `Traversal`_ chapter at bfg.repoze documentation.

Starting Django Project
-----------------------

We will start a project called ``intranet`` and create a Django application
``wiki`` inside this project::

    $ django-admin.py startproject intranet
    $ cd intranet
    intranet $ python manage.py startapp wiki

Now we need to modify our ``settings.py`` to include this new application and
configure our database connections::

    #!/usr/bin/env python
    # settings.py

    import os
    ROOTDIR = os.path.dirname(os.path.realpath(__file__))

    # append the following lines:
    ZODB = {
        'default': [ 'file://%s' % (os.path.join(ROOTDIR, 'wiki_db.fs'),) ],
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

    import markdown2 # http://pypi.python.org/pypi/Markdown

    from django_zodb import models

    # models.Root      - Define a 'root' object for database
    # models.Container - Implements a dict()-like interface.
    class Wiki(models.Root, models.Container):

        # It's possible to change models.Root defaults using
        # Meta configurations.
        class Meta:
            database = 'default' # Optional. Default: 'default'
            root_name = 'wiki'   # Optional. Default: RootClass.__name__.lower()

    class Page(models.Container):
        def __init__(self, title, content="Empty Page."):
            self.title = title
            self.content = content

        def get_content_html(self):
            md = markdown2.Markdown(
                    safe_mode="escape",
                    extensions=('codehilite', 'def_list', 'fenced_code'))
            return md.convert(self.content)


We've a configured application and models. It's time to map an URL to our view
function::

    #!/usr/bin/env python
    # urls.py

    # ... Django default URL configurations ...

    urlpatterns = patterns('',
        # ... other URL mappings ...
        (r'^(?P<path>.*)/?$', 'wiki.views.page'),
    )

And our ``wiki/views.py`` file::

    #!/usr/bin/env python
    # views.py

    from django_zodb import views

    from wiki.models import Wiki, Page

    class PageViewer(views.Viewer):
        def __index__(self, request, context, subpath=""):
            page = {
                'title': context.title,
                'content': context.get_html(),
            }
            return render_to_response("page.html", page)


        def edit(self, request, context, subpath=""):
            # TODO
            page = {
                'title': context.title,
                'content': context.get_html(),
            }
            return render_to_response("edit.html", page)

    views.register(Page, PageViewer)

    def page(request, path):
        return views.get_response(request, root=Wiki(), path=path)

Traversal
---------

From `bfg.repoze documentation`_:

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

You can read more about about traversal at `bfg.repoze documentation`_

.. Connection Schemes:

Connection Schemes
------------------

``mem:`` (``ZODB.MappingStorage.MappingStorage``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a in memory storage.

URIs Examples::

    mem
    mem:
    mem://
    mem?database_name=memory

Optional Arguments
''''''''''''''''''

* See `Common arguments`_.
* See `Blob storage arguments`_.

``file:`` (``ZODB.FileStorage.FileStorage.FileStorage``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a database stored in a file.

URIs Examples::

    file:///tmp/Data.fs
    file:///tmp/main.db#database_name=file

Required Arguments
''''''''''''''''''

* ``path`` (``str``) - absolute path to file where database will be stored.

Optional Arguments (and default values)
'''''''''''''''''''''''''''''''''''''''

* ``create=False`` (``bool``) -
* ``read_only=False`` (``bool``) -
* ``quota=None`` (``int``) - Storage quota. Disabled (``None``) by default.
* See `Common arguments`_.
* See `Blob storage arguments`_.

``zconfig:`` (``ZODB.DB.DB``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns database (or databases) specified in ZCML configuration file.

.. Note:: This scheme has some small differences with other schemes because it
   returns a DB object instead of a Storage. It's a problem only in cases where
   you are creating the connection 'by hand' instead of use a high level API.

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

.. Warning:: Not Implemented yet.

``postgresql`` (``RelStorage``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. Warning:: Not Implemented yet.

.. _`Common arguments`:

Common arguments
~~~~~~~~~~~~~~~~

XXX

.. _`Blob storage arguments`:

Blob storage arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

XXX



.. Opening a database
.. ~~~~~~~~~~~~~~~~~~
..
.. To open a ZODB database you use::
..
..     from django_zodb.database import open_database
..     db = open_database('db1')
..
.. The ``open_database()`` function will use ``settings.ZODB['db1']`` specifications to
.. establish a database connection and returns a ZODB's ``DB()`` object.

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
.. _ZODB Tutorial: http://www.zodb.org/documentation/tutorial.html
.. _ZODB programming guide: http://www.zodb.org/documentation/guide/index.html
.. _Traversal: http://docs.repoze.org/bfg/current/narr/traversal.html
.. _bfg.repoze documentation: http://docs.repoze.org/bfg/1.3/
