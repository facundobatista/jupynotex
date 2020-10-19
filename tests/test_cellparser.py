# Copyright 2020 Facundo Batista
# All Rights Reserved
# Licensed under Apache 2.0

import pytest
import re

from jupynotex import _parse_cells


def test_empty():
    msg = "Empty cells spec not allowed"
    with pytest.raises(ValueError, match=re.escape(msg)):
        _parse_cells('', 100)


def test_simple():
    r = _parse_cells('1', 100)
    assert r == [1]


def test_several_comma():
    r = _parse_cells('1,3,5,9,7', 100)
    assert r == [1, 3, 5, 7, 9]


def test_several_range():
    r = _parse_cells('1-9', 100)
    assert r == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_several_limited():
    msg = "Notebook loaded of len 3, smaller than requested cells: [1, 2, 3, 4]"
    with pytest.raises(ValueError, match=re.escape(msg)):
        _parse_cells('1-4', 3)


def test_range_default_start():
    r = _parse_cells('-3', 8)
    assert r == [1, 2, 3]


def test_range_default_end():
    r = _parse_cells('5-', 8)
    assert r == [5, 6, 7, 8]


def test_not_int():
    msg = "Found forbidden characters in cells definition (allowed digits, '-' and ',')"
    with pytest.raises(ValueError, match=re.escape(msg)):
        _parse_cells('1,a', 3)


def test_not_positive():
    msg = "Cells need to be >=1"
    with pytest.raises(ValueError, match=re.escape(msg)):
        _parse_cells('3,0', 3)


def test_several_mixed():
    r = _parse_cells('1,3,5-7,2,9,11-13', 80)
    assert r == [1, 2, 3, 5, 6, 7, 9, 11, 12, 13]


def test_overlapped():
    r = _parse_cells('3,5-7,6-9,8', 80)
    assert r == [3, 5, 6, 7, 8, 9]


def test_bad_range_equal():
    msg = "Range 'from' need to be smaller than 'to' (got '12-12')"
    with pytest.raises(ValueError, match=re.escape(msg)):
        _parse_cells('12-12', 80)


def test_bad_range_smaller():
    msg = "Range 'from' need to be smaller than 'to' (got '3-2')"
    with pytest.raises(ValueError, match=re.escape(msg)):
        _parse_cells('3-2', 80)
