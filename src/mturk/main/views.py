from django.views.generic.simple import direct_to_template

def general(request):

    '''
    Hits, Rewards, Projects from start by crawl
    '''
    
    
    
    return direct_to_template(request, 'main/graphs/general.html', locals())