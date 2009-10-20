from django.views.generic.simple import direct_to_template
from tenclouds.sql import query_to_dicts

def general(request):

    '''
    Hits, Rewards, Projects from start by crawl
    select sum(reward), sum(hits_available), count(*), (select start_time from main_crawl where main_crawl.id = p.crawl_id) as "start_time" 
        from hits_mv p 
        group by crawl_id 
        order by crawl_id asc;
    '''
    
    data = query_to_dicts('''
        select sum(reward), sum(hits_available), count(*), (select start_time from main_crawl where main_crawl.id = p.crawl_id) as "start_time" 
            from hits_mv p 
            group by crawl_id 
            order by crawl_id asc    
    ''')
    
    for cc in data:
        print cc
    
    return direct_to_template(request, 'main/graphs/general.html', locals())