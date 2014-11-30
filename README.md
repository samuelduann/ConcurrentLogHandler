ConcurrentLogHandler
====================

Lowell Alleman's ConcurrentLogHandler with a couple of fixes

Samuel Duann adds a multiprocess-safe TimedRotatingFileHandler, with a little difference with Python's logging.TimedRotatingFileHandler: these handler rotate log at the last second of each hour strictly, just like cronolog.
