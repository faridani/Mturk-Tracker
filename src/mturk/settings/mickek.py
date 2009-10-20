from base import *

LOG_DIRECTORY = '/var/log/mturk/'

import logging
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = LOG_DIRECTORY + 'crawl.log',
    filemode = 'a'
)