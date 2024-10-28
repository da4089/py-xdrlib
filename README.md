# py-xdrlib

[![Build Status](https://github.com/da4089/py-xdrlib/actions/workflows/build.yml/badge.svg?event=push)](https://github.com/da4089/py-xdrlib/actions/workflows/build.yml)
[![Docs](https://readthedocs.org/projects/py-xdrlib/badge/?version=latest)](http://py-xdrlib.readthedocs.io/en/latest/)
[![Coverage](https://coveralls.io/repos/github/da4089/py-xdrlib/badge.svg?branch=main)](https://coveralls.io/github/da4089/py-xdrlib?branch=main)
[![PyPI](https://img.shields.io/pypi/v/py-xdrlib.svg)](https://pypi.python.org/pypi/py-xdrlib)
[![Python](https://img.shields.io/pypi/pyversions/py-xdrlib.svg)](https://pypi.python.org/pypi/py-xdrlib)
[![PePY Downloads](https://pepy.tech/badge/py-xdrlib)](https://pepy.tech/project/py-xdrlib)
[![PePY Monthly](https://pepy.tech/badge/py-xdrlib/month)](https://pepy.tech/project/py-xdrlib)

This is a copy of the Python _xdrlib_ module, present in the standard
library from release 1.4 to release 3.12.  This module will be maintained
with a compatible API and functionality for as long as it is possible 
and useful.

## Removal from Standard Library

[PEP-594](https://peps.python.org/pep-0594/#xdrlib) proposed the
removal of a number of less commonly used modules from the standard
library.  The removal of _xdrlib_ was justified on the basis that it
is rarely used other than for NFS at the time of writing in 2019.

The last version of Python to support _xdrlib_ was 3.12; the module is
no longer part of the standard library in 3.13 and later.

## Supported Python Versions

This library supports the CPython versions supported by the Python
Software Foundation, plus an additional year.

Currently, that means that Python 3.8, moved to _end-of-life_ by the PSF
on 2024-10-07, will be supported by `py-xdrlib` until 2025-10-07.

## Roadmap

* Tests
  * GitHub CI integration
  * Based off current test code from 3.11
  * See if `flit` supports a test step
  * coverage?
* Formatting
  * Black?
* Lint
  * pylint?
  * flake8
* Doc
  * Clean up the cloned doc's structure so it can stand alone
  * Push it to ... ReadTheDocs, I guess?
    * Can this be a part of the `flit publish` process too?
  * ~~Check the docstrings in the module, and extend them if they're not
    already useful~~
  * ~~Add type hints to the code~~
  * ~~Add some badges in this README~~
    * ~~GitHub CI~~
    * ~~Coverage~~
    * ~~PyPI~~
    * ~~pepy.tech?~~
* Consider adding `rpcgen`-like tool to compile XDR IDL into classes
  * IDL parser
    * Need to add support for `struct` and `union`
  * Code generator
* Investigate the newer RFCs (1832/4506) and see if there's anything
  needs to be done to comply with them.
  * If so, and it can be done transparently, just do it.
  * Otherwise, if it needs some sort of mode switch, add that.
* Extend the test suite with examples from modern NFS and elsewhere
* Check for any reported bugs in the Python bug tracker
  * Mentioned in
    [gh-83162](https://github.com/python/cpython/issues/83162), which
    seems to be dead, but the point is that the exception could be
    renamed to something more descriptive.  I think ... that's a bit
    unnecessary, since `xdrlib.Error` is kinda fine?
  * Check Debian bug tracker, and maybe Arch?
* Check for any CVEs
  * TBD
  * Can I subscribe for these?
* Push out a 4.0.x fairly soon, with better tests, better doc, and
  otherwise unchanged functionality, maintaining functionality for those 
  who need to use a single module with Python 3.8 through 3.13.

## Contributing

Contributions are very welcome!
