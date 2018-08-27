|Build Status| |Coverage| |docs|

Exhibition - A Python Static Site Generator
===========================================

.. inclusion-marker-do-not-remove-start

Say it right:

    /ɛgs'hɪb'ɪʃ(ə)n/

So something like:

    eggs hib ish'n

What?
-----

A static site generator

License?
--------

GPLv3 or later. See LICENSE for the actual text.

Why though?
-----------

I've been using Hyde since forever, but I wasn't happy with it. I was also very
unhappy with other static site generators (SSGs) that used Jinja2 for their
templating needs:

- Pelican and the like are too blog focused. It didn't feel in the spirit of
  those projects to have a blog and a recipe list as two separate sections to a
  website.
- Hyde is everything I want, except for the complete lack of documentation and
  a massive code base that needs a lot of work to make it run on Python 3. It
  is also currently unmaintained.

  - I should also mention that there are huge parts of Hyde that do nothing for
    me, so starting from scratch made more sense than dealing with Hyde.

There are SSGs that aren't written in Python or don't use Jinja2 for their
templates, but I'm not interested in rewriting all the templates for the sites
that I have made with Hyde.

What's the status of this project?
----------------------------------

There are tests, there's some documentation, and I currently use it for a
number of websites including my personal blog.

Please feel free to add your site to `the wiki`_ if it uses Exhibition, but
please make sure its safe for work and not covered in adverts.

.. _`the wiki`: https://github.com/moggers87/exhibition/wiki

Contributions
^^^^^^^^^^^^^

I'm always looking for contributions, whether they be bug reports, bug fixes,
feature requests, new features, or documentation. Also, feel free to open issues
for support requests too - these are very helpful in showing me where
documentation is required or needs improving.

There are however some items I won't consider for inclusion:

- Functionality to upload the static site once generated. This is and shall
  remain out of scope for this project.
- Windows support. I've tried maintaining packages before that have Windows
  support. I usually end up breaking it as I have no way to test out my changes
  on a regular basis.
- Python 2 support.

.. inclusion-marker-do-not-remove-end

.. |Build Status| image:: https://travis-ci.org/moggers87/exhibition.svg?branch=master
   :alt: Build Status
   :scale: 100%
   :target: https://travis-ci.org/moggers87/exhibition
.. |Coverage| image:: https://codecov.io/github/moggers87/exhibition/coverage.svg?branch=master
   :target: https://codecov.io/github/moggers87/exhibition
   :alt: Coverage Status
   :scale: 100%
.. |docs| image:: https://readthedocs.org/projects/exhibition-ssg/badge/?version=latest
   :alt: Documentation Status
   :scale: 100%
   :target: https://exhibition-ssg.readthedocs.io/en/latest/?badge=latest
