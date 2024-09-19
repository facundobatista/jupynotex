# Copyright 2020-2024 Facundo Batista
# All Rights Reserved
# Licensed under Apache 2.0

import pathlib
import re

import pytest

from jupynotex import Notebook


@pytest.fixture
def notebook():
    """Provide a simple notebook."""
    return Notebook(pathlib.Path("tests/example.ipynb"), {})


def test_empty(notebook):
    msg = "Empty cells spec not allowed"
    with pytest.raises(ValueError, match=re.escape(msg)):
        notebook.parse_cells('')


def test_simple(notebook):
    result = notebook.parse_cells('1')
    assert result == [1]
    assert notebook.cell_options == {}


@pytest.mark.parametrize("src", [
    '1,3,5,9,7',
    '  1,3,5,9,7',
    '1,3,5  ,9,7',
    '1,3,  5,9,7',
    '1,3,5,9,7  ',
    ' 1, 3, 5,  9,7  ',
])
def test_several_comma(src, notebook):
    result = notebook.parse_cells(src)
    assert result == [1, 3, 5, 7, 9]
    assert notebook.cell_options == {}


def test_several_range(notebook):
    result = notebook.parse_cells('1-9')
    assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert notebook.cell_options == {}


def test_several_limited(notebook):
    notebook._cells[:] = notebook._cells[:3]
    msg = "Notebook loaded of len 3, smaller than requested cells: [1, 2, 3, 4]"
    with pytest.raises(ValueError, match=re.escape(msg)):
        notebook.parse_cells('1-4')


def test_range_default_start(notebook):
    result = notebook.parse_cells('-3')
    assert result == [1, 2, 3]
    assert notebook.cell_options == {}


def test_range_default_end(notebook):
    notebook._cells[:] = notebook._cells[:8]
    result = notebook.parse_cells('5-')
    assert result == [5, 6, 7, 8]
    assert notebook.cell_options == {}


def test_not_int(notebook):
    msg = "Found forbidden characters in cells definition (allowed digits, '-' and ',')"
    with pytest.raises(ValueError, match=re.escape(msg)):
        notebook.parse_cells('1,a')


def test_not_positive(notebook):
    msg = "Cells need to be >=1"
    with pytest.raises(ValueError, match=re.escape(msg)):
        notebook.parse_cells('3,0')


@pytest.mark.parametrize("src", [
    '1,3,5-7,2,9,11-13',
    '1,3, 5-7,2,9,11-13',
    '1,3,5-7,2, 9 ,11-13',
])
def test_several_mixed(src, notebook):
    result = notebook.parse_cells(src)
    assert result == [1, 2, 3, 5, 6, 7, 9, 11, 12, 13]
    assert notebook.cell_options == {}


def test_overlapped(notebook):
    result = notebook.parse_cells('3,5-7,6-9,8')
    assert result == [3, 5, 6, 7, 8, 9]
    assert notebook.cell_options == {}


def test_bad_range_equal(notebook):
    msg = "Range 'from' need to be smaller than 'to' (got '12-12')"
    with pytest.raises(ValueError, match=re.escape(msg)):
        notebook.parse_cells('12-12')


def test_bad_range_smaller(notebook):
    msg = "Range 'from' need to be smaller than 'to' (got '3-2')"
    with pytest.raises(ValueError, match=re.escape(msg)):
        notebook.parse_cells('3-2')


def test_with_option_simple(notebook):
    result = notebook.parse_cells('7,foo=23')
    assert result == [7]
    assert notebook.cell_options == {"foo": "23"}


def test_with_option_multiple(notebook):
    result = notebook.parse_cells('7-9, foo=23, 12, bar=baz')
    assert result == [7, 8, 9, 12]
    assert notebook.cell_options == {"foo": "23", "bar": "baz"}
