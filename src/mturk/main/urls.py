from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       url(r'^$','mturk.main.views.index', name='index'), 
)
