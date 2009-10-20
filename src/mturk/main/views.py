from django.views.generic.simple import direct_to_template

def general(request):

    
    
    return direct_to_template(request, 'main/graphs/general.html', locals())