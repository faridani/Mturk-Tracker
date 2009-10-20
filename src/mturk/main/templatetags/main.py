from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def jquery():
    
    uncompressed = 'false'
    if settings.DEBUG: uncompressed = 'true'
    
    return """<script type="text/javascript">
            google.load("jquery", "1.3.2",{uncompressed:%s});
            google.load("jqueryui", "1.7.2",{uncompressed:%s});
        </script>""" % (uncompressed, uncompressed)