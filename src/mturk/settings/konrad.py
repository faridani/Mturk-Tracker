from base import *

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'mturk_crawl'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = 'test12'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'

TIME_ZONE = 'Europe/Warsaw'
LANGUAGE_CODE = 'pl-pl'

LOG_DIRECTORY = '/var/log/mturk/'

import logging
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = LOG_DIRECTORY + 'crawl.log',
    filemode = 'a'
)