from django.views.generic.simple import direct_to_template
from tenclouds.sql import query_to_dicts, query_to_tuples
from django.views.decorators.cache import cache_page
from django.core.urlresolvers import reverse
from mturk.main.templatetags.graph import text_row_formater
from django.shortcuts import get_object_or_404
from mturk.main.models import HitGroupContent
import datetime

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
        yield {'date': cc['start_time'], 'row':(str(cc['hits']), str(cc['reward']), str(cc['count']),)}
    return


@cache_page(ONE_HOUR)
def general(request):
    
    data = data_formater(query_to_dicts('''
        select reward, hits, projects as "count", start_time 
            from main_crawlagregates 
            order by start_time asc    
    '''))
            
    return direct_to_template(request, 'main/graphs/timeline.html', {
                                                                    'data':data, 
                                                                    'columns':DEFAULT_COLUMNS,
                                                                    'title': 'General Data'
    })

@cache_page(ONE_DAY)
def arrivals(request):
    
    data = data_formater(query_to_dicts('''
        select date as "start_time", arrivals_hits as "hits", arrivals_reward as "reward", arrivals_projects as "count"
            from main_daystats where day_end_hits != 0
    '''))
    
    return direct_to_template(request, 'main/graphs/timeline.html', {
                                                                     'data':data, 
                                                                     'columns':DEFAULT_COLUMNS, 
                                                                     'title': 'New Tasks/HITs/$$$ per day'
    })
    
@cache_page(ONE_DAY)
def completed(request):
    
    data = data_formater(query_to_dicts('''
        select date as "start_time", day_start_hits - day_end_hits as "hits", day_start_reward - day_end_reward as "reward", day_start_projects - day_end_projects as "count"
            from main_daystats where day_end_hits != 0
    '''))
    
    return direct_to_template(request, 'main/graphs/timeline.html', {
                                                                     'data':data, 
                                                                     'columns':DEFAULT_COLUMNS, 
                                                                     'title': 'Tasks/HITs/$$$ completed per day'
    })
    
@cache_page(ONE_DAY)
def top_requesters(request):
    
    def row_formatter(input):

        for cc in input:
            row = []
            row.append('<a href="%s">%s</a>' % (reverse('requester_details',kwargs={'requester_id':cc[0]}) ,cc[1]))
            
            row.append('<a href="https://www.mturk.com/mturk/searchbar?requesterId=%s" target="_mturk">%s</a> (<a href="http://feed.crowdsauced.com/r/req/%s">RSS</a>)'
                       % (cc[0],cc[0],cc[0]) )
            row.extend(cc[2:6])
            
            yield row
    
    data = row_formatter(query_to_tuples('''
select    
    p.requester_id, 
    p.requester_name, 
    count(*) as "projects", 
    sum(q.hits_available) as "hits", 
    sum(q.hits_available*p.reward) as "reward",
    max(p.occurrence_date) as "last_posted"
from main_hitgroupcontent p join main_hitgroupstatus q 
    on( p.first_crawl_id = q.crawl_id and q.hit_group_content_id = p.id )
where 
    p.occurrence_date > TIMESTAMP '%s'
    and q.crawl_id in ( select id from main_crawl where start_time > TIMESTAMP '%s')
group by p.requester_id, p.requester_name
order by sum(q.hits_available*p.reward) desc;    
''' % (
        (datetime.date.today() - datetime.timedelta(days=30)).isoformat(),
        (datetime.date.today() - datetime.timedelta(days=33)).isoformat()
        )
)) 
    
    columns = (('string','Requester ID'),
               ('string','Requester'),
               ('number','#Task'),
               ('number','#HITs'),
               ('number','Rewards'),
               ('datetime', 'Last Posted On'))

    return direct_to_template(request, 'main/graphs/table.html', {
                                                                  'data':data,
                                                                  'columns':columns,
                                                                  'title':'Top-1000 Recent Requesters'
                                                                  })
@cache_page(ONE_DAY)    
def requester_details(request, requester_id):


    def row_formatter(input):

        for cc in input:
            row = []
            row.append('<a href="%s">%s</a>' % (reverse('hit_group_details',kwargs={'hit_group_id':cc[5]}) ,cc[0]))
            row.extend(cc[1:5])
            
            yield row

    requster_name = HitGroupContent.objects.filter(requester_id = requester_id).values_list('requester_name',flat=True).distinct() 
    
    if requster_name: requster_name = requster_name[0]
    else: requster_name = requester_id

    data = query_to_tuples("""
select
    title, 
    hits_available, 
    reward, 
    occurrence_date, 
    (select end_time from main_crawl where id = (select max(crawl_id) from main_hitgroupstatus where group_id = q.group_id and hit_group_content_id = p.id)) - occurrence_date,
    p.group_id
from main_hitgroupcontent p join main_hitgroupstatus q 
    on( q.hit_group_content_id = p.id and p.first_crawl_id = q.crawl_id )
where 
    requester_id = '%s';    
    """ % requester_id)
    
    columns = (('string', 'HIT Title'),
               ('number', '#HITs'),
               ('number', 'Reward'),
               ('datetime', 'Posted'),
               ('number', 'Duration (Days)'))
        
    return direct_to_template(request, 'main/requester_details.html',{
                                                                      'data':text_row_formater(row_formatter(data)),
                                                                      'columns':columns,
                                                                      'title':'Last 100 Tasks posted by %s' % (requster_name)
                                                                      })
cache_page(ONE_DAY)
def hit_group_details(request, hit_group_id):
    
    hit = get_object_or_404(HitGroupContent, group_id = hit_group_id)
    
    return direct_to_template(request, 'main/hit_group_details.html', {'hit':hit})