# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import logging

from ZODB.blob import BlobStorage
from ZODB.DemoStorage import DemoStorage

from django_zodb.config import parse_bool, get_configuration_from_uri


# Utilities
log = logging.getLogger("django_zodb.storage")


# Factory Base
class AbstractStorageFactory(object):
    _storage_args = ()

    def __init__(self, config):
        self.demostorage = parse_bool(config.pop('demostorage', "false"))
        self.config = config

    def _wrap_blob(self, storage, **kwargs):
        if 'base_directory' not in kwargs:
            return storage
        return BlobStorage(storage=storage, **kwargs)

    def get_base_storage(self, *args, **kwargs):
        raise NotImplemented("Abstract class: %r, %r" % (args, kwargs))  # pragma: no cover abstract method code

    def get_storage(self):
        settings = self.config.get_settings(self._storage_args)
        storage = self.get_base_storage(**settings)
        if self.demostorage:
            storage = DemoStorage(base=storage)
        return storage


# Factories Registry
class _FactoriesRegistry(object):
    def __init__(self):
        self.enabled = {}
        self.disabled = {}

    def enable(self, scheme, factory_class):
        self.enabled[scheme] = factory_class

    def disable(self, scheme, reason):
        self.disabled[scheme] = str(reason)

    def available(self):
        return self.enabled.keys()

    def get(self, scheme):
        return self.enabled[scheme]

    def disable_reason(self, scheme):
        return self.disabled[scheme]

    def register(self, scheme, factory):
        try:
            package_name, module_name, factory_name = factory.rsplit(".", 2)
            module = __import__(package_name + "." + module_name, fromlist=module_name)
            factory_class = getattr(module, factory_name)
            self.enable(scheme, factory_class)
        except (ImportError, AttributeError, IndexError), ex:
            self.disable(scheme, ex)

factories = _FactoriesRegistry()


# Register Factories
factories.register("mem", "django_zodb.storage.base.MemoryFactory")
factories.register("file", "django_zodb.storage.base.FileFactory")
factories.register("zeo", "django_zodb.storage.zeo.ZEOFactory")
factories.register("mysql", "django_zodb.storage.mysql.MySQLFactory")
factories.register("postgresql", "django_zodb.storage.postgresql.PostgreSQLFactory")
factories.register("oracle", "django_zodb.storage.oracle.OracleFactory")


# Get storages
def get_storage(config):
    try:
        scheme = config.pop('scheme')
        factory = factories.get(scheme)
    except KeyError:
        raise ValueError('Invalid or Unknown scheme: %s' % (scheme,))

    storage = factory(config).get_storage()

    return storage


def get_storage_from_uri(uri):
    config = get_configuration_from_uri(uri)
    return get_storage(config)
