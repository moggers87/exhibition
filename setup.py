from setuptools import setup, find_packages

with open("README.rst", "r") as f:
    long_desc = f.read()

setup(
    name="exhibition",
    version="0.0.3",
    author="Matt Molyneaux",
    author_email="moggers87+git@moggers87.co.uk",
    description="A Python static site generator",
    long_description=long_desc,
    url="https://github.com/moggers87/exhibition",
    download_url="https://pypi.org/project/exhibition/",
    packages=find_packages(),
    test_suite="exhibition.tests",
    license="GPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Internet",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development",
    ],
    install_requires=[
        "click",
        "jinja2",
        "markdown",
        "ruamel.yaml",
        "typogrify",
    ],
    extras_require={
        "docs": [
            "sphinx",
            "sphinx_rtd_theme",
            "sphinx-click",
        ],
    },
    entry_points={
        "console_scripts": [
            "exhibit = exhibition.command:exhibition",
        ]
    },
)
