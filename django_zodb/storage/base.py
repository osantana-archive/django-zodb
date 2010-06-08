# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import os

from ZODB.MappingStorage import MappingStorage
from ZODB.FileStorage.FileStorage import FileStorage

from django_zodb.config import parse_bool, REQUIRED
from django_zodb.storage import AbstractStorageFactory


# Basic Storage Factories
class MemoryFactory(AbstractStorageFactory):
    _storage = MappingStorage
    _storage_args = (
        ('blobstorage_dir', str, 'base_directory'),
        ('blobstorage_layout', str, 'layout'),
    )

    def get_base_storage(self, **kwargs):
        return self._wrap_blob(self._storage(), **kwargs)


class FileFactory(AbstractStorageFactory):
    _storage = FileStorage
    _storage_args = (
        ('path', os.path.normpath, 'file_name', REQUIRED),
        ('create', parse_bool, 'create'),
        ('read_only', parse_bool, 'read_only'),
        ('quota', int, 'quota'),
        ('blobstorage_dir', str, 'base_directory'),
        ('blobstorage_layout', str, 'layout'),
    )

    def get_base_storage(self, **kwargs):
        arguments = {}
        if 'base_directory' in kwargs:
            arguments['base_directory'] = kwargs.pop("base_directory")
        if 'layout' in kwargs:
            arguments['layout'] = kwargs.pop("layout")
        arguments['storage'] = self._storage(**kwargs)
        return self._wrap_blob(**arguments)
