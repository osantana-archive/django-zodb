import os

from django.conf.urls.defaults import patterns, include, handler500, handler404

DEFAULT_CHARSET = 'utf-8'

ROOT_PATH = os.path.realpath(os.path.dirname(__file__))

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'django_zodb'
DATABASE_USER = 'test_django_zodb'
DATABASE_PASSWORD = 'test_django_zodb'
DATABASE_HOST = 'localhost'

ZODB_CONFIG_URL = os.path.join(ROOT_PATH, "localdev_zodb.conf")

ROOT_URLCONF = 'settings'

SITE_ID = 1

INSTALLED_APPS = (
    'django_zodb',
)

# TEMPLATE_LOADERS = (
#     'django.template.loaders.app_directories.load_template_source',
# )
# 
# urlpatterns = patterns('',
#     (r'^comments/', include('django.contrib.comments.urls')),
# )
