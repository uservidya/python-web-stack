#!/usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
import collections
import contextlib


try:
    input = raw_input
except AttributeError:  # No raw_input means we're in Python 3. Good! :)
    pass


class Environment(object):
    pass


# Some constants
env = Environment()
env.virtualenv_root = os.path.join(os.path.dirname(__file__), '..', 'envs')
env.project_container_name = 'project'
env.project_config_file_name = '.pywebstack.conf'


@contextlib.contextmanager
def chdir(dirname):
    """Context manager for changing the current working directory temporarily
    """
    cwd = os.getcwd()
    try:
        os.chdir(dirname)
        yield
    except:
        os.chdir(cwd)
        raise
    else:
        os.chdir(cwd)


def prompt(msg, default=None):
    """Simple input() wrapper with default value

    Decorates :msg with a default value hint, and coerse the input value with
    the default value (`None` if the user does not prvide one).
    """
    if default:
        msg = '{msg} [{default}]'.format(msg=msg, default=default)
    return input(msg + ': ') or default or None


def parse_args(arg_list=None, opt_arg_list=None):
    """Parse command line arguments with argparse"""
    parser = argparse.ArgumentParser()
    if arg_list:
        for arg_name in arg_list:
            parser.add_argument(
                arg_name, help=arg_list[arg_name][0]
            )
    if opt_arg_list:
        for arg_name in opt_arg_list:
            parser.add_argument(
                '--' + arg_name, default=None, help=opt_arg_list[arg_name][0]
            )
    return parser.parse_args()


def fill_opt_args(args, opt_arg_list):
    """Fill the optional arguments by prompting user for input"""
    for arg_name in opt_arg_list:
        if getattr(args, arg_name, None) is None:
            try:
                default = opt_arg_list[arg_name][1]
            except IndexError:
                default = None
            if isinstance(default, collections.Callable):
                default = default(args)
            result = prompt('Specify ' + opt_arg_list[arg_name][0], default)
            if result is None:
                sys.exit('You need to provide value for ' + arg_name)
            setattr(args, arg_name, result)
    return args


def get_formula_class(formula_name):
    name = formula_name.lower()

    if name == 'django':
        from .formulae.django import Django
        return Django

    raise UnrecognizedFormulaError(
        'Unrecognized formula: {name}'.format(formula_name)
    )


def get_formula(formula_name, *args, **kwargs):
    klass = get_formula_class(formula_name)
    return klass(*args, **kwargs)


class UnrecognizedFormulaError(Exception):
    pass
