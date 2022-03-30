Filters
=======

Exhibition comes with a number of filters. You can also write your own!

Filters are set by adding the dotted path to their module to the ``filter`` key
in your configuration. See :doc:`meta` for more inforatmion.

Jinja2
------

``exhibition.filters.jinja2`` will process the contents of a node via the
`Jinja2 templating engine <http://jinja.pocoo.org/>`_. Check the Jinja2
documentation for syntax and a basic understanding of how Jinja2 works.

Unless it is set, ``filter_glob`` will default to ``*.html``

Context variables
^^^^^^^^^^^^^^^^^

:node: The current node

:time_now: A datetime object that contains the current time in UTC.

Meta
^^^^

There are some meta options that are used exclusively by Jinja2:

:templates: Where to search for templates.

:extends:   Automatically add an ``{% extends %}`` tag to the start of the
            content of every affected node.

:default_block: Wrap the content of affected nodes with the specificity
                ``{% block %}`` tag.


Markdown
^^^^^^^^

``markdown`` is provided as a Jinja2 filter and it can be configured via the
``markdown_config`` meta variable, which is passed to the markdown function as
keyword arguments.

Please view the `Markdown documentation <https://python-markdown.github.io/>`_ for details.

Pandoc
^^^^^^

``pandoc`` is provided as a Jinja2 filter and can be configured by the
``pandoc_config`` meta variable, which is passed to the convert_text function
as keyword arguments.

Please refer `pypandoc project <https://github.com/bebraw/pypandoc>`_ for details.

Note, pypandoc requires pandoc to be installed. It will error without it.

Typogrify
^^^^^^^^^

All Typogrify filters are available. See the `Typogrify webste
<https://github.com/mintchaos/typogrify>`_ for more details.


Exhibition specific filters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``metasort``
~~~~~~~~~~~~

Given a list of nodes, ``metasort`` will sort the list like this:

.. code-block:: html+jinja

   {{ node.children.values()|metasort("somekey") }}

Where ``somekey`` is a key found in each node's meta.

You can also reverse the order like so:

.. code-block:: html+jinja

   {{ node.children.values()|metasort("somekey", True) }}

``metaselect`` and ``metareject``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Given a list of nodes, ``metaselect`` will filter out nodes that either do not
have that key in their meta or do but the value resolves to something falsey.
For example, the following will filter out any nodes that have ``listable`` set
to ``False``:

.. code-block:: html+jinja

   {{ node.children.values()|metaselect("listable") }}

``metareject`` works the same way, except it filters out nodes that *don't*
have falsey values for the given key.

Marked sections
^^^^^^^^^^^^^^^

Marked sections are a great way to allow parts of your content to be referenced
elsewhere, for example the preamble to a blog post:

.. code-block:: html+jinja

   ---
   title: My Post
   ---
   {% mark intro %}
   Blah blah blah…
   {% endmark %}

   Some more text

In another node you might want to list all the blog posts with their intros:

.. code-block:: html+jinja

    {% for child in node.children.values() %}
        <h3>{{ node.meta.title }}</h3>
        <p>{{ node.marks.intro }}</p>
    {% endfor %}

You can have as many marks as you like in a node and they can be nested.

Raising Errors
^^^^^^^^^^^^^^

Sometimes it can be useful to raise an error, especially if the logic in your
template is quite complex!

.. code-block:: html+jinja

    {% if 2 == 3 %}
        {% raise "This shouldn't be true! The Universe is broken!" %}
    {% endif %}

Add Your Own Template Filters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An example:

.. code-block:: python

    from exhibition.filters.jinja2 import JinjaFilter

    def emoji(input_string):
        return input_string + "🖼️"

    content_filter = JinjaFilter({"emoji": emoji})

This file should be a module that Exhibition can import and must be set in the
configuration for any pages you want to use it.

Extending Jinja2 Filter Further
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Extending the Jinja2 filter is much the same as adding your own template
filters. Simply subclass :class:`exhibition.filters.jinja2.JinjaFilter`,
override whatever methods you want and instanisate the class to
`content_filter` on your module. Then add your filter to your configuration in
place of the default  Jinja2 filter.


External Command
----------------

The external command filter only has one option: ``external_cmd``, which is the
shell command to be run. The specified command should use ``{INPUT}`` as the
input file and ``{OUTPUT}`` as the output file, for example:

.. code-block:: yaml

    external_cmd: "cat {INPUT} | base64 > {OUTPUT}"

Unless it is set, ``filter_glob`` will default to ``*.*`` for this filter.

Markdown
--------

The Markdown filter is a simple filter for those who don't want to use Jinja2.

This filter can be configured via the ``markdown_config`` meta key, which is
passed to the markdown function as keyword arguments.

Please view the `Markdown documentation <https://python-markdown.github.io/>`_ for details.

Pandoc
------

The Pandoc filter is a simple filter that can a file from one format to
another, e.g. rendering a LaTeX document to a PDF. It can be configured by the
``pandoc_config`` meta variable, which is passed to the convert_text function
as keyword arguments.

Please refer `pypandoc project <https://github.com/bebraw/pypandoc>`_ for details.

Note, pypandoc requires pandoc to be installed. It will error without it.

Make Your Own
-------------

To create your own filter for Exhibition, your module must implement a function
with the following signature:

.. code-block:: python

    def content_filter(node, content):
        return ""

:node: is the current node being processed.

:content: is the content of that node, with any frontmatter removed.

``content_filter`` should return a string, which will then become the rendered
form of this node.

As we saw in `Extending Jinja2 Filter Further`_, a filter can also be written
as a class. You can write a filter in any way you like as long as you end up
with a module that has a callable named ``content_filter``. You can take a look
at :class:`exhibition.filters.base.BaseFilter` for an example of a class based
filter.
