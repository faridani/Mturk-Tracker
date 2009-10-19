from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
import os

urlpatterns = patterns('',
    ('', include('mturk.main.urls')),
)

if settings.MEDIA_ROOT != '' and \
   settings.MEDIA_URL.startswith('/'):
    urlpatterns += patterns('',
        (r'^' + settings.MEDIA_URL[1:] + r'(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )