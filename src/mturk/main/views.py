from django.views.generic.simple import direct_to_template
from tenclouds.sql import query_to_dicts
from django.views.decorators.cache import cache_page

@cache_page(60 * 60 * 24)
def general(request):

    '''
    Hits, Rewards, Projects from start by crawl
    '''

    def data_formater(input):
        for cc in input:
            yield {'date': cc['start_time'], 'row':(str(cc['hits']), str(cc['reward']), str(cc['count']),)}
        return
    
    columns = (
               ('date','Date'),
               ('number','#HITs'),
               ('number','Rewards($)'),
               ('number','#Projects'),
               )
    
    data = data_formater(query_to_dicts('''
        select sum(reward*hits_available) as "reward", sum(hits_available) as "hits", count(*) as "count", start_time 
            from hits_mv p 
            group by crawl_id, start_time
            order by crawl_id asc    
    '''))
            
    return direct_to_template(request, 'main/graphs/general.html', {'data':data, 'columns':columns})