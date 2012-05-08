"""Settings specific for running under Jenkins."""

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
    'django_jenkins.tasks.run_jslint',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
)

SESSION_ENGINE = "django.contrib.sessions.backends.cache"


JS_IGNORES = []


def prepare_js_files():
    js_dir = os.path.join(STATICFILES_DIRS[0], 'js')
    js_files = []
    for dirname, dirs, files in os.walk(js_dir):
        for file_name in files:
            # JS Libraries ignore.
            if file_name.endswith('min.js'):
                continue
            if file_name in JS_IGNORES:
                continue
            if file_name.startswith('bootstrap'):
                continue
            if not file_name.endswith('.js'):
                continue
            js_files.append(os.path.join(dirname, file_name))
    return js_files


JSLINT_CHECKED_FILES = prepare_js_files()
###################################################################
## voodoo magic needed to run jslint :)                          ##
if 'compressor.finders.CompressorFinder' in STATICFILES_FINDERS:
    from compressor.conf import settings as c_settings
    if not os.path.exists(c_settings.COMPRESS_ROOT):
        os.makedirs(c_settings.COMPRESS_ROOT)
