# What is Jupynotex?

A Jupyter Notebook to LaTeX translator to include whole or partial notebooks in your papers.

# How To Use?

All you need to do is include the `jupynotex.py` and `jupynotex.sty` files in your LaTeX project, and start using it.


## Example

Check the example directory in this project.

There you will find an example `notebook.ipynb`, an `example.tex` file that includes cells from that notebook in different ways, and a `build` script.

Play with it. Enjoy.


# Dependencies

You need Python 3 in your system, and the [tcolorbox](https://ctan.org/pkg/tcolorbox) module in your LaTeX toolbox.


# Feedback & Development

Please open any issue [here](https://github.com/facundobatista/jupynotex/issues/new).

To run the tests (need to have [fades](https://github.com/pyar/fades) installed):
    
    ./tests/run
