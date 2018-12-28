Configuration
=============

Exhibition draws configuration options from three places:

- ``site.yaml``, which is the root configuration file
- ``meta.yaml``, which there can be one or none in any given folder
- "Frontmatter", which is a YAML header that can be put in any text file. It
  *must* be the first thing in the file and it *must* start and end with
  ``---`` - both on their own lines.

The difference between these different places to put configuration is explain
in detail in the :doc:`getting-started` page.

Inheritance
-----------

One important aspect of Exhibition's configuration system is that for a given
node (a file or a folder), a key is search for in the following way:

1. The current node is checked for the
   specified key. If it's found, it is returned. Otherwise carry on to 2.
2. The parent of the current node is checked, and if the specified key is not
   found here then *its* parent is checked the same way (and so on), until the
   root node is found.
3. If the root node does not have the specified key, then ``site.yaml`` is searched.
4. Only once ``site.yaml`` has been searched is a :class:`KeyError` raised.

Mandatory
---------

The following options must be present in ``site.yaml``:

``content_path``
^^^^^^^^^^^^^^^^

This is the path to where Exhibition will load data from. It should have the
same directory structure and files as you want to appear in the rendered site.

``deploy_path``
^^^^^^^^^^^^^^^

Once rendered, pages will be placed here.

.. warning::

   ``content_path`` and ``deploy_path`` should *only* appear in ``site.yaml``.

General
-------

``ignore``
^^^^^^^^^^

Matching files are not processed by Exhibition at all. Can be a file name or a
glob pattern:

.. code-block:: yaml

   ignore: "*.py"

As glob patterns are fairly simple, ``ignore`` can also be a list of patterns:

.. code-block:: yaml

   ignore:
     - "*.py"
     - example.xcf

``base_url``
^^^^^^^^^^^^

If your site isn't deployed to the root of a domain, use this setting to tell
Exhibition about the prefix so it can be added to all URLs

Filters
-------

` `filter``
^^^^^^^^^^^

The dotted path notation that Exhibition can import to process content on a node.

Exhibition comes with one filter: ``exhibition.filters.jinja2``

``filter_glob``
^^^^^^^^^^^^^^^

Matching files are processed by ``filter`` if specified, otherwise this option
does nothing.

.. code-block:: yaml

   filter_glob: "*.html"

As glob patterns are fairly simple, ``filter_glob`` can also be a list of
patterns:

.. code-block:: yaml

   filter_glob:
     - "*.html"
     - "*.htm"
     - "robot.txt"

Filters specify their own default glob, refer to the documentation of that
filter to find out what that is.

Jinja2
^^^^^^

``templates``
~~~~~~~~~~~~~

The path where Jinja2 templates will be found. Can be single string or a list.

``extends``
~~~~~~~~~~~

If specified, this will insert a ``{% extends %}`` statement at the beginning of
the file content before it is passed to Jinja2.

``default_block``
~~~~~~~~~~~~~~~~~

If specified, this will wrap the file content in ``{% block %}``.

``markdown_config``
~~~~~~~~~~~~~~~~~~~

Markdown options as specified in the `Markdown documentation
<https://python-markdown.github.io/reference/#markdown>`_.

External Command
^^^^^^^^^^^^^^^^

external_cmd
~~~~~~~~~~~~

The command to run. This should use the placeholders ``{INPUT}`` and
``{OUTPUT}`` for the input and output files respectively. For example:

.. code-block: yaml

   external_cmd: "cat {INPUT} | sort > {OUTPUT}"

Cache busting
-------------

Cache busting is an important tool that allows static assets (such as CSS
files) to bypass the browser cache when the content of such files is updated,
while still allowing high value expiry times.

``cache_bust_glob``
^^^^^^^^^^^^^^^^^^^

Matching files have their deployed path and URL changed to include a hash of
their contents. E.g. ``media/site.css`` might become
``media/site.894a4cd1.css``. You can specify globs in the usual manner:

.. code-block:: yaml

   cache_bust_glob: "*.css"

As glob patterns are fairly simple, ``cache_bust_glob`` can also be a list of
patterns:

.. code-block:: yaml

   cache_bust_glob:
     - "*.css"
     - "*.jpg"
     - "*.jpeg"

To refer to cache busted nodes in your Jinja2 templates, do the following:

.. code-block:: html+jinja

   <link rel="stylesheet" href="{{ node.get_from_path("/media/css/site.css").full_url }}" type="text/css">
