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
from defaults import *

MANAGERS = ADMINS = (
    ('maciel', 'cielecki@gmail.com'),
    ('mklujszo', 'mklujszo@gmail.com'),
    ('konrad', 'conrad.adamczyk@gmail.com'),
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'op56pokf54./&^%$GDAWLEosh"AP#O$%^&KLUYHBLAKLPLPkso'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
)

TEMPLATE_DIRS = (
    os.path.join(ROOT_PATH, 'templates'),
)


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',

    'mturk.tabs_context_processor.tabs'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.webdesign',
    'south',
    'mturk.main',
    'mturk.importer',
    'mturk.spam',
)

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
)
INTERNAL_IPS = ['127.0.0.1']

GOOGLE_ANALYTICS_ID='UA-89122-17'

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
LOGIN_REDIRECT_URL = "/"

DATASMOOTHING = True

PREDICTION_API_KEY= "AIzaSyDiETxIg9DJ6Unu7zbfPDKEoXq3v_9CAms"
# PREDICTION_API_KEY= "AIzaSyDmmL1HdgFRnE32sSYay52X5bplfhnxyrA"

# mickek client
# PREDICTION_API_CLIENT_ID= "581229398898.apps.googleusercontent.com"
# PREDICTION_API_CLIENT_SECRET= "u-TQagk4z93p5W6OO7hoRBKZ"

PREDICTION_API_CLIENT_ID= "1096089602663-erfn2lj26ae9n1djidfu8gf2e5egs5bk.apps.googleusercontent.com"
PREDICTION_API_CLIENT_SECRET= "cWPdUE0BCcQsbZZ_xvLO9dMI"

PREDICTION_API_DATA_SET= "mturk-tracker/spam-training-data-20110506.txt"