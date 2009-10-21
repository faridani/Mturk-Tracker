from base import *
import logging

DATABASE_NAME = 'mturk_crawl'

LOG_DIRECTORY = '/var/log/mturk/'
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = LOG_DIRECTORY + 'crawl.log',
    filemode = 'a'
)

CACHE_BACKEND = 'dummy:///'
#CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
