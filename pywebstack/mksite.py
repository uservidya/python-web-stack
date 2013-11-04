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


def add_startup_conf(filename, content):
    path = '/etc/init.d'
    with chdir(path):
        with open(filename, 'w') as f:
            f.write(content)


def setup(formula, args):
    config = ConfigParser()
    config.add_section('Project')
    config.set('Project', 'type', args.type)

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
    gunicorn_command = (
        '{gunicorn} {module} -D -b 127.0.0.1:{bind_to} -p {pid_file}'.format(
            gunicorn=os.path.join(current_virtualenv, 'bin', 'gunicorn'),
            module=args.wsgi_path, bind_to=args.bind_to,
            pid_file=os.path.join(formula.containing_dir, 'gunicorn.pid')
        )
    )
    with chdir(args.wsgi_root):
        os.system(gunicorn_command)
    add_startup_conf(
        env.startup_script_prefix + args.name,
        'cd {root}; {cmd}'.format(root=args.wsgi_root, cmd=gunicorn_command)
    )
    os.system('service nginx restart')


def main():
    arg_list = collections.OrderedDict((
        ('type', ('WSGI ptoject type',)),
        ('name', ('name of site',)),
    ))
    opt_arg_list = collections.OrderedDict((
        ('bind_to', ('port to bind Gunicorn', '8001')),
        ('wsgi_root', (
            'where Gunicorn loads your WSGI module',
            lambda args: get_formula(args.type, args.name).get_wsgi_env()[0]
        )),
        ('wsgi_path', (
            'path Gunicorn uses to import the WSGI module',
            lambda args: get_formula(args.type, args.name).get_wsgi_env()[1]
        ))
    ))
    args = parse_args(arg_list, opt_arg_list)

    formula = get_formula(args.type, args.name)

    # Fill the WSGI info first (don't prompt the user; just use default values)
    wsgi_env = formula.get_wsgi_env()
    if args.wsgi_root is None:
        args.wsgi_root = wsgi_env[0]
    if args.wsgi_path is None:
        args.wsgi_path = wsgi_env[1]

    # Prompt for some other needed fields
    args = fill_opt_args(args, opt_arg_list)

    # Establish environment
    env.pip = os.path.join(env.virtualenv_root, args.name, 'bin', 'pip')

    # Start setup
    setup(formula, args)


if __name__ == '__main__':
    main()
