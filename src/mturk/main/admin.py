# -*- coding: utf-8 -*-

import datetime

from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from tenclouds.sql import query_to_tuples
from mturk.main.templatetags.graph import text_row_formater
from models import RequesterProfile, HitGroupContent



def no_cache(view):
    """Decorator that disables any cache for view

    Instead of setting headers and other boring stuff, use django decorator
    with 0 cache timeout
    """
    wrapper = cache_page(0)
    return wrapper(view)


@login_required
@no_cache
def top_requesters(request):

    def row_formatter(input):
        "Yield formatted rows"
        for cc in input:
            row = []
            url = reverse('requester_details', kwargs={'requester_id':cc[0]})
            row.append('<a href="%s">%s</a>' % (url, cc[1]))
            row.append('<a href="https://www.mturk.com/mturk/searchbar?requesterId=%s" target="_mturk">%s</a> (<a href="http://feed.crowdsauced.com/r/req/%s">RSS</a>)'
                       % (cc[0],cc[0],cc[0]) )
            row.extend(cc[2:6])
            url = reverse('admin-toggle-requester-status', args=(cc[0], ))
            row.append('<a href="%s">%s</a>' % (url, cc[6] and 'public' or 'private'))
            yield row

    date_30_days_before = datetime.date.today() - datetime.timedelta(days=30)
    data = row_formatter(query_to_tuples('''
            SELECT
                h.requester_id,
                h.requester_name,
                count(*) as "projects",
                sum(h.hits_available) as "hits",
                sum(h.hits_available*reward) as "reward",
                max(h.occurrence_date) as "last_posted",
                coalesce(p.is_public, true) as is_public
            FROM
                main_hitgroupfirstoccurences h
                    LEFT JOIN main_requesterprofile p ON h.requester_id = p.requester_id
            WHERE
                h.occurrence_date > %s
            GROUP BY
                h.requester_id, h.requester_name, p.is_public
            ORDER BY
                sum(h.hits_available*reward)
                DESC
            LIMIT 1000;
            ''', date_30_days_before))

    columns = (
        ('string','Requester ID'),
        ('string','Requester'),
        ('number','#Task'),
        ('number','#HITs'),
        ('number','Rewards'),
        ('datetime', 'Last Posted On'),
        ('string', 'Status'),
    )
    ctx = {
        'data': data,
        'columns': columns,
        'title': 'Top-1000 Recent Requesters',
    }
    return direct_to_template(request, 'main/graphs/table.html', ctx)

@login_required
@no_cache
def toggle_requester_status(request, id):
    """Toggle given requester private/public status"""
    rp, created = RequesterProfile.objects.get_or_create(requester_id=id)
    rp.is_public = not rp.is_public
    rp.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@no_cache
def requester_details(request, requester_id):
    def row_formatter(input):
        for cc in input:
            row = []
            url = reverse('hit_group_details',kwargs={'hit_group_id':cc[5]})
            row.append('<a href="%s">%s</a>' % (url, cc[0]))
            row.extend(cc[1:5])
            url = reverse('admin-toggle-hitgroup-status', args=(cc[5],))
            row.append('<a href="%s">%s</a>' % (url, cc[6] and 'public' or 'private'))
            yield row

    requster_name = HitGroupContent.objects.filter(requester_id=requester_id)
    requster_name = requster_name.values_list('requester_name',flat=True).distinct()

    if requster_name:
        requster_name = requster_name[0]
    else:
        requster_name = requester_id

    date_from = datetime.date.today() - datetime.timedelta(days=30)
    data = query_to_tuples("""
        SELECT
            title, hits_available, p.reward, p.occurrence_date,
            (SELECT end_time FROM main_crawl WHERE id = (SELECT max(crawl_id) FROM main_hitgroupstatus WHERE group_id = q.group_id AND hit_group_content_id = p.group_content_id)) - p.occurrence_date, p.group_id, q.is_public
        FROM
            main_hitgroupfirstoccurences p
                JOIN main_hitgroupcontent q ON (p.group_content_id = q.id AND p.requester_id = q.requester_id)
        WHERE
            p.requester_id = %s
            AND p.occurrence_date > %s
            AND q.occurrence_date > %s
        """, requester_id, date_from, date_from)

    columns = (
        ('string', 'HIT Title'),
        ('number', '#HITs'),
        ('number', 'Reward'),
        ('datetime', 'Posted'),
        ('number', 'Duration (Days)'),
        ('string', 'Status'),
    )

    ctx = {
        'data': text_row_formater(row_formatter(data)),
        'columns': tuple(columns),
        'title': 'Last 100 Tasks posted by %s' % requster_name,
        'user': request.user,
    }
    return direct_to_template(request, 'main/requester_details.html', ctx)

@login_required
@no_cache
def toggle_hitgroup_status(request, id):
    """Toggle given hitgroup public/private status, where id is the amazon hash key)
    """
    hg = get_object_or_404(HitGroupContent, group_id=id)
    hg.is_public = not hg.is_public
    hg.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
