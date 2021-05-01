.. _zero-two-one:

0.2.1
~~~~~

This release is just for a fix some bad syntax in our documentation. Nothing
else has changed!

.. _zero-two-zero:

0.2.0
-----

Added
~~~~~

- Add support for a pandoc filter for Jinja2 templates

Removed
~~~~~~~

- Remove support for Python 3.5, 3.6, and 3.7

Fixed
~~~~~

- Add description to ``exhibit`` command
- Use ``cached_property`` to make code cleaner

.. _zero-one-one:

0.1.1
-----

Added
~~~~~

- Allow settings of local HTTP server address and port.
- Added Python 3.8 support.

Removed
~~~~~~~

*Nothing was removed in this release*

Fixed
~~~~~

- Set ``Cache-Control`` to ``no-store`` on HTTP server respones
- HTTP server should ignore ``GET`` params and fragments

.. _zero-one-zero:

0.1.0
-----

The *"I'd almost recommand it to my friends"* release.

Added
~~~~~

- Added Python 3.7 support.
- Add the external command filter.
- Document Jinja2 filter.
- Add ``strip_exts`` as an user configurable setting.
- Add ``index_file`` as an user configurable setting.

Removed
~~~~~~~

- Removed Python 3.4 support.

Fixed
~~~~~

- Reorganised package so that code is easier to manage.
- Make node loading deterministic, meta files loaded first and then
  alphabetical order for the rest.

.. _zero-zero-four:

0.0.4
-----

- Added vesrioneer.
- Fix bug where ``exhibit serve`` was not serving files with extension
  stripping enabled.
- A ``KeyError`` raised by ``Config`` now display the path of the node they are
  attached to, making debuging missing keys far easier.
- Improved test coverage and fixed numerous bugs.
- Implemented cache busting for static assets (images, CSS, and such). Use the
  ``cache_bust_glob`` option to control which files are cache busted.
- Implemented ``Node.get_from_path`` which can fetch a
  :class:`exhibition.main.Node` specified by a path.
- Make all Exhibition defined meta keys use underscores not hyphens.

.. _zero-zero-three:

0.0.3
-----

- Fix bug where extension stripping was not being applied.

.. _zero-zero-two:

0.0.2
-----

- Fixed trove classifiers.
- Add ``__version__`` to ``exhibition.__init__``.

.. _zero-zero-one:

0.0.1
-----

Everything is new! Some choice features:

- Configuration via YAML files and YAML front matter.
- Jinja2 template engine is provided by default.
- A local HTTP server for development work.
- Less than 2000 lines of code, including tests.
