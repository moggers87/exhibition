Unreleased
----------

- Added vesrioneer
- Fix bug where ``exhibit serve`` was not serving files with extension
  stripping enabled
- ``KeyError``s raised by ``Config`` now display the path of the node they are
  attached to, making debuging missing keys far easier.

.. _zero-zero-three:

0.0.3
-----

- Fix bug where extension stripping was not being applied

.. _zero-zero-two:

0.0.2
-----

- Fixed trove classifiers
- Add ``__version__`` to ``exhibition.__init__``

.. _zero-zero-one:

0.0.1
-----

Everything is new! Some choice features:

- Configuration via YAML files and YAML front matter
- Jinja2 template engine is provided by default
- A local HTTP server for development work
- Less than 2000 lines of code, including tests
