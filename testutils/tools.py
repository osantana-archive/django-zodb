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


TOOLS_DIR = os.path.dirname(os.path.realpath(__file__))

def remove_db_files():
    filelist = (
        '/tmp/test.db',
        '/tmp/test.db.lock',
        '/tmp/test.db.index',
        '/tmp/test.db.tmp',
        '/tmp/blobdir',
    )
    for filename in filelist:
        if os.path.isdir(filename):
            shutil.rmtree(filename)
        if os.path.exists(filename):
            os.remove(filename)

def get_tool_path(filename):
    return os.path.join(TOOLS_DIR, filename)

def start_zeo(mode='host'):
    zeoconf = get_tool_path('zeo_test.conf')
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

