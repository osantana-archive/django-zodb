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

* `RelStorage`_ 1.4.0b3 or newer - ZODB storage system that store pickles in a
  relational database (in a non-relational format).
* `MySQLdb`_ 1.2.3c1 or newer - required to connect `MySQL`_ database.
* `psycopg2`_ 2.2.0rc1 or newer - required to connect `PostgreSQL`_ database.
* `cx_Oracle`_ 5.0.3 or newer - required to connect `Oracle`_ database.

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

    MIDDLEWARE_CLASSES = (
        # ... other middlewares ...

        # If everything is ok (aka no exception raised) this middleware will
        # run a transaction.commit() on response.
        'django_zodb.middleware.TransactionMiddleware',
    )

    INSTALLED_APPS = (
        'django_zodb',  # enable manage.py zshell command
        'wiki',
    )

Let's create our model classes. We will need a "root" object that will store our
objects (let's name it ``Wiki``) and a model to store the wiki pages itself
(``Page``)::

    #!/usr/bin/env python
    # wiki/models.py

    import markdown  # http://pypi.python.org/pypi/Markdown
    from django_zodb import models

    # models.RootContainer - Define a 'root' object for database. This class
    #                        defines __parent__ = __name__ = None
    class Wiki(models.RootContainer):
        def pages(self):
            for pagename in sorted(self):
                yield self[pagename]

        def get_absolute_url(self):
            return "/wiki"

        # It's possible to change models.RootContainer settings using Meta
        # configurations. Here we will explicitly define the default values
        class Meta:
            database = 'default'  # Optional. Default: 'default'
            rootname = 'wiki'     # Optional. Default: RootClass.__name__.lower()

    # models.Container - We will use Container to add support to subpages.
    class Page(models.Model):
        def __init__(self, content="Empty Page."):
            super(Page, self).__init__()
            self.content = content

        def html(self):
            md = markdown.Markdown(safe_mode="escape",
                    extensions=('codehilite', 'def_list', 'fenced_code'))
            return md.convert(self.content)

        @property
        def name(self):
            return self.__name__

        def get_absolute_url(self):
            return u"/".join((self.__parent__.get_absolute_url(), self.name))

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

    import re

    from django.shortcuts import render_to_response
    from django.http import HttpResponseRedirect
    from django import forms

    import transaction
    from django_zodb import views
    from django_zodb import models

    from samples.wiki.models import Wiki, Page

    wikiwords = re.compile(ur"\b([A-Z]\w+([A-Z]+\w+)+)")


    class PageEditForm(forms.Form):
        content = forms.CharField(widget=forms.Textarea)


    class WikiView(views.View):
        def __index__(self, request, context, root, subpath, traversed):
            return HttpResponseRedirect("FrontPage")

        def add(self, request, context, root, subpath, traversed):
            try:
                name = subpath[0]
            except IndexError:
                return HttpResponseRedirect("/")

            if request.method == "POST":
                form = PageEditForm(request.POST)
                if form.is_valid():
                    page = Page(form.cleaned_data['content'])
                    root[name] = page
                    return HttpResponseRedirect(page.get_absolute_url())
            else:
                form = PageEditForm()

            page_data = {
                'name': name,
                'cancel_link': "javascript:history.go(-1)",
                'form': form,
            }
            return render_to_response("edit.html", page_data)
    views.registry.register(model=Wiki, view=WikiView())


    class PageView(views.View):
        def __index__(self, request, context, root, subpath, traversed):
            content = context.html()

            def check(match):
                word = match.group(1)
                if word in root:
                    page = root[word]
                    view_url = page.get_absolute_url()
                    return '<a href="%s">%s</a>' % (view_url, word)
                else:
                    add_url = models.model_path(root, "", "add", word)
                    return '<a href="%s">%s</a>' % (add_url, word)

            content = wikiwords.sub(check, content)

            page_data = {
                'context': context,
                'content': content,
                'edit_link': context.get_absolute_url() + "/edit",
                'root': root,
            }
            return render_to_response("page.html", page_data)

        def edit(self, request, context, root, subpath, traversed):
            context_path = models.model_path(context)

            if request.method == "POST":
                form = PageEditForm(request.POST)
                if form.is_valid():
                    context.content = form.cleaned_data['content']
                    return HttpResponseRedirect(context_path)
            else:
                form = PageEditForm(initial={'content': context.content})

            page_data = {
                'name': context.name,
                'context': context,
                'cancel_link': context_path,
                'form': form,
            }
            return render_to_response("edit.html", page_data)
    views.registry.register(model=Page, view=PageView())


    def create_frontpage(root):
        frontpage = Page()
        root["FrontPage"] = frontpage
        return root

    def page(request, path):
        root = models.get_root(Wiki, setup=create_frontpage)
        return views.get_response_or_404(request, root=root, path=path)


Traversal
---------

From `Repoze.BFG documentation`_:

    Traversal is a context finding mechanism. It is the act of finding a context
    and a view name by walking over an object graph, starting from a root
    object, using a request object as a source of path information.

Django-ZODB implements the traversal algorithm in function
``django_zodb.views.traverse()`` that receive two arguments:

* ``root`` - an instance of Root model.
* ``path`` - a string with the path to be traversed.

And return a ``views.TraverseResult`` object with the following attributes:

* ``context`` - model object found by traversal.
* ``method_name`` - a method name if exists.
* ``subpath`` - aditional path arguments.
* ``traversed`` - path elements 'traversed'.
* ``root`` - root object.

We've created some shortcuts functions to interpret these results:

* ``get_response(request, root, path) -> HttpResponse``
* ``get_response_or_404(request, root, path) -> HttpResponse or Http404``

These functions will traverse the model tree and call a registered view function
that handle the context model object found. For example::

    def handle_page_objects(request, result):
        # result is a TraverseResult object.
        # result.context is a Page object found by traverse
        return render_to_response(...)

    # Register handle_page_objects function to handle Page objects:
    views.registry.register(model=Page, view=handle_page_objects)

You can register a ``views.View()`` instance to handle model objects::

    class PageView(views.View):
        # This is the 'default' handle (no method_name)
        def __index__(self, request, context, root, subpath, traversed):
            # ... context is a Page object ...
            return render_to_response(...)

        # called when method_name == "edit"
        def edit(self, request, context, root, subpath, traversed):
            # ... context is a Page object ...
            return render_to_response(...)

    # Register a PageView *instance* to handle Page objects
    views.registry.register(model=Page, view=PageView())


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

* ``database_name`` - ``str`` - database name used by ZODB.
* ``connection_cache_size`` - ``int`` - size (in bytes) of database cache.
* ``connection_pool_size`` - ``int`` - size of connection pool.

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

* ``path`` - ``str`` - absolute path to file where database will be stored.

Optional Arguments
''''''''''''''''''

* ``create`` - ``bool`` - create database file if does not exist. Default:
  ``create=True``.
* ``read_only`` - ``bool`` - open storage only for reading. Default:
  ``read_only=False``.
* ``quota`` - ``int`` - storage quota. Default: disabled (``quota=None``).

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

TODO

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

* Review my 'engrish' in documentation
* Test with Django >= 1.2
* Finish this README (remove XXX)
* Create a new Website
* Release 0.2 version (and announce)
* Test Relstorage connections with Oracle and PostgreSQL
* Create more manage.py commands for ZODB management
* Create a Django-ORM layer (wow!)
* Evaluate some fulltext-search, catalog, etc integrations
* Fix performance issues (?)
* ... and fix (tons of) bugs! :D


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
