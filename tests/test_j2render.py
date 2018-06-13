import os
import sys
from copy import deepcopy

import jinja2
import pytest

TESTS_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.abspath(os.path.join(TESTS_DIR, '..'))
sys.path.insert(0, PROJECT_DIR)

SAMPLE_DATA = {
    "greeting": "Hello",
    "subject": "World",
    "inner": {
        "prop1": "alpha",
        "prop2": "beta",
        "prop3": "gamma",
        "prop4": "delta",
        "prop5": "epsilon"
    }
}


def test__merge():
    from j2render import _merge
    defaults = deepcopy(SAMPLE_DATA)
    overrides = {
        'greeting': 'Goodbye',
        'inner': {
            'prop1': 'ALPHA'
        },
    }
    expected = {
        "greeting": "Goodbye",
        "subject": "World",
        "inner": {
            "prop1": "ALPHA",
            "prop2": "beta",
            "prop3": "gamma",
            "prop4": "delta",
            "prop5": "epsilon"
        }
    }
    merged = dict(_merge(defaults, overrides))
    assert merged == expected


def test__update():
    from j2render import _update
    from munch import munchify
    data = munchify(deepcopy(SAMPLE_DATA))
    _update(data, 'greeting=Goodbye')
    assert data.greeting == 'Goodbye'
    _update(data, 'inner.prop1=ALPHA')
    assert data.inner.prop1 == 'ALPHA'


def test__get_file_format():
    from j2render import _get_file_format
    assert _get_file_format('/some/file.json') == 'json'
    assert _get_file_format('/some/file.JSON') == 'json'
    assert _get_file_format('/some/file.toml') == 'toml'
    assert _get_file_format('/some/file.TOML') == 'toml'
    assert _get_file_format('/some/file.yaml') == 'yaml'
    assert _get_file_format('/some/file.yml') == 'yaml'
    assert _get_file_format('/some/file.ymal') is None


def test__load_variables_from_module():
    from j2render import _load_variables_from_module
    expected = {
        "greeting": "Hello",
        "subject": "World",
        "inner": {
            "prop1": "alpha",
            "prop2": "beta",
            "prop3": "gamma",
            "prop4": "delta",
            "prop5": "epsilon"
        }
    }
    loaded = _load_variables_from_module('demo.demo:config')
    assert loaded == expected
    with pytest.raises(RuntimeError):
        _load_variables_from_module('demo.notdemo:config')
    with pytest.raises(RuntimeError):
        _load_variables_from_module('demo.demo:notconfig')


def test__load_variables_from_data_file():
    from j2render import _load_variables_from_data_file
    expected = {
        "greeting": "Hello",
        "subject": "World",
        "inner": {
            "prop1": "alpha",
            "prop2": "beta",
            "prop3": "gamma",
            "prop4": "delta",
            "prop5": "epsilon"
        }
    }
    for path in ['demo/demo.json', 'demo/demo.toml', 'demo/demo.yaml']:
        loaded = _load_variables_from_data_file(path)
        assert loaded == expected
    with pytest.raises(RuntimeError):
        _load_variables_from_data_file('/demo/demo.txt')


def test__load_template():
    from j2render import _load_template
    loaded = _load_template('demo/demo.j2')
    assert isinstance(loaded, jinja2.Template)
    with pytest.raises(RuntimeError):
        _load_template('demo/demo')


def test__find_data_file():
    from j2render import _find_data_file
    assert _find_data_file('demo/demo.j2') == os.path.abspath('demo/demo.json')
