from django.conf import settings
from django.conf.urls.defaults import * #This must look like this
from django.contrib import admin
import os

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    ('', include('mturk_crawl.main.urls')),
    (r'^admin/(.*)', admin.site.root),
)

if settings.MEDIA_ROOT != '' and \
   settings.MEDIA_URL.startswith('/') and \
   settings.ADMIN_MEDIA_PREFIX.startswith('/'):
    urlpatterns += patterns('',
        (r'^' + settings.MEDIA_URL[1:] + r'(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        (r'^' + settings.ADMIN_MEDIA_PREFIX[1:] + r'(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.abspath(os.path.join(settings.DJANGO_PATH, 'contrib/admin/media/'))}),
    )