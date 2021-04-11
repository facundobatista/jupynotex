# Copyright 2020-2021 Facundo Batista
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

from jupynotex import Notebook, HIGHLIGHTERS


@pytest.fixture
def notebook():
    _, name = tempfile.mkstemp()

    def _f(cells, lang_name=None):
        fake_nb = {
            'cells': cells,
            'metadata': {
                'language_info': {'name': lang_name},
            },
        }
        with open(name, 'wt', encoding='utf8') as fh:
            json.dump(fake_nb, fh)

        return Notebook(name)

    yield _f
    os.unlink(name)


def test_empty(notebook):
    nb = notebook([])
    assert len(nb) == 0


def test_source_code_simple(notebook):
    rawcell = {
        'cell_type': 'code',
        'source': ['line1\n', '    line2\n'],
    }
    nb = notebook([rawcell])
    assert len(nb) == 1

    src, _ = nb.get(1)
    expected = textwrap.dedent("""\
        \\begin{footnotesize}
        \\begin{verbatim}
        line1
            line2
        \\end{verbatim}
        \\end{footnotesize}
    """)
    assert src == expected


def test_source_code_highlighted(notebook, monkeypatch):
    monkeypatch.setitem(HIGHLIGHTERS, 'testlang', (['highlight start'], ['highlight end']))
    rawcell = {
        'cell_type': 'code',
        'source': ['line1\n', '    line2\n'],
    }
    nb = notebook([rawcell], lang_name='testlang')
    assert len(nb) == 1

    src, _ = nb.get(1)
    expected = textwrap.dedent("""\
        highlight start
        line1
            line2
        highlight end
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
        \\begin{footnotesize}
        \\begin{verbatim}
        default always present
        line2
        \\end{verbatim}
        \\end{footnotesize}
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
    m = re.match(r'\\includegraphics\[width=1\\textwidth\]\{(.+)\}\n', out)
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
        \\begin{footnotesize}
        \\begin{verbatim}
        some text line
        text 2
        \\end{verbatim}
        \\end{footnotesize}
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
    m = re.match(r'\\includegraphics\[width=1\\textwidth\]\{(.+)\}\n', out)
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
        \\begin{footnotesize}
        \\begin{verbatim}
        some text line
        text 2
        \\end{verbatim}
        \\end{footnotesize}
    """)
    assert out == expected


def test_output_error(notebook):
    rawcell = {
        'cell_type': 'code',
        'source': [],
        'outputs': [
            {
                'ename': 'ValueError',
                'evalue': 'not enough values to unpack (expected 3, got 2)',
                'output_type': 'error',
                'traceback': [
                    '\x1b[0;31m------------------------------------------------------\x1b[0m',
                    '\x1b[0;31mValueError\x1b[0m           Traceback (most recent call last)',
                    ('\x1b[0;32m<ipython-input-8-9dbc59cfd6c6>\x1b[0m in '
                        '\x1b[1;36m<module>\x1b[0;34m\x1b[0m\n\x1b[0;32m----> '
                        '1\x1b[0;31m \x1b[0ma\x1b[0m\x1b[0;34m,\x1b[0m '
                        '\x1b[0mb\x1b[0m\x1b[0;34m,\x1b[0m \x1b[0mc\x1b[0m '
                        '\x1b[1;34m=\x1b[0m \x1b[0;36m1\x1b[0m\x1b[0;34m,\x1b[0m '
                        '\x1b[0;36m2\x1b[0m\x1b[0;34m\x1b[0m\x1b[0;34m\x1b[0m\x1b[0m\n\x1b[0m'),
                    '\x1b[0;31mValueError\x1b[0m: not enough values to unpack (expected 3, got 2)',
                ]
            },
        ],
    }
    nb = notebook([rawcell])
    assert len(nb) == 1

    _, out = nb.get(1)
    expected = textwrap.dedent("""\
        \\begin{footnotesize}
        \\begin{verbatim}
        ValueError           Traceback (most recent call last)
        <ipython-input-8-9dbc59cfd6c6> in <module>
        ----> 1 a, b, c = 1, 2

        ValueError: not enough values to unpack (expected 3, got 2)
        \\end{verbatim}
        \\end{footnotesize}
    """)
    assert out == expected
