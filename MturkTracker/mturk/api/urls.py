from django.conf.urls.defaults import url, patterns

from wapi.bindings import RestBinding

from mturk.api import  MturkApiAuth
from mturk.api.search import SearchApi

urlpatterns = patterns('mturk.api.views',
   
    url(r'^$','test_client', name='api_test_client'),   
    url(r'1.0/search/%s$' % RestBinding.PATTERN, RestBinding(auth=MturkApiAuth(), api=SearchApi()))
)