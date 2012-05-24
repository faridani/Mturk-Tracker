import logging
import sys

DATABASE_NAME = 'mturk_crawl'
DEBUG = False

USE_CACHE = True
SOLR_MAIN = "http://localhost:8983/solr/en"

LOG_DIRECTORY = '/home/mtracker/log'


FORMAT = '%(asctime)s %(levelname)s %(message)s'
formatter = logging.Formatter(FORMAT)

logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    filename=LOG_DIRECTORY + 'crawl.log',
    filemode='a'
)

stdout_log_handler = logging.StreamHandler(sys.stdout)
stdout_log_handler.setFormatter(formatter)

_log = logging.getLogger()
_log.addHandler(stdout_log_handler)


CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
