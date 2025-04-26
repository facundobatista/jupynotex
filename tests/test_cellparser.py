# Copyright 2020-2024 Facundo Batista
# All Rights Reserved
# Licensed under Apache 2.0

import pathlib
import re

import pytest

from jupynotex import Notebook, CellSelection


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
    assert result == [CellSelection(1)]
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
    assert result == [CellSelection(x) for x in (1, 3, 5, 7, 9)]
    assert notebook.cell_options == {}


def test_several_range(notebook):
    result = notebook.parse_cells('1-9')
    assert result == [CellSelection(x) for x in (1, 2, 3, 4, 5, 6, 7, 8, 9)]
    assert notebook.cell_options == {}


def test_several_limited(notebook):
    notebook._cells[:] = notebook._cells[:3]
    msg = "Notebook loaded of len 3, smaller than requested cells"
    with pytest.raises(ValueError, match=re.escape(msg)):
        notebook.parse_cells('1-4')


def test_range_default_start(notebook):
    result = notebook.parse_cells('-3')
    assert result == [CellSelection(x) for x in (1, 2, 3)]
    assert notebook.cell_options == {}


def test_range_default_end(notebook):
    notebook._cells[:] = notebook._cells[:8]
    result = notebook.parse_cells('5-')
    assert result == [CellSelection(x) for x in (5, 6, 7, 8)]
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
    assert result == [CellSelection(x) for x in (1, 2, 3, 5, 6, 7, 9, 11, 12, 13)]
    assert notebook.cell_options == {}


def test_overlapped(notebook):
    result = notebook.parse_cells('3,5-7,6-9,8')
    assert result == [CellSelection(x) for x in (3, 5, 6, 7, 8, 9)]
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
    assert result == [CellSelection(7)]
    assert notebook.cell_options == {"foo": "23"}


def test_with_option_multiple(notebook):
    result = notebook.parse_cells('7-9, foo=23, 12, bar=baz')
    assert result == [CellSelection(x) for x in (7, 8, 9, 12)]
    assert notebook.cell_options == {"foo": "23", "bar": "baz"}


def test_partial_input_one_alone(notebook):
    result = notebook.parse_cells('7i')
    assert result == [CellSelection(7, partial="i")]
    assert notebook.cell_options == {}


def test_partial_input_one_range(notebook):
    result = notebook.parse_cells('1-3i')
    assert result == [CellSelection(x, partial="i") for x in (1, 2, 3)]
    assert notebook.cell_options == {}


def test_partial_input_one_mixed(notebook):
    result = notebook.parse_cells('1, 2i, 3-5, 6-7i')
    assert result == [
        CellSelection(1),
        CellSelection(2, partial="i"),
        CellSelection(3),
        CellSelection(4),
        CellSelection(5),
        CellSelection(6, partial="i"),
        CellSelection(7, partial="i"),
    ]
    assert notebook.cell_options == {}


def test_partial_output_one_alone(notebook):
    result = notebook.parse_cells('7o')
    assert result == [CellSelection(7, partial="o")]
    assert notebook.cell_options == {}


def test_partial_output_one_range(notebook):
    result = notebook.parse_cells('1-3o')
    assert result == [CellSelection(x, partial="o") for x in (1, 2, 3)]
    assert notebook.cell_options == {}


def test_partial_output_one_mixed(notebook):
    result = notebook.parse_cells('1, 2o, 3-5, 6-7o')
    assert result == [
        CellSelection(1),
        CellSelection(2, partial="o"),
        CellSelection(3),
        CellSelection(4),
        CellSelection(5),
        CellSelection(6, partial="o"),
        CellSelection(7, partial="o"),
    ]
    assert notebook.cell_options == {}


@pytest.mark.parametrize("value", [
    "1x",  # invalid letter
    "1I",  # not upper! (I may be confused with 1 or l)
    "1O",  # not upper! (O may be confused with 0)
    "o1",  # not before
    "1-o2",  # not before
    "1o2",  # whatever
    "1o-2",  # not in the middle
    "1,1i"  # mixed complete and partial for same cell
])
def test_partial_invalid_cases(notebook, value):
    with pytest.raises(ValueError):
        notebook.parse_cells(value)


def test_partial_repeated_and_misordered(notebook):
    result = notebook.parse_cells('1, 2i, 3, 2i, 4, 6-7o, 6o')
    assert result == [
        CellSelection(1),
        CellSelection(2, partial="i"),
        CellSelection(3),
        CellSelection(4),
        CellSelection(6, partial="o"),
        CellSelection(7, partial="o"),
    ]
    assert notebook.cell_options == {}
