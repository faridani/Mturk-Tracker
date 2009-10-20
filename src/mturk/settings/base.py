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
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
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
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'mturk.main'    
)

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
)
INTERNAL_IPS = ['127.0.0.1']

GOOGLE_ANALYTICS_ID='UA-89122-1'

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
LOGIN_REDIRECT_URL = "/"