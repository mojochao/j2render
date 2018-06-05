.. _j2render_docs:

=========
j2render
=========

The **j2render** package provides the ``j2render`` command-line interface
(CLI) for rendering `Jinja2 <http://jinja.pocoo.org/docs>`_ from data provided
by JSON, TOML and YAML files and on the command line to standard output or a file.

..  toctree::
    :maxdepth: 1

    releases

Installation
============

Install the **j2render** package from `PyPi <https://pypi.org>`_ with ``pip``::

    $ pip install j2render

Help
====

Use the *--help* option to get help on usage.

..  command-output:: j2render --help

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

The ``demo.txt.j2`` template can be rendered to standard output with:

..  command-output:: j2render -o stdout demo.j2
    :cwd: ../../demo

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
