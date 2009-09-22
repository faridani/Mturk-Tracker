from defaults import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('konrad', 'conrad.adamczyk@gmail.com'),
    ('mklujszo', 'mklujszo@gmail.com'),
)

MANAGERS = ADMINS

SITE_ID = 1

USE_I18N = True

ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1=r4y=s3=t-l&dj4t)s7yj&nhu^aio8%0l4f@v2r)e6v#upyi+'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_DIRS = (
    os.path.join(ROOT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',    
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
)
