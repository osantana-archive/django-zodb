# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#


import os
import shutil
import subprocess
import logging
import tempfile
import random


def make_uri_path(path):
    path = path.replace("\\", "/")
    if path[0] != "/":
        path = "/" + path  # for windows URI path
    if path[-1] != "/":
        path = path + "/"
    return path


TOOLS_DIR = os.path.dirname(os.path.realpath(__file__))
TOOLS_DIR_URI = make_uri_path(TOOLS_DIR)

TEMP_DIR = os.path.join(tempfile.gettempdir(), "djangozodb_" + str(random.randint(100, 1000)))
os.mkdir(TEMP_DIR)
TEMP_DIR_URI = make_uri_path(TEMP_DIR)


def remove_db_files():
    filelist = [
        os.path.join(TEMP_DIR, 'test.db'),
        os.path.join(TEMP_DIR, 'test.db.lock'),
        os.path.join(TEMP_DIR, 'test.db.index'),
        os.path.join(TEMP_DIR, 'test.db.tmp'),
        os.path.join(TEMP_DIR, 'blobdir')
    ]
    for filename in filelist:
        if os.path.isdir(filename):
            shutil.rmtree(filename)
        if os.path.exists(filename):
            os.remove(filename)


def get_tool_uri_path(filename):
    return os.path.join(TOOLS_DIR_URI, filename).replace("\\", "/")


def start_zeo(mode='host'):
    zeoconf = get_tool_uri_path('zeo_test.conf')
    if mode == 'host':
        args = ["runzeo", '-C', zeoconf]
    else:
        args = ["runzeo", '-a', '/tmp/zeo.zdsock', '-C', zeoconf]
    zeo = subprocess.Popen(args)
    return zeo


class _NullHandler(logging.Handler):
    def emit(self, record):
        pass

def turn_off_log(logger):
    logging.getLogger(logger).addHandler(_NullHandler())

