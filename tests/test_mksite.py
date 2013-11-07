#!/usr/bin/env python
# -*- coding: utf-8

import os.path
import shutil
import tempfile
from nose.tools import ok_, with_setup
from pywebstack import mksite, utils


utils.env.virtualenv_root = tempfile.gettempdir()
PROJECT_NAME = 'omega_directive'


class MockedArguments(object):
    def __init__(self, **attributes):
        for k in attributes:
            setattr(self, k, attributes[k])


def _clean_virtualenv():
    shutil.rmtree(utils.normalize(utils.env.virtualenv_root, PROJECT_NAME))


@with_setup(teardown=_clean_virtualenv)
def test_make_virtualenv():
    cl_args = MockedArguments(name=PROJECT_NAME)
    mksite.make_virtualenv(cl_args)

    virtualenv_path = utils.normalize(utils.env.virtualenv_root, PROJECT_NAME)
    ok_(os.path.exists(virtualenv_path))
    ok_(os.path.exists(
        utils.normalize(virtualenv_path, utils.env.project_container_name))
    )


if __name__ == '__main__':
    import nose
    nose.run(argv=[__file__, '--with-doctest', '-vv'])
