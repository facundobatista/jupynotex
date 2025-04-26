# What is Jupynotex?

A Jupyter Notebook to LaTeX translator to include whole or partial notebooks in your papers.

## Wait, what?

A TeX package that you can use in your project to include Jupyter Notebooks (all of them, or some specific cells) as part of your text.

It will convert the Jupyter Notebook format to proper LaTeX so it gets included seamless, supporting text, latex, images, etc.


# How To Use?

All you need to do is include the `jupynotex.py` and `jupynotex.sty` files in your LaTeX project, and use the package from your any of your `.tex` files:

    `\usepackage{jupynotex}`

After that, you can include a whole Jupyter Notebook in your file just specifying it's file name:

    `\jupynotex{file_name_for_your_notebook.ipynb}`

If you do not want to include it completely, you can optionally specify which cells:

    `\jupynotex[<which cells>]{sample.ipynb}`

The cells specification can be numbers separated by comma, or ranges using dashes (defaulting to first and last if any side is not included).

Examples:

- include the whole *foobar* notebook:

    `\jupynotex{foobar.ipynb}`

- include just the cell #7:

    `\jupynotex[7]{sample.ipynb}`

- include cells 1, 3, and 6, 7, and 8 from the range:

    `\jupynotex[1,3,6-8]{sample.ipynb}`

- include everything up to the fourth cell, and the eigth:

    `\jupynotex[-4,8]{whatever.ipynb}`

- include the cell number 3, and from 12 to the notebook's end

    `\jupynotex[3,12-]{somenote.ipynb}`

If the cell number or the range ends with an `i` or an `o` it will only show the input or output, correspondingly. E.g.:

- include cell 1 completely, only the input of cell 2, and cells 3 and 4

    `\jupynotex[1,2i,3-4]{sample.ipynb}`

- include cell 3 completely, and outputs of 5, 6, and 7

    `\jupynotex[3,5-7o]{sample.ipynb}`


## Configurations available

The whole package can be configured when included in your project:

    \usepackage[OPTIONS]{jupynotex}

Global options available:

- `output-text-limit=N` where N is a number; it will wrap all outputs that exceed that quantity of columns
- `cells-id-template=TPL`: Where TPL is a template to build the title of each cell using Python's format syntax; available variables are 'number' and 'filename', it defaults to `Cell {number:02d}`
- `first-cell-id-template=TPL`: Same than `cells-id-template` but only applies to the first cell of each file; it defaults to the value of `cells-id-template`

A note regarding these configurations per project: as they use Python's format syntax, it may get weird with curly braces, which you must use for LaTeX to respect spaces and other characters. E.g., see this config that changes the title of all cells to just the number using three digits surrounded by dots, see how there is the `{}` for latex to delimit the whole value of the config variable, and the `{}` inside for Python formatting:

    \usepackage[cells-id-template={...{number:03d}...}]{jupynotex}

Also, each cell(s) can be configured when included in your .tex files:

    \jupynotex[3, OPTIONS]{yournotebook.ipynb}

Cell options available:

- `output-image-size=SIZE` where SIZE is a valid .tex size (a number with an unit, e.g. `70mm`); it will set any image in the output of those cells to the indicated size


## Full Example

Check the `example` directory in this project.

There you will find different notebook examples and `.tex` files using them. Also there's a build script to easily run on any of the examples, like:

    ./build cell_ranges.tex

Play with it. Enjoy.


# Supported cell types

Jupyter has several types of cells, `jupynotex` supports most of those. If you find one that is not supported, please open an issue with an example.

In any case, only the "code" cells are included when processing a notebook (no markdown titles, for example, to make it easy for the developer to find the numbers of cells to include).

Supported cell types in the output:

- `execute_result`: this may have multiple types of information inside; if an image is present, it will be included, otherwise if a latex output is present it will included (directly, so the latex is really parsed later by the LaTeX system, else the plain text will be included (verbatim).

- `stream`: the different text lines will be included (verbatim)
                result.extend(_verbatimize(x.rstrip() for x in item["text"]))

- `display_data`: the image will be included

- `error`: in this case the Traceback will be parsed, sanitized and included in the output keeping its structure (verbatim)

Two type of images are currently supported (for the case in `execute_result` or `display_data` cell type:

- PNG: used directly

- SVG: converted to PDF (need to have `inkscape` present in the system) and included that


# Dependencies

You need Python 3 in your system, and the following modules in your LaTeX toolbox:

- [tcolorbox](https://ctan.org/pkg/tcolorbox)

- [minted](https://www.ctan.org/pkg/minted)

To support SVG images in the notebook, [inkscape](https://inkscape.org/) needs to be installed and in the system's PATH.


# Feedback & Development

Please open any issue or ask any question [here](https://github.com/facundobatista/jupynotex/issues/new).

To run the tests (need to have [fades](https://github.com/pyar/fades) installed):

    ./tests/run

This material is subject to the Apache 2.0 license.
