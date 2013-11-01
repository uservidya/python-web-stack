#!/usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
import collections
import contextlib
import importlib
from .formulae import Formula


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
env.startup_script_prefix = 'pywebstack_'
env.pip = None      # Path to virtualenv pip. Provided at runtime in main()


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


def pip_install(*cmd):
    """Run ``pip install`` on the currently active virtualenv"""
    os.system(env.pip + ' install ' + ' '.join(cmd))


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
    module_name = formula_name.lower()

    try:
        module = importlib.import_module(
            'pywebstack.formulae.{name}'.format(name=module_name)
        )
        for name in reversed(dir(module)):
            if name.lower() == module_name:
                klass = getattr(module, name)
                if issubclass(klass, Formula) and klass is not Formula:
                    return klass
    except (ImportError, AttributeError):
        pass    # Go to exception at the bottom

    raise UnrecognizedFormulaError(
        'Unrecognized formula: {name}'.format(name=formula_name)
    )


def get_formula(formula_name, project_name):
    klass = get_formula_class(formula_name)
    return klass(env, project_name)


class UnrecognizedFormulaError(Exception):
    pass
