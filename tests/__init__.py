#!/usr/bin/env python
# -*- coding: utf-8

import os.path
import shutil
import tempfile
from pywebstack import utils

ALL_FORMULAE_NAMES = (
    'django', 'Django'
)

PROJECT_NAME = 'omega_directive'

TEMP_DIR = os.path.join(tempfile.gettempdir(), 'pywebstack_test')


def create_tempdir():
    utils.mkdir_p(TEMP_DIR)


def cleanup_tempdir():
    shutil.rmtree(TEMP_DIR)
