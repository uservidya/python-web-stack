#!/usr/bin/env python
# -*- coding: utf-8

import os.path
from nose.tools import ok_, with_setup
from pywebstack import mksite, rmsite, utils
from . import *


utils.env.update({
    'virtualenv_root': os.path.join(TEMP_DIR, 'virtualenv'),
    'nginx_conf_dir': os.path.join(TEMP_DIR, 'nginx', 'available'),
    'nginx_conf_link_dir': os.path.join(TEMP_DIR, 'nginx', 'enabled'),
    'startup_script_dir': os.path.join(TEMP_DIR, 'init.d')
})


def _create_tempdirs():
    create_tempdir()
    utils.mkdir_p(utils.env.virtualenv_root)
    utils.mkdir_p(utils.env.nginx_conf_dir)
    utils.mkdir_p(utils.env.nginx_conf_link_dir)
    utils.mkdir_p(utils.env.startup_script_dir)


@with_setup(setup=_create_tempdirs, teardown=cleanup_tempdir)
def test_rm_virtualenv():
    cl_args = MockedArguments(name=PROJECT_NAME)
    mksite.make_virtualenv(cl_args)
    rmsite.rm_virtualenv(PROJECT_NAME)

    path = os.path.join(utils.env.virtualenv_root, PROJECT_NAME)
    ok_(not os.path.exists(path))   # The virtualenv should *not* exist


if __name__ == '__main__':
    import nose
    nose.run(argv=[__file__, '--with-doctest', '-vv'])
