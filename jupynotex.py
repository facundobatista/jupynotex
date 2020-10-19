# Copyright 2020 Facundo Batista
# All Rights Reserved
# Licensed under Apache 2.0

"""USAGE: jupynote.py notebook.ipynb cells

    cells is a string with which cells to include, separate groups
    with comma, ranges with dash (with defaults to start and end.
"""

import base64
import json
import sys
import tempfile
import traceback


def _verbatimize(lines):
    """Wrap a series of lines around a verbatim indication."""
    result = [r"\begin{verbatim}"]
    for line in lines:
        result.append(line.rstrip())
    result.append(r"\end{verbatim}")
    return result


def _save_content(data):
    """Save the received b64encoded data to a temp file."""
    _, fname = tempfile.mkstemp(suffix='.png')
    with open(fname, 'wb') as fh:
        fh.write(base64.b64decode(data))
    return fname


class Notebook:
    """The notebook converter to latex."""

    def __init__(self, path):
        with open(path, 'rt', encoding='utf8') as fh:
            nb_data = json.load(fh)

        self._cells = nb_data['cells']

    def __len__(self):
        return len(self._cells)

    def _proc_src(self, content):
        """Process the source of a cell."""
        source = content['source']
        result = []
        if content['cell_type'] == 'code':
            result.extend(_verbatimize(source))
        elif content['cell_type'] == 'markdown':
            # XXX: maybe we could parse this?
            result.extend(_verbatimize(source))
        else:
            raise ValueError(
                "Cell type not supported when processing source: {!r}".format(
                    content['cell_type']))

        return '\n'.join(result) + '\n'

    def _proc_out(self, content):
        """Process the output of a cell."""
        outputs = content.get('outputs')
        if not outputs:
            return

        result = []
        for item in outputs:
            output_type = item['output_type']
            if output_type == 'execute_result':
                data = item['data']
                if 'image/png' in data:
                    fname = _save_content(data['image/png'])
                    result.append(r"\includegraphics{{{}}}".format(fname))
                elif 'text/latex' in data:
                    result.extend(data["text/latex"])
                else:
                    result.extend(_verbatimize(data["text/plain"]))
            elif output_type == 'stream':
                result.extend(_verbatimize(x.rstrip() for x in item["text"]))
            elif output_type == 'display_data':
                data = item['data']
                fname = _save_content(data['image/png'])
                result.append(r"\includegraphics{{{}}}".format(fname))
            else:
                raise ValueError("Output type not supported in item {!r}".format(item))

        return '\n'.join(result) + '\n'

    def get(self, cell_idx):
        """Return the content from a specific cell in the notebook.

        The content is already splitted in source and output, and converted to latex.
        """
        content = self._cells[cell_idx - 1]
        source = self._proc_src(content)
        output = self._proc_out(content)
        return source, output


def _parse_cells(spec, maxlen):
    """Convert the cells spec to a range of ints."""
    if not spec:
        raise ValueError("Empty cells spec not allowed")
    if set(spec) - set('0123456789-,'):
        raise ValueError(
            "Found forbidden characters in cells definition (allowed digits, '-' and ',')")

    cells = set()
    groups = spec.split(',')
    for group in groups:
        if '-' in group:
            cfrom, cto = group.split('-')
            cfrom = 1 if cfrom == '' else int(cfrom)
            cto = maxlen if cto == '' else int(cto)
            if cfrom >= cto:
                raise ValueError(
                    "Range 'from' need to be smaller than 'to' (got {!r})".format(group))
            cells.update(range(cfrom, cto + 1))
        else:
            cells.add(int(group))
    cells = sorted(cells)

    if any(x < 1 for x in cells):
        raise ValueError("Cells need to be >=1")
    if maxlen < cells[-1]:
        raise ValueError(
            "Notebook loaded of len {}, smaller than requested cells: {}".format(maxlen, cells))

    return cells


def main(notebook_path, cells_spec):
    """Main entry point."""
    nb = Notebook(notebook_path)
    cells = _parse_cells(cells_spec, len(nb))

    for cell in cells:
        try:
            src, out = nb.get(cell)
        except Exception:
            title = "ERROR when parsing cell {}".format(cell)
            print(
                r"\begin{{tcolorbox}}"
                r"[colback=red!5!white,colframe=red!75!,title={{{}}}]".format(title))
            tb = traceback.format_exc()
            print('\n'.join(_verbatimize(tb.split('\n'))))
            print(r"\end{tcolorbox}")
            continue

        print(r"\begin{{tcolorbox}}[title=Cell {{{:02d}}}]".format(cell))
        print(src)
        if out:
            print(r"\tcblower")
            print(out)
        print(r"\end{tcolorbox}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        exit()

    main(*sys.argv[1:3])
