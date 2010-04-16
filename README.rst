Using Django, ZODB and RelStorage with MySQL backend.

 * Django 1.1.1: http://www.djangoproject.com/
 * ZODB 3.9.3: http://pypi.python.org/pypi/ZODB3
 * RelStorage 1.2.0: http://pypi.python.org/pypi/RelStorage (we'll try 1.4.0b1)

settings.py example:

    :
    ROOT_PATH = os.path.realpath(os.path.dirname(__file__))

    DATABASE_ENGINE = 'mysql'
    DATABASE_NAME = 'zodb_test_db'
    DATABASE_USER = 'zodb_test_db'
    DATABASE_PASSWORD = 'password123'
    DATABASE_HOST = 'mysqlserver'

    ZODB_CONFIG_URL = os.path.join(ROOT_PATH, "localdev_zodb.conf")
    :

localdev_zodb.conf example:

    %import relstorage
    <zodb>
      <relstorage>
        <mysql>
          db zodb_test_db
          user zodb_test_db
          host mysqlserver
          passwd password123
        </mysql>
      </relstorage>
    </zodb>

Tests
=====

To run tests:

 1. Create a test_django_zodb user with database creation permissions in your localhost MySQL.
 2. Run:
    $ cd tests
    $ python runtests.py
