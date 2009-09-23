import os
from django.conf import ENVIRONMENT_VARIABLE

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DJANGO_PATH = os.path.join(ROOT_PATH, os.path.join(ROOT_PATH, 'libs', 'django'))
PROJECT_NAME = os.path.basename(ROOT_PATH)
SETTINGS_NAME = os.environ[ENVIRONMENT_VARIABLE].split(".")[-1]

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'mturk_crawl'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

ROOT_URLCONF = PROJECT_NAME + '.urls'

MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')
MEDIA_URL = '/s/'