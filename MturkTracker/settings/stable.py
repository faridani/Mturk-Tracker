from defaults import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
JS_DEBUG = DEBUG
PIPELINE = True

DATABASES.update({
    'default': {
        'ENGINE': 'django.db.backends.',
        'NAME': 'MturkTracker_stable',
        'PORT': '',
        'USER': 'MturkTracker',
        'PASSWORD': '',
        'HOST': '',
        'OPTIONS': {}
    },
})

KEY_PREFIX = 'stable_MturkTracker'

MIDDLEWARE_CLASSES = tuple(list(MIDDLEWARE_CLASSES) + [
        'pipeline.middleware.MinifyHTMLMiddleware',
])

# Production Mail settings
SERVER_EMAIL = DEFAULT_FROM_EMAIL = 'noreply@MturkTracker'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None

# django sentry
SENTRY_DSN = None
INSTALLED_APPS = INSTALLED_APPS + (
    'raven.contrib.django',
)
