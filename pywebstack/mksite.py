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
    chdir, parse_args, fill_opt_args, env, get_formula, run, pip_install,
    reload_nginx
)


def make_virtualenv(args):
    name = args.name
    print('Making virtualenv {name}...'.format(name=name))
    with chdir(env.virtualenv_root):
        run('virtualenv -q {name}'.format(name=name), quiet=True)
        with chdir(name):
            os.mkdir(env.project_container_name)


def add_nginx_conf(filename, content):
    available = '/etc/nginx/sites-available'
    enabled = '/etc/nginx/sites-enabled'

    available_filename = os.path.join(available, filename)

    print('Adding nginx configuration at {n}...'.format(n=available_filename))
    with open(available_filename, 'w') as f:
        f.write(content)

    print('Linking {filename} as enabled...'.format(filename=filename))
    with chdir(enabled):
        if os.path.exists(filename):
            os.remove(filename)
        os.symlink(available_filename, filename)


def add_startup_conf(filename, content):
    path = '/etc/init.d'

    print('Adding app server to startup script...')
    with chdir(path):
        with open(filename, 'w') as f:
            f.write(content)


def setup(formula, args):
    config = ConfigParser()
    config.add_section('Project')
    config.set('Project', 'type', args.type)

    # Run environment setup
    make_virtualenv(args)
    pip_install('uwsgi')

    # Formula-specific setup
    formula.setup()

    current_virtualenv = os.path.join(env.virtualenv_root, args.name)

    # Secretly put the config file inside virtualenv to store project info
    with chdir(current_virtualenv):
        with open(env.project_config_file_name, 'w+') as f:
            config.write(f)

    # Setup nginx
    add_nginx_conf(args.name, formula.get_nginx_conf(args))

    # Setup uWSGI
    ini_file = os.path.join(formula.containing_dir, 'uwsgi.ini')
    pid_file = os.path.join(formula.containing_dir, 'uwsgi.pid')
    log_file = os.path.join(formula.containing_dir, 'uwsgi.log')
    with open(ini_file, 'w') as f:
        f.write(formula.get_uwsgi_conf(
            args, pid_file=pid_file, log_file=log_file
        ))

    uwsgi = os.path.join(current_virtualenv, 'bin', 'uwsgi')
    cmd_args = (
        '--master', '--vacuum', '--uid={uid}', '--gid={gid}'
    )
    cmd = '{uwsgi} --ini {ini_file} {cmd_args}'.format(
        uwsgi=uwsgi, ini_file=ini_file, cmd_args=' '.join(cmd_args),
        uid=args.uid, gid=args.gid
    )
    print('Starting daemon...')
    run(cmd)

    add_startup_conf(env.startup_script_prefix + args.name, cmd)
    reload_nginx()


def main():
    arg_list = collections.OrderedDict((
        ('type', ('WSGI ptoject type',)),
        ('name', ('name of site',)),
    ))
    opt_arg_list = collections.OrderedDict((
        ('bind_to', ('port to bind the app server', '8001')),
        ('server_root', ('root URL of the web server', '/')),
        ('wsgi_root', (
            'where the app server starts loading your WSGI module',
            lambda args: get_formula(args.type, args.name).get_wsgi_env()[0]
        )),
        ('wsgi_path', (
            'Python path used by the app server to import the WSGI module',
            lambda args: get_formula(args.type, args.name).get_wsgi_env()[1]
        )),
        ('uid', ('User ID for uWSGI worker', '1000')),
        ('gid', ('Group ID for uWSGI worker', '2000')),
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

    # Be sensitive and fix leading and trailing slashes
    if not args.server_root.endswith('/'):
        args.server_root = args.server_root + '/'
    if not args.server_root.startswith('/'):
        args.server_root = '/' + args.server_root

    # Establish environment
    env.pip = os.path.join(env.virtualenv_root, args.name, 'bin', 'pip')

    # Start setup
    setup(formula, args)


if __name__ == '__main__':
    main()
