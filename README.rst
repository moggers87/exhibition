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

I've been using Hyde since forever, but I wasn't happy with it. I was also very unhappy with other static site generators (SSGs) that used Jinja2 for their templating needs:

- Pelican and the like are too blog focused. It didn't feel in the spirit of
  those projects to have a blog and a recipe list as two separate sections to a
  website.
- Hyde is everything I want, except for the complete lack of documentation and
  a massive code base that needs a lot of work to make it run on Python 3. It
  is also currently unmaintained.

  - I should also mention that there are huge parts of Hyde that do nothing for
    me, so starting from scratch made more sense than dealing with Hyde.

There are SSGs that aren't written in Python or don't use Jinja2 for their
templates, but I'm not interested in rewritting all the templates for the sites
that I have made with Hyde.

What's the status of this project?
----------------------------------

I'm not using it for anything serious yet, but there are tests, and there are some docs.

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
