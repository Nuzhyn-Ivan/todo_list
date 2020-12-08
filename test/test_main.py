import pytest


def setup_module(module):
    # init_something()
    pass


def teardown_module(module):
    # teardown_something()
    pass


def test_upper():
    assert 'foo'.upper() == 'FOO'