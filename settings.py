DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ''
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

INSTALLED_APPS = (
    'core',
)

TEST_RUNNER='testutils.django_coverage.test_runner_with_coverage'
COVERAGE_MODULES = (
    'django_zodb.storage',
    'django_zodb.database',
    'django_zodb.utils',
    'django_zodb.config',
)
