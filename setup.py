from setuptools import setup


setup(
    name="exhibition",
    version="0.1",
    author="Matt Molyneaux",
    author_email="moggers87+git@moggers87.co.uk",
    packages=["exhibition"],
    license="GPLv3",
    classifiers=[
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Internet",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development",
        "Programming Language :: Python :: 3.5",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3) or later",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=[
        "click",
        "jinja2",
        "ruamel.yaml",
    ],
    entry_points={
        "console_scripts": [
            "exhibit = exhibition.command:exhibition",
        ]
    },
)
