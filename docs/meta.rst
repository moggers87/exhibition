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

1. The current node is checked for the specified key. If it's found, it is
   returned. Otherwise carry on to 2.
2. The parent of the current node is checked, and if the specified key is not
   found here then *its* parent is checked the same way (and so on), until the
   root node is found.
3. If the root node does not have the specified key, then ``site.yaml`` is
   searched.
4. Only once ``site.yaml`` has been searched is a :class:`KeyError` raised if
   the key cannot be found.

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

``strip_exts``
^^^^^^^^^^^^^^

Specifies if certain files should have their extensions removed when being
referenced via ``Node.full_url``. When deploying, this does not change the
filename, so you will need to configure your web server to serve those files
correctly.

By default, this will be applied to files ending in ``.html``, to disable this
feature use the following:

.. code-block:: yaml

    strip_exts:

You can also specify multiple file extensions:

.. code-block:: yaml

    strip_exts:
        - .html
        - .htm

``index_file``
^^^^^^^^^^^^^^

Specify the name file name of the "index" file for a directory. By default this
is ``index.html``, as it is on most web servers. If you change this settings,
be sure to update your web server's configuration to reflect this change.

``dir_mode``
^^^^^^^^^^^^

Specify the permissions of the directories created when generating the site. Default value is ``0o755``.

``file_mode``
^^^^^^^^^^^^^

Specify the permissions of the files created when generating the site. Default value is ``0o644``.

Filters
-------

``filter``
^^^^^^^^^^

The dotted path notation that Exhibition can import to process content on a node.

Exhibition comes with a number of filters, such as ``exhibition.filters.jinja2``.

.. code-block:: yaml

   filter: exhibition.filters.jinja2

You can also specify multiple filters, like this:

.. code-block:: yaml

   filter:
     - exhibition.filters.jinja2
     - - exhibition.filters.external
       - "*.jpeg"
   external_cmd: "cat {INPUT} | exiftool - > {OUTPUT}"

Here you can see that the jinja2 filter will be applied using its default glob
(``*.html``) and the external command filter will be applied to JPEG images.

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

``filter_glob`` is ignored if ``filter`` is a list of filters.

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

``pandoc_config``
~~~~~~~~~~~~~~~~~~~

Pandoc options as specified in the `PyPandoc documentation
<https://github.com/NicklasTegner/pypandoc#usage>`_ for the ``convert_text``
function.

External Command
^^^^^^^^^^^^^^^^

external_cmd
~~~~~~~~~~~~

The command to run. This should use the placeholders ``{INPUT}`` and
``{OUTPUT}`` for the input and output files respectively. For example:

.. code-block:: yaml

   external_cmd: "cat {INPUT} | sort > {OUTPUT}"

Markdown
^^^^^^^^

``markdown_config``
~~~~~~~~~~~~~~~~~~~

Markdown options as specified in the `Markdown documentation
<https://python-markdown.github.io/reference/#markdown>`_.

Pandoc
^^^^^^

``pandoc_config``
~~~~~~~~~~~~~~~~~~~

Pandoc options as specified in the `PyPandoc documentation
<https://github.com/NicklasTegner/pypandoc#usage>`_ for the ``convert_text``
function.

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
