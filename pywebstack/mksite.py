#!/usr/bin/env python
# -*- coding: utf-8

from __future__ import print_function
import os
import collections
try:
    from configparser import ConfigParser
except ImportError:     # Python 2 compatibility
    from ConfigParser import SafeConfigParser as ConfigParser
from .utils import (
    chdir, parse_args, fill_opt_args, env, get_formula, pip_install
)


def make_virtualenv(args):
    with chdir(env.virtualenv_root):
        os.system('virtualenv {name}'.format(name=args.name))
        with chdir(args.name):
            os.mkdir(env.project_container_name)


def add_nginx_conf(filename, content):
    available = '/etc/nginx/sites-available'
    enabled = '/etc/nginx/sites-enabled'

    with chdir(available):
        with open(filename, 'w') as f:
            f.write(content)
    with chdir(enabled):
        if os.path.exists(filename):
            os.remove(filename)
        os.symlink(os.path.join(available, filename), filename)


def setup(args):
    config = ConfigParser()
    config.add_section('Project')
    config.set('Project', 'type', args.type)

    formula = get_formula(args.type, args.name)

    # Run environment setup
    make_virtualenv(args)
    pip_install('gunicorn')

    # Formula-specific setup
    formula.setup()

    current_virtualenv = os.path.join(env.virtualenv_root, args.name)

    # Secretly put the config file inside virtualenv to store project info
    with chdir(current_virtualenv):
        with open(env.project_config_file_name, 'w+') as f:
            config.write(f)

    # Setup nginx
    add_nginx_conf(args.name, formula.get_nginx_conf(args.bind_to))

    # (Re-)starts the server
    path, wsgi_module = formula.get_wsgi_env()
    with chdir(path):
        gunicorn = os.path.join(current_virtualenv, 'bin', 'gunicorn')
        print(gunicorn)
        os.system(
            '{gunicorn} {module} '
            '--bind={bind_to} --pid gunicorn.pid --daemon'.format(
                gunicorn=gunicorn, module=wsgi_module, bind_to=args.bind_to
            )
        )
    # TODO: Write this command to /etc/init.d?
    os.system('service nginx restart')


def main():
    arg_list = collections.OrderedDict((
        ('type', ('WSGI ptoject type',)),
        ('name', ('name of site',)),
    ))
    opt_arg_list = collections.OrderedDict((
        ('bind_to', ('where to bind Gunicorn', '127.0.0.1:8001')),
    ))
    args = parse_args(arg_list, opt_arg_list)
    args = fill_opt_args(args, opt_arg_list)

    env.pip = os.path.join(env.virtualenv_root, args.name, 'bin', 'pip')
    setup(args)


if __name__ == '__main__':
    main()
