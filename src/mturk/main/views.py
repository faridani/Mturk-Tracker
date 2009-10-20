from django.views.generic.simple import direct_to_template
from tenclouds.sql import query_to_dicts

def general(request):

    '''
    Hits, Rewards, Projects from start by crawl
    '''

    def data_formater(input):
        for cc in input:
            yield {'date': cc['date'], 'row':(str(cc['hits']), str(cc['reward']), str(cc['count']),)}
        return
    
    data = data_formater(query_to_dicts('''
        select sum(reward*hits_available) as "reward", sum(hits_available) as "hits", count(*) as "count", (select start_time from main_crawl where main_crawl.id = p.crawl_id) as "date" 
            from hits_mv p 
            group by crawl_id 
            order by crawl_id asc    
    '''))
            
    return direct_to_template(request, 'main/graphs/general.html', {'data':data})