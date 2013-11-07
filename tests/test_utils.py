#!/usr/bin/env python
# coding: utf-8

import os.path
from nose.tools import ok_, raises
from pywebstack.formulae import Formula
from pywebstack import utils


ALL_FORMULAE_NAMES = (
    'django', 'Django'
)


def test_normalize():
    ok_(utils.normalize('..', 'test_utils.py'), __file__)


def test_chdir():
    current = os.getcwd()
    outer = os.path.abspath(utils.normalize(current, '..'))
    with utils.chdir('..'):
        ok_(os.getcwd(), outer)
    ok_(os.getcwd(), current)


def test_get_formula_class():
    for name in ALL_FORMULAE_NAMES:
        ok_(issubclass(utils.get_formula_class(name), Formula))


@raises(utils.UnrecognizedFormulaError)
def test_get_formula_class_fail():
    utils.get_formula_class('rails')


def test_get_formula():
    for name in ALL_FORMULAE_NAMES:
        formula = utils.get_formula(name, 'test_project')
        ok_(isinstance(formula, Formula))


if __name__ == '__main__':
    import nose
    nose.run(argv=[__file__, '--with-doctest', '-vv'])
