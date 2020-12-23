# Copyright 2020 Facundo Batista
# All Rights Reserved
# Licensed under Apache 2.0

import base64
import json
import os
import pathlib
import re
import tempfile
import textwrap

import pytest

from jupynotex import Notebook


@pytest.fixture
def notebook():
    _, name = tempfile.mkstemp()

    def _f(cells):
        with open(name, 'wt', encoding='utf8') as fh:
            json.dump({'cells': cells}, fh)

        return Notebook(name)

    yield _f
    os.unlink(name)


def test_empty(notebook):
    nb = notebook([])
    assert len(nb) == 0


def test_source_code(notebook):
    rawcell = {
        'cell_type': 'code',
        'source': ['line1\n', '    line2\n'],
    }
    nb = notebook([rawcell])
    assert len(nb) == 1

    src, _ = nb.get(1)
    expected = textwrap.dedent("""\
        \\begin{verbatim}
        line1
            line2
        \\end{verbatim}
    """)
    assert src == expected


def test_source_markdown_ignored(notebook):
    rawcell = {
        'cell_type': 'markdown',
        'source': ['line1\n', '    line2\n'],
    }
    nb = notebook([rawcell])
    assert len(nb) == 0


def test_output_missing(notebook):
    rawcell = {
        'cell_type': 'code',
        'source': [],
    }
    nb = notebook([rawcell])
    assert len(nb) == 1

    _, out = nb.get(1)
    assert out is None


def test_output_simple_executeresult_plain(notebook):
    rawcell = {
        'cell_type': 'code',
        'source': [],
        'outputs': [
            {
                'output_type': 'execute_result',
                'data': {
                    'text/plain': ['default always present', 'line2'],
                },
            },
        ],
    }
    nb = notebook([rawcell])
    assert len(nb) == 1

    _, out = nb.get(1)
    expected = textwrap.dedent("""\
        \\begin{verbatim}
        default always present
        line2
        \\end{verbatim}
    """)
    assert out == expected


def test_output_simple_executeresult_latex(notebook):
    rawcell = {
        'cell_type': 'code',
        'source': [],
        'outputs': [
            {
                'output_type': 'execute_result',
                'data': {
                    'text/latex': ['some latex line', 'latex 2'],
                    'text/plain': ['default always present'],
                },
            },
        ],
    }
    nb = notebook([rawcell])
    assert len(nb) == 1

    _, out = nb.get(1)
    expected = textwrap.dedent("""\
        some latex line
        latex 2
    """)
    assert out == expected


def test_output_simple_executeresult_image(notebook):
    raw_content = b"\x01\x02 asdlklda3wudghlaskgdlask"
    rawcell = {
        'cell_type': 'code',
        'source': [],
        'outputs': [
            {
                'output_type': 'execute_result',
                'data': {
                    'image/png': base64.b64encode(raw_content).decode('ascii'),
                    'text/plain': ['default always present'],
                },
            },
        ],
    }
    nb = notebook([rawcell])
    assert len(nb) == 1

    _, out = nb.get(1)
    m = re.match(r'\\includegraphics\{(.+)\}\n', out)
    assert m
    (fpath,) = m.groups()
    assert pathlib.Path(fpath).read_bytes() == raw_content


def test_output_simple_stream(notebook):
    rawcell = {
        'cell_type': 'code',
        'source': [],
        'outputs': [
            {
                'output_type': 'stream',
                'text': ['some text line', 'text 2'],
            },
        ],
    }
    nb = notebook([rawcell])
    assert len(nb) == 1

    _, out = nb.get(1)
    expected = textwrap.dedent("""\
        \\begin{verbatim}
        some text line
        text 2
        \\end{verbatim}
    """)
    assert out == expected


def test_output_simple_display_data(notebook):
    raw_content = b"\x01\x02 asdlklda3wudghlaskgdlask"
    rawcell = {
        'cell_type': 'code',
        'source': [],
        'outputs': [
            {
                'output_type': 'display_data',
                'data': {
                    'image/png': base64.b64encode(raw_content).decode('ascii'),
                },
            },
        ],
    }
    nb = notebook([rawcell])
    assert len(nb) == 1

    _, out = nb.get(1)
    m = re.match(r'\\includegraphics\{(.+)\}\n', out)
    assert m
    (fpath,) = m.groups()
    assert pathlib.Path(fpath).read_bytes() == raw_content


def test_output_multiple(notebook):
    rawcell = {
        'cell_type': 'code',
        'source': [],
        'outputs': [
            {
                'output_type': 'execute_result',
                'data': {
                    'text/latex': ['some latex line', 'latex 2'],
                },
            }, {
                'output_type': 'stream',
                'text': ['some text line', 'text 2'],
            },
        ],
    }
    nb = notebook([rawcell])
    assert len(nb) == 1

    _, out = nb.get(1)
    expected = textwrap.dedent("""\
        some latex line
        latex 2
        \\begin{verbatim}
        some text line
        text 2
        \\end{verbatim}
    """)
    assert out == expected
