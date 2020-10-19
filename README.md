# What is Jupynotex?

A Jupyter Notebook to LaTeX translator to include whole or partial notebooks in your papers.

# How To Use?

All you need to do is include the `jupynotex.py` and `jupynotex.sty` files in your LaTeX project, and use the package from your any of your `.tex` files:

    \usepackage{jupynotex}

After that, you can include a whole Jupyter Notebook in your file just specifying it's file name:

    \jupynotex{file_name_for_your_notebook.ipynb}

If you do not want to include it completely, you can optionally specify which cells:

    \jupynotex[<which cells>]{sample.ipynb}

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


## Full Example

Check the `example` directory in this project.

There you will find an example `notebook.ipynb`, an `example.tex` file that includes cells from that notebook in different ways, and a `build` script.

Play with it. Enjoy.


# Dependencies

You need Python 3 in your system, and the [tcolorbox](https://ctan.org/pkg/tcolorbox) module in your LaTeX toolbox.


# Feedback & Development

Please open any issue or ask any question [here](https://github.com/facundobatista/jupynotex/issues/new).

To run the tests (need to have [fades](https://github.com/pyar/fades) installed):
    
    ./tests/run

This material is subject to the Apache 2.0 license.
