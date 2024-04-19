# Copyright 2020-2024 Facundo Batista
# All Rights Reserved
# Licensed under Apache 2.0

import json
import textwrap
from unittest.mock import patch

import pytest

import jupynotex
from jupynotex import main, Notebook, CMDLINE_OPTION_NAMES


class FakeNotebook:
    """Fake notebook.

    The instance supports calling (as it if were instantiated). The .get will return the
    value in a dict for received key; raise it if exception.
    """

    def __init__(self, side_effects):
        self.side_effects = side_effects

    def __call__(self, path, config_options):
        return self

    def __len__(self):
        return len(self.side_effects)

    def parse_cells(self, spec):
        return self.side_effects.values()

    def get(self, key, options):
        """Return or raise the stored side effect."""
        value = self.side_effects[key]
        if isinstance(value, Exception):
            raise value
        else:
            return value


@pytest.fixture
def save_notebook(monkeypatch, tmp_path):
    monkeypatch.setattr(jupynotex, "HIGHLIGHTERS", {None: ([], [])})
    monkeypatch.setattr(jupynotex, "VERBATIM_BEGIN", [])
    monkeypatch.setattr(jupynotex, "VERBATIM_END", [])
    monkeypatch.setattr(jupynotex, 'FORMAT_OK', 'testformat')

    name = tmp_path / "testnotebook.ipynb"

    def _f(contents):
        cells = []
        for src, out in contents:
            cell = {
                'cell_type': 'code',
                'source': [src],
                'outputs': [
                    {
                        'output_type': 'execute_result',
                        'data': {
                            'text/plain': [out],
                        },
                    },
                ]
            }
            cells.append(cell)

        fake_nb = {
            'cells': cells,
            'metadata': {
                'language_info': {'name': None},
            },
        }
        with open(name, 'wt', encoding='utf8') as fh:
            json.dump(fake_nb, fh)

        return name

    yield _f


def test_simple_ok(capsys, save_notebook):
    notebook_path = save_notebook([
        ("test cell content up", "test cell content down"),
    ])

    empty_config = {key: "" for key in CMDLINE_OPTION_NAMES}
    main(notebook_path, '1', empty_config)
    expected = textwrap.dedent("""\
        \\begin{tcolorbox}[testformat, title=Cell {01}]
        test cell content up
        \\tcblower
        test cell content down
        \\end{tcolorbox}
    """)
    assert expected == capsys.readouterr().out


def test_simple_only_first(capsys, save_notebook):
    notebook_path = save_notebook([
        ("test cell content up", ""),
    ])

    main(notebook_path, '1', {})

    expected = textwrap.dedent("""\
        \\begin{tcolorbox}[testformat, title=Cell {01}]
        test cell content up
        \\end{tcolorbox}
    """)
    assert expected == capsys.readouterr().out


def test_simple_error(monkeypatch, capsys, save_notebook):
    notebook_path = save_notebook([("foo", "bar")])
    monkeypatch.setattr(jupynotex, 'FORMAT_ERROR', 'testformat')

    with patch.object(Notebook, "get", side_effect=ValueError("test problem")):
        main(notebook_path, '1', {})

    # verify the beginning and the end, as the middle part is specific to the environment
    # where the test runs
    expected_ini = [
        r"\begin{tcolorbox}[testformat, title={ERROR when parsing cell 1}]",
        r"Traceback (most recent call last):",
    ]
    expected_end = [
        r"ValueError: test problem",
        r"\end{tcolorbox}",
    ]
    out = [line for line in capsys.readouterr().out.split('\n') if line]
    assert expected_ini == out[:2]
    assert expected_end == out[-2:]


def test_multiple(capsys, save_notebook):
    notebook_path = save_notebook([
        ("test cell content up", "test cell content down"),
        ("test cell content ONLY up", ""),
    ])

    main(notebook_path, '1-2', {})
    expected = textwrap.dedent("""\
        \\begin{tcolorbox}[testformat, title=Cell {01}]
        test cell content up
        \\tcblower
        test cell content down
        \\end{tcolorbox}
        \\begin{tcolorbox}[testformat, title=Cell {02}]
        test cell content ONLY up
        \\end{tcolorbox}
    """)
    assert expected == capsys.readouterr().out
