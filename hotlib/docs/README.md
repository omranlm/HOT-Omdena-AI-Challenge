# Documentation of hotlib with Sphinx

[Sphinx](https://www.sphinx-doc.org/) is a python library for generating documentation based on docstrings.

## Installation of Sphinx into the conda environment 'hot'

```console
   activate hot
   conda install sphinx
   pip install sphinx_rtd_theme
```

## Generation of HTML documentation for the hotlib library

```console
   cd hotlib/docs
   sphinx-build -b html source build
```

## Generation of LaTeX/PDF documentation for the hotlib library

```console
   cd hotlib/docs
   sphinx-build -M latexpdf source build
```
