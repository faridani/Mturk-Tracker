from django.views.generic.simple import direct_to_template
from tenclouds.sql import query_to_dicts
from django.views.decorators.cache import cache_page

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

    