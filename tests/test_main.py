# Copyright 2020 Facundo Batista
# All Rights Reserved
# Licensed under Apache 2.0

import textwrap

import jupynotex
from jupynotex import main


class FakeNotebook:
    """Fake notebook.

    The instance supports calling (as it if were instantiated). The .get will return the
    value in a dict for received key; raise it if exception.
    """

    def __init__(self, side_effects):
        self.side_effects = side_effects

    def __call__(self, path):
        return self

    def __len__(self):
        return len(self.side_effects)

    def get(self, key):
        """Return or raise the stored side effect."""
        value = self.side_effects[key]
        if isinstance(value, Exception):
            raise value
        else:
            return value


def test_simple_ok(monkeypatch, capsys):
    fake_notebook = FakeNotebook({
        1: ("test cell content up", "test cell content down"),
    })
    monkeypatch.setattr(jupynotex, 'Notebook', fake_notebook)
    monkeypatch.setattr(jupynotex, 'FORMAT_OK', 'testformat')

    main('boguspath', '1')
    expected = textwrap.dedent("""\
        \\begin{tcolorbox}[testformat, title=Cell {01}]
        test cell content up
        \\tcblower
        test cell content down
        \\end{tcolorbox}
    """)
    assert expected == capsys.readouterr().out


def test_simple_only_first(monkeypatch, capsys):
    fake_notebook = FakeNotebook({
        1: ("test cell content up", ""),
    })
    monkeypatch.setattr(jupynotex, 'Notebook', fake_notebook)
    monkeypatch.setattr(jupynotex, 'FORMAT_OK', 'testformat')

    main('boguspath', '1')
    expected = textwrap.dedent("""\
        \\begin{tcolorbox}[testformat, title=Cell {01}]
        test cell content up
        \\end{tcolorbox}
    """)
    assert expected == capsys.readouterr().out


def test_simple_error(monkeypatch, capsys):
    fake_notebook = FakeNotebook({
        1: ValueError("test problem"),
    })
    monkeypatch.setattr(jupynotex, 'Notebook', fake_notebook)
    monkeypatch.setattr(jupynotex, 'FORMAT_ERROR', 'testformat')

    main('boguspath', '1')

    # verify the beginning and the end, as the middle part is specific to the environment
    # where the test runs
    expected_ini = [
        r"\begin{tcolorbox}[testformat, title={ERROR when parsing cell 1}]",
        r'\begin{footnotesize}',
        r"\begin{verbatim}",
        r"Traceback (most recent call last):",
    ]
    expected_end = [
        r"ValueError: test problem",
        r"\end{verbatim}",
        r'\end{footnotesize}',
        r"\end{tcolorbox}",
    ]
    out = [line for line in capsys.readouterr().out.split('\n') if line]
    assert expected_ini == out[:4]
    assert expected_end == out[-4:]


def test_multiple(monkeypatch, capsys):
    fake_notebook = FakeNotebook({
        1: ("test cell content up", "test cell content down"),
        2: ("test cell content ONLY up", ""),
    })
    monkeypatch.setattr(jupynotex, 'Notebook', fake_notebook)
    monkeypatch.setattr(jupynotex, 'FORMAT_OK', 'testformat')

    main('boguspath', '1-2')
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
