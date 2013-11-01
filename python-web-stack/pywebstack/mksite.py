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


def activate_virtualenv(args):
    activate_script = os.path.join(
        env.virtualenv_root, args.name, 'bin', 'activate_this.py'
    )
    exec(open(activate_script).read()) in {'__file__': activate_script}


def setup(args):
    config = ConfigParser()
    config.add_section('Project')
    config.set('Project', 'type', args.type)

    formula = get_formula(args.type, args.name)

    # Run environment setup
    make_virtualenv(args)
    activate_virtualenv(args)
    pip_install('gunicorn')

    # Formula-specific setup
    formula.setup()

    # Secretly put the config file inside virtualenv to store project info
    with chdir(os.path.join(env.virtualenv_root, args.name)):
        with open(env.project_config_file_name, 'w+') as f:
            config.write(f)

    # Setup nginx
    pass

    # (Re-)starts the server
    path, wsgi_module = formula.get_wsgi_env()
    with chdir(path):
        os.system('gunicorn {module} --pid gunicorn.pid --daemon'.format(
            module=wsgi_module
        ))
    # TODO: Write this command to /etc/init.d?


def main():
    arg_list = collections.OrderedDict((
        ('type', ('WSGI ptoject type',)),
        ('name', ('name of site',)),
    ))
    opt_arg_list = collections.OrderedDict((
        ('db_name', ('name of the database', lambda args: args.name)),
        ('db_owner', ('owner of the database', lambda args: args.name)),
    ))
    args = parse_args(arg_list, opt_arg_list)
    args = fill_opt_args(args, opt_arg_list)

    env.pip = os.path.join(env.virtualenv_root, args.name, 'bin', 'pip')
    setup(args)


if __name__ == '__main__':
    main()
