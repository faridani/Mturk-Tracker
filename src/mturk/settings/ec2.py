LOG_DIRECTORY = '/var/log/mturk/'

import logging
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = LOG_DIRECTORY + 'crawl.log',
    filemode = 'a'
)

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'