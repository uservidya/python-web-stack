#!/usr/bin/env python
# -*- coding: utf-8

from __future__ import print_function
import os
import collections
from .utils import chdir, parse_args, fill_opt_args, env, get_formula


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
    # Secretly put a config file inside virtualenv to store project info
    with chdir(os.path.join(env.virtualenv_root, args.name)):
        with open(env.project_config_file_name, 'w+') as f:
            f.write(args.type)

    # Install things we need
    os.system('pip install gunicorn psycopg2')

    # Formula-specific setup
    formula = get_formula(args.type, args.name)
    formula.pre_setup()
    formula.setup()
    formula.post_setup()


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

    make_virtualenv(args)
    activate_virtualenv(args)
    setup(args)


if __name__ == '__main__':
    main()
