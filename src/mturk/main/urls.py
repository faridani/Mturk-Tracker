from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to

urlpatterns = patterns('',
                       url(r'^$', redirect_to, {'url':'/general/'}),
                       url(r'^general/$','mturk.main.views.general', name='graphs_general'),                       
                       url(r'^about/$',direct_to_template, {'template':'main/about.html'}, name='about'),
                       url(r'^arrivals/$','mturk.main.views.arrivals', name='graphs_arrivals'),
                       url(r'^completed/$','mturk.main.views.completed', name='graphs_completed'),
                       url(r'^top_requesters/$','mturk.main.views.top_requesters', name='graphs_top_requesters'),
                       
                       url(r'^requester_details/(?P<requester_id>[A-Z0-9]+)/$','mturk.main.views.requester_details', name='requester_details'),
                       url(r'^hit/(?P<hit_group_id>[a-fA-Z0-9]+)/$','mturk.main.views.hit_group_details', name='hit_group_details') 
)
