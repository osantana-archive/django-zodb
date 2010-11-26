# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import os

from ZODB.MappingStorage import MappingStorage
from ZODB.blob import BlobStorage
from ZODB.FileStorage.FileStorage import FileStorage

from django_zodb.config import parse_bool, REQUIRED
from django_zodb.storage import AbstractStorageFactory


# Basic Storage Factories
class MemoryFactory(AbstractStorageFactory):
    _storage = MappingStorage
    _storage_args = (
        ('blob_dir', str, 'base_directory'),
    )

    def get_base_storage(self, **kwargs):
        storage = self._storage()
        if 'base_directory' in kwargs:
            storage = BlobStorage(storage=storage, **kwargs)
        return storage



class FileFactory(AbstractStorageFactory):
    _storage = FileStorage
    _storage_args = (
        ('path', os.path.normpath, 'file_name', REQUIRED),
        ('create', parse_bool, 'create'),
        ('read_only', parse_bool, 'read_only'),
        ('quota', int, 'quota'),
        ('blob_dir', str, 'blob_dir'),
    )

    def get_base_storage(self, **kwargs):
        return self._storage(**kwargs)
