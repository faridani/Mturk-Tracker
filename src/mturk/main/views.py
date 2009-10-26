from django.views.generic.simple import direct_to_template
from tenclouds.sql import query_to_dicts, query_to_tuples
from django.views.decorators.cache import cache_page
import datetime

DEFAULT_COLUMNS =  (
               ('date','Date'),
               ('number','#HITs'),
               ('number','Rewards($)'),
               ('number','#Projects'),
)

ONE_DAY = 60 * 60 * 24

def data_formater(input):
    for cc in input:
        yield {'date': cc['start_time'], 'row':(str(cc['hits']), str(cc['reward']), str(cc['count']),)}
    return


@cache_page(ONE_DAY)
def general(request):
    
    data = data_formater(query_to_dicts('''
        select sum(reward*hits_available) as "reward", sum(hits_available) as "hits", count(*) as "count", start_time 
            from hits_mv p 
            group by crawl_id, start_time
            order by crawl_id asc    
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
            from main_daystats
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
            from main_daystats
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
            row.append('%s' % cc[1])
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
where p.occurrence_date > TIMESTAMP '%s'
group by p.requester_id, p.requester_name
order by sum(q.hits_available*p.reward) desc;    
''' % (datetime.date.today() - datetime.timedelta(days=30)).isoformat())) 
    
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