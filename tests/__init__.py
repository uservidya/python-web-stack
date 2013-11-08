#!/usr/bin/env python
# -*- coding: utf-8

import os.path
import shutil
import tempfile
from pywebstack import utils


__all__ = [
    'ALL_FORMULAE_NAMES', 'PROJECT_NAME', 'TEMP_DIR',
    'MockedArguments',
    'create_tempdir', 'cleanup_tempdir'
]


ALL_FORMULAE_NAMES = (
    'django', 'Django'
)

PROJECT_NAME = 'omega_directive'

TEMP_DIR = os.path.join(tempfile.gettempdir(), 'pywebstack_test')


class MockedArguments(object):
    def __init__(self, **attributes):
        for k in attributes:
            setattr(self, k, attributes[k])


def create_tempdir():
    utils.mkdir_p(TEMP_DIR)


def cleanup_tempdir():
    shutil.rmtree(TEMP_DIR)
