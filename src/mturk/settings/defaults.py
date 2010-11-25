'''
Copyright (c) 2009 Panagiotis G. Ipeirotis

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

Initially designed and created by 10clouds.com, contact at 10clouds.com
'''
import os
from django.conf import ENVIRONMENT_VARIABLE

DEBUG = True
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DJANGO_PATH = os.path.join(ROOT_PATH, os.path.join(ROOT_PATH, 'libs', 'django'))
PROJECT_NAME = os.path.basename(ROOT_PATH)
SETTINGS_NAME = os.environ[ENVIRONMENT_VARIABLE].split(".")[-1]

DATABASE_ENGINE = 'postgresql_psycopg2'         # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = PROJECT_NAME + "_" + SETTINGS_NAME    # Or path to database file if using sqlite3.
DATABASE_USER = 'postgres'                      # Not used with sqlite3.
DATABASE_PASSWORD = ''                          # Not used with sqlite3.
DATABASE_HOST = ''                              # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''                              # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# do not cache search API results
USE_CACHE = False

API_CACHE_TIMEOUT=60*60*24

SOLR_MAIN = "http://localhost:8983/solr/en"

ROOT_URLCONF = PROJECT_NAME + '.urls'

MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')
MEDIA_URL = '/s/'

DYNAMIC_MEDIA = 'd/'
ADMIN_MEDIA_PREFIX = MEDIA_URL + 'admin/'

RUN_DATA_PATH = '/tmp'

try:
    os.makedirs(os.path.join(MEDIA_ROOT, DYNAMIC_MEDIA))
except Exception:
    pass
