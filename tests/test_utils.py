#!/usr/bin/env python
# coding: utf-8

from nose.tools import ok_, raises
from pywebstack.formulae import Formula
from pywebstack import utils


ALL_FORMULAE_NAMES = (
    'django', 'Django'
)


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
