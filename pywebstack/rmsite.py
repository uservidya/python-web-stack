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
    parse_args, chdir, env, get_formula, UnrecognizedFormulaError
)


def rm_virtualenv(name):
    with chdir(env.virtualenv_root):
        if os.path.exists(name):
            shutil.rmtree(name)


def rm_nginx_conf(name):
    available = '/etc/nginx/sites-available'    # TODO: DRY (with mksite.py)
    enabled = '/etc/nginx/sites-enabled'

    with chdir(enabled):
        if os.path.exists(name):
            os.remove(name)
    with chdir(available):
        if os.path.exists(name):
            os.remove(name)


def rm_startup_conf(filename):
    path = '/etc/init.d'
    with chdir(path):
        if os.path.exists(filename):
            os.remove(filename)


def main():
    arg_list = collections.OrderedDict((
        ('name', 'name of site to remove'),
    ))
    args = parse_args(arg_list=arg_list)

    config = ConfigParser()
    try:
        with chdir(os.path.join(env.virtualenv_root, args.name)):
            config.read(env.project_config_file_name)
    except OSError:     # Happens if the virtualenv is faulty, etc.
        pass

    try:
        formula = get_formula(config.get('Project', 'type', ''), args.name)
    except (UnrecognizedFormulaError, NoSectionError):
        formula = None

    if formula is not None:
        try:
            with chdir(formula.get_wsgi_env()[0]):
                with open('gunicorn.pid', 'r') as f:
                    os.system('kill {pid}'.format(pid=f.read()))
        except IOError:     # No gunicorn.pid, which is alright
            pass
        formula.teardown()

    rm_startup_conf(env.startup_script_prefix + args.name)
    rm_nginx_conf(args.name)
    rm_virtualenv(args.name)
    os.system('service nginx restart')


if __name__ == '__main__':
    main()
