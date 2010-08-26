from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required, user_passes_test

def test_client(request):
    
    return direct_to_template(request, 'api/test_client.html', locals())