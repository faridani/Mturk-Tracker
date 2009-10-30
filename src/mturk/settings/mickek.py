from base import *

LOG_DIRECTORY = '/var/log/mturk/'

#DATABASE_NAME = PROJECT_NAME + "_crawl"    # Or path to database file if using sqlite3.
#DATABASE_HOST = '127.0.0.1'                              # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = '54320'                              # Set to empty string for default. Not used with sqlite3.

import logging
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = LOG_DIRECTORY + 'crawl.log',
    filemode = 'a'
)

TIME_ZONE = 'Europe/Warsaw'
CACHE_BACKEND = 'dummy:///'