#!/usr/bin/env python
# -*- coding: utf-8

from __future__ import print_function
import os.path
import collections
import shutil
from .utils import parse_args, chdir, env, get_formula


def rm_virtualenv(name):
    with chdir(env.virtualenv_root):
        shutil.rmtree(name)


def main():
    arg_list = collections.OrderedDict((
        ('name', 'name of site to remove'),
    ))
    args = parse_args(arg_list=arg_list)

    formula_type = None
    with chdir(os.path.join(env.virtualenv_root, args.name)):
        with open(env.project_config_file_name, 'r') as f:
            formula_type = f.readline().strip()
    formula = get_formula(formula_type, args.name)
    formula.pre_teardown()
    formula.teardown()
    formula.post_teardown()
    rm_virtualenv(args.name)


if __name__ == '__main__':
    main()
