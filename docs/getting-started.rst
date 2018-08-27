Getting started
===============

Exhibition is fairly quick to configure.

Minimum setup
-------------

At minimum, Exhibition expects to find a YAML file, ``site.yaml``, with at
least ``deploy_path`` and ``content_path`` defined. The path specified in
``content_path`` needs to exist.

For example:

.. code-block:: shell

   $ mkdir content
   $ cat << EOF > site.yaml
   > deploy_path: deploy
   > content_path: content
   > EOF

You can now generate your first Exhibition website!:

.. code-block:: shell

   $ exhibit gen
   $ ls deploy

Of course, you've got no content so the directory will be empty.

Any file or directory you put in ``content`` will appear in ``deploy`` when you
run ``exhibit gen``.

Templates
---------

Exhibition supports `Jinja2 <http://jinja.pocoo.org/>`_ out of the box, but it
needs to be enabled:

.. code-block:: yaml
   :caption: site.yaml

   deploy_path: deploy
   content_path: content
   filter: exhibition.filters.jinja2

Now we can create HTML files that use Jinja2 template syntax:

.. code-block:: html+jinja
   :caption: content/index.html

   <html>
     <body>
       <p>This page has {{ node.siblings|length }} siblings</p>
     </body>
   </html>

.. note::

   ``node`` is the current page being rendered and is passed to Jinja2 as a context variable.

Run ``exhibit gen`` and then ``exhibit serve``. If you connect to
``http://localhost:8000`` you'll see the following text::

    This page has 0 siblings

If you add another page, this number will increase when run ``exhibit gen`` again.

If you wish to use template inheritance, add the following to ``site.yaml``:

.. code-block:: yaml

   templates: mytemplates

Where "mytemplates" is whatever directory you will store your templates in. You
can either use the extends tag directly or you can specify ``extends`` in
``site.yaml``. You can also specify ``default-block`` to save you from wrapping
every page in ``{% block content %}``:

.. code-block:: yaml

   extends: page.j2
   default-block: content

And then our template:

.. code-block:: html+jinja
   :caption: mytemplates/page.j2

   <html>
     <body>
       {% block content %}{% endblock %}
     </body>
   </html>

Our index page would be this:

.. code-block:: html+jinja
   :caption: content/index.html

   <p>This page has {{ node.siblings|length }} siblings</p>

The generated HTML will be exactly the same, except now files in ``content/``
will not have to each have their own copy of any headings, page title, links to
CSS or whatever.

Meta
----

Site settings are available in templates as ``node.meta``. For example:

.. code-block:: html+jinja
   :caption: content/otherpage.html

   <p>Current filter is "{{ node.meta.filter }}"</p>

Which will generate the following::

    Current filter is "exhibition.filters.jinja2"

You can reference any data that you put in ``site.yaml`` like this - and
there's no limit on what you can put in there.

As well as ``site.yaml`` there are two additional places that settings can be
controlled: ``meta.yaml`` and front matter.

Meta files
^^^^^^^^^^

A ``meta.yaml`` can be used to define or override settings for a particular
directory and any files or subdirectories it contains.

Let's add a blog to our website:

.. code-block:: shell

   $ mkdir content/blog
   $ cat << EOF > content/blog/meta.yaml
   > extends: blog_post.j2

Now all HTML files in ``content/blog/`` will use the ``blog_post.j2`` as their
base template rather than ``page.j2``, but files such as ``content/index.html``
will still use ``page.j2`` as their base template.

.. note::
   ``meta.yaml`` files do not appear as nodes and won't appear in ``deploy_path``

Frontmatter
^^^^^^^^^^^

Frontmatter is the term used to describe YAML metadata put at the beginning of
a file. Unlike ``meta.yaml``, any settings defined (or overridden) here will
only affect this one file.

For example, we won't want the index page of our blog to use ``blog_post.j2``
as its base template:

.. code-block:: html+jinja
   :caption: content/blog/index.html

   ---
   extends: blog_index.j2
   ---
   {% for post in node.sibling %}
      <p><a href="{{ post.full_url }}">{{ post.meta.title }}</a></p>

.. code-block:: html+jinja
   :caption: content/blog/first-post.html

   ---
   title: My First Post
   ---
   <h1>{{ node.meta.title }}
   <p>Hey! This is my first blog post!</p>

What next?
----------

Checkout the :doc:`API <modules>`. File bugs. Submit patches.

Exhibition is still in the early stages of development, so please contribute!
