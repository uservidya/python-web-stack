#!/usr/bin/env python
# -*- coding: utf-8

from __future__ import print_function
import os.path
import collections
import shutil
try:
    from configparser import ConfigParser
except ImportError:     # Python 2 compatibility
    from ConfigParser import SafeConfigParser as ConfigParser
from .utils import parse_args, chdir, env, get_formula


def rm_virtualenv(name):
    with chdir(env.virtualenv_root):
        shutil.rmtree(name)


def main():
    arg_list = collections.OrderedDict((
        ('name', 'name of site to remove'),
    ))
    args = parse_args(arg_list=arg_list)

    config = ConfigParser()
    with chdir(os.path.join(env.virtualenv_root, args.name)):
        config.read(env.project_config_file_name)

    formula = get_formula(config.get('Project', 'type'), args.name)

    with chdir(formula.get_wsgi_env()[0]):
        with open('gunicorn.pid', 'r') as f:
            os.system('kill {pid}'.format(pid=f.read()))

    formula.teardown()
    rm_virtualenv(args.name)


if __name__ == '__main__':
    main()
