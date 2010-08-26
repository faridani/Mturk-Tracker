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
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to

urlpatterns = patterns('',
                       url(r'^$', redirect_to, {'url':'/general/'}),
                       url(r'^general/$','mturk.main.views.general', name='graphs_general'),                      
                       url(r'^about/$',direct_to_template, {'template':'main/about.html'}, name='about'),
                       url(r'^arrivals/$','mturk.main.views.arrivals', name='graphs_arrivals'),
                       url(r'^completed/$','mturk.main.views.completed', name='graphs_completed'),
                       url(r'^top_requesters/$','mturk.main.views.top_requesters', name='graphs_top_requesters'),

                       #url(r'^search/$', direct_to_template, {'template':'main/search.html'}, name='search'),
                       url(r'^search/$', 'mturk.main.views.search', name='search'),
                       
                       url(r'^requester_details/(?P<requester_id>[A-Z0-9]+)/$','mturk.main.views.requester_details', name='requester_details'),
                       url(r'^hit/(?P<hit_group_id>[a-fA-Z0-9]+)/$','mturk.main.views.hit_group_details', name='hit_group_details') 
)
