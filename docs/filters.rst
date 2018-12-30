Filters
=======

Exhibition comes with a number of filters. You can also write your own!

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

``markdown`` is provided as a filter and it can be configured via the
``markdown_config`` meta variable, which is passed to the markdown function as
keyword arguments.

Please view the `Markdown documentation <https://python-markdown.github.io/>`_ for details.

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

External Command
----------------

The external command filter only has one option: ``external_cmd``, which is the
shell command to be run. The specified command should use ``{INPUT}`` as the input file and ``{OUTPUT}`` as the output file, for example:

.. code-block:: yaml

    external_cmd: "cat {INPUT} | base64 > {OUTPUT}"

Unless it is set, ``filter_glob`` will default to ``*.*`` for this filter.

Make Your Own
-------------

To create your own filter for Exhibition, your module must implement a function with the following signature:

.. code-block:: python

    def content_filter(node, content):
        return ""

:node: is the current node being processed.

:content: is the content of that node, with any frontmatter removed.

``content_filter`` should return a string, which will then become the rendered form of this node.
