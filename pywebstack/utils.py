#!/usr/bin/env python
# coding: utf-8

import os
import os.path
import sys
import argparse
import collections
import contextlib
import importlib


try:
    input = raw_input
except AttributeError:  # No raw_input means we're in Python 3. Good! :)
    pass


def normalize(*args):
    """Normalize path relative to pywebstack"""
    return os.path.normpath(os.path.join(os.path.dirname(__file__), *args))


class Environment(object):
    def __init__(self, **attributes):
        for k in attributes:
            setattr(self, k, attributes[k])

env = Environment(
    virtualenv_root=normalize('..', 'envs'),
    template_root=normalize('..', 'templates'),
    project_container_name='project',
    project_config_file_name='.pywebstack.conf',
    startup_script_prefix='pywebstack_',
    pip=None        # Path to virtualenv pip. Provided at runtime in main()
)


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


def run(cmd, quiet=False):
    """Run a command with os.system"""
    if not quiet:
        print('Running {cmd}'.format(cmd=cmd))
    os.system(cmd)


def pip_install(*cmd):
    """Run ``pip install`` on the currently active virtualenv"""
    cmds = ' '.join(cmd)
    print('Running pip install {cmds}'.format(cmds=cmds))
    run(env.pip + ' install -q ' + cmds, quiet=True)


def reload_nginx():
    run('service nginx restart', quiet=True)


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


def fill_opt_args(arg_list, opt_arg_list):
    """Fill the optional arguments by prompting user for input"""
    for arg_name in opt_arg_list:
        if getattr(arg_list, arg_name, None) is None:
            try:
                default = opt_arg_list[arg_name][1]
            except IndexError:
                default = None
            if isinstance(default, collections.Callable):
                default = default(arg_list)
            result = prompt('Specify ' + opt_arg_list[arg_name][0], default)
            if result is None:
                sys.exit('You need to provide value for ' + arg_name)
            setattr(arg_list, arg_name, result)
    return arg_list


def get_formula_class(formula_name):
    module_name = formula_name.lower()
    from .formulae import Formula

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
    return klass(formula_name, env, project_name)


class UnrecognizedFormulaError(Exception):
    pass
