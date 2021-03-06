#!/usr/bin/env python
# This is the module's setup script.  To install this module, run:
#
#   python setup.py install
#
# $Id: setup.py 6175 2009-11-02 18:40:35Z lowell $
""" Concurrent logging handler (drop-in replacement for RotatingFileHandler)
Overview
========
This module provides an additional log handler for Python's standard logging
package (PEP 282). This handler will write log events to log file which is 
rotated when the log file reaches a certain size.  Multiple processes can
safely write to the same log file concurrently.

Details
=======
.. _portalocker:  http://code.activestate.com/recipes/65203/

The ``ConcurrentRotatingFileHandler`` class is a drop-in replacement for
Python's standard log handler ``RotatingFileHandler``. This module uses file
locking so that multiple processes can concurrently log to a single file without
dropping or clobbering log events. This module provides a file rotation scheme
like with ``RotatingFileHanler``.  Extra care is taken to ensure that logs
can be safely rotated before the rotation process is started. (This module works
around the file rename issue with ``RotatingFileHandler`` on Windows, where a
rotation failure means that all subsequent log events are dropped).

This module attempts to preserve log records at all cost. This means that log
files will grow larger than the specified maximum (rotation) size. So if disk
space is tight, you may want to stick with ``RotatingFileHandler``, which will
strictly adhere to the maximum file size.

If you have multiple instances of a script (or multiple scripts) all running at
the same time and writing to the same log file, then *all* of the scripts should
be using ``ConcurrentRotatingFileHandler``. You should not attempt to mix
and match ``RotatingFileHandler`` and ``ConcurrentRotatingFileHandler``.

This package bundles `portalocker`_ to deal with file locking.  Please be aware
that portalocker only supports Unix (posix) an NT platforms at this time, and
therefore this package only supports those platforms as well.

Installation
============
Use the following command to install this package::

    easy_install ConcurrentLogHandler

If you are installing from source, you can use::

    python setup.py install


Examples
========

Simple Example
--------------
Here is a example demonstrating how to use this module directly (from within
Python code)::

    from logging import getLogger, INFO
    from cloghandler import ConcurrentRotatingFileHandler
    import os
    
    log = getLogger()
    # Use an absolute path to prevent file rotation trouble.
    logfile = os.path.abspath("mylogfile.log")
    # Rotate log after reaching 512K, keep 5 old copies.
    rotateHandler = ConcurrentRotatingFileHandler(logfile, "a", 512*1024, 5)
    log.addHandler(rotateHandler)
    log.setLevel(INFO)
    
    log.info("Here is a very exciting log message, just for you")


Automatic fallback example
--------------------------
If you are distributing your code and you are unsure if the
`ConcurrentLogHandler` package has been installed everywhere your code will run,
Python makes it easy to gracefully fallback to the built in
`RotatingFileHandler`, here is an example::

    try:
        from cloghandler import ConcurrentRotatingFileHandler as RFHandler
    except ImportError:
        # Next 2 lines are optional:  issue a warning to the user
        from warnings import warn
        warn("ConcurrentLogHandler package not installed.  Using builtin log handler")
        from logging.handlers import RotatingFileHandler as RFHandler
    
    log = getLogger()
    rotateHandler = RFHandler("/path/to/mylogfile.log", "a", 1048576, 15)
    log.addHandler(rotateHandler)



Config file example
-------------------
This example shows you how to use this log handler with the logging config file
parser. This allows you to keep your logging configuration code separate from
your application code.

Example config file: ``logging.ini``::

    [loggers]
    keys=root
    
    [handlers]
    keys=hand01
    
    [formatters]
    keys=form01
    
    [logger_root]
    level=NOTSET
    handlers=hand01
    
    [handler_hand01]
    class=handlers.ConcurrentRotatingFileHandler
    level=NOTSET
    formatter=form01
    args=("rotating.log", "a", 512*1024, 5)
    
    [formatter_form01]
    format=%(asctime)s %(levelname)s %(message)s

Example Python code: ``app.py``::

    import logging, logging.config
    import cloghandler
    
    logging.config.fileConfig("logging.ini")
    log = logging.getLogger()
    log.info("Here is a very exciting log message, just for you")


Change Log
==========

- 0.8.4:  Fixed lock-file naming issue
   * Resovled a minor issue where lock-files would be improperly named if the
     log file contained ".log" in the middle of the log name.  For example, if
     you log file was "/var/log/mycompany.logging.mysource.log", the lock file
     would be named "/var/log/mycompany.ging.mysource.lock", which is not correct.
     Thanks to Dirk Rothe for pointing this out.  Since this introduce a slight 
     lock-file behaviour difference, make sure all concurent writers are updated
     to 0.8.4 at the same time if this issue effects you.
   * Updated ez_setup.py to 0.6c11

- 0.8.3:  Fixed a log file rotation bug and updated docs
   * Fixed a bug that happens after log rotation when multiple processes are
     witting to the same log file. Each process ends up writing to their own
     log file ("log.1" or "log.2" instead of "log"). The fix is simply to reopen
     the log file and check the size again.  I do not believe this bug results in
     data loss; however, this certainly was not the desired behavior.  (A big
     thanks goes to Oliver Tonnhofer for finding, documenting, and providing a
     patch for this bug.)
   * Cleanup the docs. (aka "the page you are reading right now") I fixed some
     silly mistakes and typos... who writes this stuff?

- 0.8.2:  Minor bug fix release (again)
   * Found and resolved another issue with older logging packages that do not
     support encoding.

- 0.8.1:  Minor bug fix release
   * Now importing "codecs" directly; I found some slight differences in the
     logging module in different Python 2.4.x releases that caused the module to
     fail to load.

- 0.8.0:  Minor feature release
    * Add better support for using ``logging.config.fileConfig()``. This class
      is now available using ``class=handlers.ConcurrentRotatingFileHandler``.
    * Minor changes in how the ``filename`` parameter is handled when given a
      relative path.

- 0.7.4:  Minor bug fix
    * Fixed a typo in the package description (incorrect class name)
    * Added a change log; which you are reading now.
    * Fixed the ``close()`` method to no longer assume that stream is still
      open.

To-do
=====
* This module has had minimal testing in a multi-threaded process.  I see no
  reason why this should be an issue, but no stress-testing has been done in a
  threaded situation. If this is important to you, you could always add
  threading support to the ``stresstest.py`` script and send me the patch.

"""




from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup


VERSION = "0.8.4"
classifiers = """\
Development Status :: 4 - Beta
Development Status :: 5 - Production/Stable
Topic :: System :: Logging
Operating System :: POSIX
Operating System :: Microsoft :: Windows
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
License :: OSI Approved :: Apache Software License
"""
doc = __doc__.splitlines()


setup(name='ConcurrentLogHandler',
      version=VERSION,
      author="Lowell Alleman",
      author_email="lowell87@gmail.com",
      py_modules=[
        "cloghandler",
        "portalocker",
        ],
      package_dir={ '' : 'src', },
      data_files=[
        ('tests', ["stresstest.py"]),
        ('docs', [
            'README',
            'LICENSE',
            ]),
      ],
      url="http://pypi.python.org/pypi/ConcurrentLogHandler",
      license = "http://www.apache.org/licenses/LICENSE-2.0",
      description=doc.pop(0),
      long_description="\n".join(doc),
      platforms = [ "nt", "posix" ],
      classifiers=classifiers.splitlines(),
      zip_safe=True,
      #test_suite=unittest.TestSuite,
)



