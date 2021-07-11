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

Where?
------

- Download: https://pypi.org/project/exhibition/
- Source: https://github.com/moggers87/exhibition
- Docs: https://exhibition-ssg.readthedocs.io/en/latest/

License?
--------

GPLv3 or later. See LICENSE for the actual text.

Why though?
-----------

I'd been using `Hyde`_ for a number of years, eventually that project stopped
receiving updates. Hyde had very limited test coverage, many features that I
didn't personally use, and no Python 3 support.  This combination made the
prospect of maintaining Hyde daunting, so forking was out of the question.

.. _`Hyde`: https://github.com/hyde/hyde

In the end, I wrote Exhibition as other available static site generators would
either require massively rewriting the sites I already had or weren't flexible
enough to generate the same URL structure.

What's the status of this project?
----------------------------------

There are tests, there's some documentation, and I currently use it for a
number of websites, including my personal blog.

Please feel free to add your site to `the wiki`_ if it uses Exhibition, but
please make sure its safe for work and not covered in adverts.

.. _`the wiki`: https://github.com/moggers87/exhibition/wiki

Contributions
^^^^^^^^^^^^^

I'm always looking for contributions, whether they be bug reports, bug fixes,
feature requests, new features, or documentation. Also, feel free to open issues
for support requests too - these are very helpful in showing me where
documentation is required or needs improving.

Code Of Conduct
---------------

The Exhibition project has adopted the Contributor Covenant Code version 1.4. By
contributing to this project, you agree to abide by its terms.

The full text of the code of conduct can be found `here
<https://github.com/moggers87/exhibition/blob/main/CODE_OF_CONDUCT.md>`__


.. inclusion-marker-do-not-remove-end

Funding
-------

If you have found Exhibition to be useful and would like to see its continued
development, please consider `buying me a coffee
<https://ko-fi.com/moggers87>`__.

.. |Build Status| image:: https://github.com/moggers87/exhibition/actions/workflows/tests.yml/badge.svg?branch=main
   :alt: Build Status
   :scale: 100%
   :target: https://github.com/moggers87/exhibition/actions/workflows/tests.yml?query=branch%3Amain
.. |Coverage| image:: https://codecov.io/github/moggers87/exhibition/coverage.svg?branch=main
   :target: https://codecov.io/github/moggers87/exhibition
   :alt: Coverage Status
   :scale: 100%
.. |docs| image:: https://readthedocs.org/projects/exhibition-ssg/badge/?version=latest
   :alt: Documentation Status
   :scale: 100%
   :target: https://exhibition-ssg.readthedocs.io/en/latest/?badge=latest
