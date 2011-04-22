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
from django.conf import settings
from django.core.cache import cache
from django.views.generic.simple import direct_to_template
from tenclouds.sql import query_to_dicts, query_to_tuples
from django.views.decorators.cache import cache_page
from django.core.urlresolvers import reverse
from mturk.main.templatetags.graph import text_row_formater
from django.shortcuts import get_object_or_404
from mturk.main.models import HitGroupContent

import datetime
import time

import admin
import plot

DEFAULT_COLUMNS =  (
               ('date','Date'),
               ('number','#HITs'),
               ('number','Rewards($)'),
               ('number','#Projects'),
)

ONE_DAY = 60 * 60 * 24
ONE_HOUR = 60 * 60

def data_formater(input):
    for cc in input:
        yield {
                'date': cc['start_time'],
                'row': (str(cc['hits']), str(cc['reward']), str(cc['count'])),
        }

@cache_page(ONE_HOUR)
def general(request):

    params = {
        'multichart': True,
        'columns':DEFAULT_COLUMNS,
        'title': 'General Data'
    }

    if 'date_from' in request.GET:
        date_from = datetime.datetime(
                *time.strptime(request.GET['date_from'], '%m/%d/%Y')[:6])
    else:
        date_from = datetime.datetime.now() - datetime.timedelta(days=7)

    if 'date_to' in request.GET:
        date_to = datetime.datetime(
                *time.strptime(request.GET['date_to'], '%m/%d/%Y')[:6])
    else:
        date_to = datetime.datetime.now()

    params['date_from'] = date_from.strftime('%m/%d/%Y')
    params['date_to'] = date_to.strftime('%m/%d/%Y')

    data = data_formater(query_to_dicts('''
        select reward, hits, projects as "count", start_time
            from main_crawlagregates
            where start_time >= %s and start_time <= %s
            order by start_time asc
        ''', date_from, date_to))

    def _is_anomaly(a, others):
        mid = sum(map(lambda e: int(e['row'][0]), others)) / len(others)
        return abs(mid - int(a['row'][0])) > 7000

    def _fixer(a, others):
        val = sum(map(lambda e: int(e['row'][0]), others)) / len(others)
        a['row'] = (str(val), a['row'][1], a['row'][2])
        return a

    if settings.DATASMOOTHING:
        params['data'] = plot.repair(list(data), _is_anomaly, _fixer, 2)
    else:
        params['data'] = list(data)
    print type(params['data']), len(params['data']), settings.DATASMOOTHING
    return direct_to_template(request, 'main/graphs/timeline.html', params)

@cache_page(ONE_DAY)
def arrivals(request):

    params = {
        'multichart': True,
        'columns':DEFAULT_COLUMNS,
        'title': 'New Tasks/HITs/$$$ per day'
    }

    date_from = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    date_to = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

    if request.method == 'GET' and 'date_from' in request.GET and 'date_to' in request.GET:

        date_from = datetime.datetime(*time.strptime(request.GET['date_from'], '%m/%d/%Y')[:6])
        date_to = datetime.datetime(*time.strptime(request.GET['date_to'], '%m/%d/%Y')[:6])
        params['date_from'] = request.GET['date_from']
        params['date_to'] = request.GET['date_to']

    data = data_formater(query_to_dicts('''
        select date as "start_time", arrivals_hits as "hits", arrivals_reward as "reward", arrivals_projects as "count"
        from main_daystats where day_end_hits != 0 and date >= '%s' and date <= '%s'
    ''' % (date_from,date_to)))

    params['data'] = data

    return direct_to_template(request, 'main/graphs/timeline.html', params)

@cache_page(ONE_DAY)
def completed(request):

    params = {
        'columns': DEFAULT_COLUMNS,
        'title': 'Tasks/HITs/$$$ completed per day'
    }

    date_from = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    date_to = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

    if request.method == 'GET' and 'date_from' in request.GET and 'date_to' in request.GET:

        date_from = datetime.datetime(*time.strptime(request.GET['date_from'], '%m/%d/%Y')[:6])
        date_to = datetime.datetime(*time.strptime(request.GET['date_to'], '%m/%d/%Y')[:6])
        params['date_from'] = request.GET['date_from']
        params['date_to'] = request.GET['date_to']

    data = data_formater(query_to_dicts('''
        select date as "start_time", day_start_hits - day_end_hits as "hits", day_start_reward - day_end_reward as "reward", day_start_projects - day_end_projects as "count"
            from main_daystats where day_end_hits != 0 and date >= '%s' and date <= '%s'
    ''' % (date_from,date_to)))

    params['data'] = data

    return direct_to_template(request, 'main/graphs/timeline.html', params)

def top_requesters(request):
    if request.user.is_superuser:
        return admin.top_requesters(request)


    key = 'TOPREQUESTERS_CACHED'
    # check cache
    data = cache.get(key) or []

    def _top_requesters(request):
        def row_formatter(input):
            for cc in input:
                row = []
                row.append('<a href="%s">%s</a>' % (reverse('requester_details',kwargs={'requester_id':cc[0]}) ,cc[1]))
                row.append('<a href="https://www.mturk.com/mturk/searchbar?requesterId=%s" target="_mturk">%s</a> (<a href="http://feed.crowdsauced.com/r/req/%s">RSS</a>)'
                           % (cc[0],cc[0],cc[0]) )
                row.extend(cc[2:6])
                yield row


        columns = (
            ('string','Requester ID'),
            ('string','Requester'),
            ('number','#Task'),
            ('number','#HITs'),
            ('number','Rewards'),
            ('datetime', 'Last Posted On')
        )
        ctx = {
            'data': data,
            'columns': columns,
            'title': 'Top-1000 Recent Requesters',
        }
        return direct_to_template(request, 'main/graphs/table.html', ctx)

    return _top_requesters(request)

def requester_details(request, requester_id):
    if request.user.is_superuser:
        return admin.requester_details(request, requester_id)

    @cache_page(ONE_DAY)
    def _requester_details(request, requester_id):
        def row_formatter(input):

            for cc in input:
                row = []
                row.append('<a href="%s">%s</a>' % (reverse('hit_group_details',kwargs={'hit_group_id':cc[5]}) ,cc[0]))
                row.extend(cc[1:5])
                yield row

        requster_name = HitGroupContent.objects.filter(requester_id = requester_id).values_list('requester_name',flat=True).distinct()

        if requster_name: requster_name = requster_name[0]
        else: requster_name = requester_id

        date_from = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()

        data = query_to_tuples("""
    select
        title,
        hits_available,
        p.reward,
        p.occurrence_date,
        (select end_time from main_crawl where id = (select max(crawl_id) from main_hitgroupstatus where group_id = q.group_id and hit_group_content_id = p.group_content_id)) - p.occurrence_date,
        p.group_id
    from main_hitgroupfirstoccurences p join main_hitgroupcontent q on ( p.group_content_id = q.id and p.requester_id = q.requester_id )
    where
        p.requester_id = '%s'
        and q.is_public = true
        and p.occurrence_date > TIMESTAMP '%s' and
        q.occurrence_date > TIMESTAMP '%s';
        """ % (requester_id, date_from, date_from))

        columns = [
            ('string', 'HIT Title'),
            ('number', '#HITs'),
            ('number', 'Reward'),
            ('datetime', 'Posted'),
            ('number', 'Duration (Days)'),
        ]
        ctx = {
            'data': text_row_formater(row_formatter(data)),
            'columns': tuple(columns),
            'title':'Last 100 Tasks posted by %s' % (requster_name),
            'user': request.user,
        }
        return direct_to_template(request, 'main/requester_details.html',ctx)

    return _requester_details(request, requester_id)

cache_page(ONE_DAY)
def hit_group_details(request, hit_group_id):

    hit = get_object_or_404(HitGroupContent, group_id = hit_group_id)

    return direct_to_template(request, 'main/hit_group_details.html', {'hit':hit})

def search(request):

    params = {}

    if request.method == 'POST' and 'query' in request.POST:
        params['query'] = request.POST['query']

    return direct_to_template(request, 'main/search.html', params)

