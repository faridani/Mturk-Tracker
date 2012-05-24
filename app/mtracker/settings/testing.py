"""Settings specific for running under Jenkins."""

import re
import os
from defaults import *

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')
STATIC_ROOT = os.path.join(PROJECT_PATH, 'collected_static')
STATIC_URL = '/static/'

TIME_ZONE = 'UTC'
CACHE_BACKEND = 'dummy:///'

# sudo -u postgres psql
# CREATE USER jenkins_mtracker WITH CREATEDB NOCREATEUSER ENCRYPTED PASSWORD E'jenkins';
# CREATE DATABASE jenkins_mtracker_db WITH OWNER jenkins_mtracker;

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'jenkins_mtracker_db',
        'USER': 'jenkins_mtracker',
        'PASSWORD': 'jenkins',
        'HOST': 'localhost',
        'PORT': '',
    },
}

DB = DATABASES['default']
DATABASE_NAME = DB['NAME']
DATABASE_USER = DB['USER']
DATABASE_PASSWORD = DB['PASSWORD']

INSTALLED_APPS = tuple(list(INSTALLED_APPS) + [
    "django_jenkins",
])

# Which apps should we test.
PROJECT_APPS = MTRACKER_APPS

# Which tasks to run.
JENKINS_TASKS = (
    'django_jenkins.tasks.run_pyflakes',
    'django_jenkins.tasks.run_pep8',
    # JSlint is broken with Django jenkins.
    #'django_jenkins.tasks.run_jslint',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
)

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
