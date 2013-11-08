#!/usr/bin/env python
# -*- coding: utf-8

from __future__ import print_function
import os
import collections
import shutil
try:
    from configparser import ConfigParser, NoSectionError
except ImportError:     # Python 2 compatibility
    from ConfigParser import SafeConfigParser as ConfigParser, NoSectionError
from .utils import (
    parse_args, chdir, env, get_formula, UnrecognizedFormulaError, run,
    reload_nginx
)


def rm_virtualenv(name):
    print('Removing virtualenv...')
    with chdir(env.virtualenv_root):
        if os.path.exists(name):
            shutil.rmtree(name)


def rm_nginx_conf(name):
    available = env.nginx_conf_dir
    enabled = env.nginx_conf_link_dir

    print('Removing nginx configuration files...')
    with chdir(enabled):
        if os.path.exists(name):
            os.remove(name)
    with chdir(available):
        if os.path.exists(name):
            os.remove(name)


def rm_startup_conf(filename):
    path = env.startup_script_dir

    print('Removing startup scripts...')
    with chdir(path):
        if os.path.exists(filename):
            os.remove(filename)


def kill_appserver(formula):
    print('Stopping server instance...')
    uwsgi = os.path.join(
        env.virtualenv_root, formula.project_name, 'bin', 'uwsgi'
    )
    cmd = '{uwsgi} --stop {pid_file}'.format(
        uwsgi=uwsgi,
        pid_file=os.path.join(formula.containing_dir, 'uwsgi.pid')
    )
    run(cmd, quiet=True)


def main():
    arg_list = collections.OrderedDict((
        ('name', 'name of site to remove'),
    ))
    cl_args = parse_args(arg_list=arg_list)

    config = ConfigParser()
    try:
        with chdir(os.path.join(env.virtualenv_root, cl_args.name)):
            config.read(env.project_config_file_name)
    except OSError:     # Happens if the virtualenv is faulty, etc.
        print('Warning: Cannot load project configuration. '
              'Removal may be incomplete.')

    try:
        formula = get_formula(config.get('Project', 'type', ''), cl_args.name)
    except (UnrecognizedFormulaError, NoSectionError):
        formula = None

    if formula is not None:
        kill_appserver(formula)
        formula.teardown(cl_args)

    rm_startup_conf(env.startup_script_prefix + cl_args.name)
    rm_nginx_conf(cl_args.name)
    rm_virtualenv(cl_args.name)
    reload_nginx()


if __name__ == '__main__':
    main()
