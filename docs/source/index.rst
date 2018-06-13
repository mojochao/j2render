.. _j2render_docs:

=========
j2render
=========

The **j2render** package provides the ``j2render`` command-line interface
(CLI) for rendering `Jinja2 <http://jinja.pocoo.org/docs>`_ templates from data
provided by JSON, TOML and YAML data files, Python modules, and on the command
line to standard output or a file.

Installation
============

Install the **j2render** package from `PyPi <https://pypi.org>`_ with ``pip``::

    $ pip install j2render

Help
====

Use the *--help* option to get help on usage::

    $ j2render --help

Usage
=====

Consider the following template and data files.

demo.j2
-------

..  literalinclude:: ../../demo/demo.j2

demo.json
---------

..  literalinclude:: ../../demo/demo.json

demo.toml
---------

..  literalinclude:: ../../demo/demo.toml

demo.yaml
---------

..  literalinclude:: ../../demo/demo.yaml

The ``demo.txt.j2`` template can be rendered to standard output with::

    $ j2render -o stdout demo.j2
    Hello, World!
    alpha
    beta
    gamma
    delta
    epsilon

If the *--output* option is not provided, rendered template output will be
written to a file with the same name as the template, minus its Jinja extension.
If the *--output* option is provided, rendered template output will be
written to that file.

Templates are rendered using template variables provided by one or more data
sources.

If no template variables sources are provided, a data file will be searched for
meeting the following criteria:

- a data file in the same directory as the template file with the same base name
- a data file with an extension of one of the supported data formats

Given a template ``demo/demo.j2`` the following data files would be considered,
and used if it exists:

- ``demo/demo.json``
- ``demo/demo.toml``
- ``demo/demo.yaml``
- ``demo/demo.yml``

A specific data file may be provided with the *--source* option.  Multiple
sources may be provided, and later sources will override values in previously
loaded sources.

Data may also be loaded from a Python module, using the ``some.module:attr``
format.  For example, ``my.pkg:config`` would specify using the values found in
the ``config`` attribute of the ``my.pkg`` module.

..  toctree::
    :maxdepth: 1

    releases
