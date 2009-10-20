# -*- coding: utf-8 -*-

from django import template

register = template.Library()

def row_formater(input):
    for cc in input:
        date = cc['date']
        row = "new Date(%s,%s,%s,%s,%s)," % (date.year, date.month-1, date.day, date.hour, date.minute)
        row += ",".join(cc['row'])
        yield "["+row+"]"


@register.simple_tag
def google_timeline(context, data):
    '''
    http://code.google.com/apis/visualization/documentation/gallery/annotatedtimeline.html
    
    data.setValue(0,0, new Date(2009,01-1,07,14,00,00));
    data.setValue(0,2, 2310.19);
    data.setValue(0,1, 31144);
    data.setValue(0,3, 765);    
    '''
    return {'data':row_formater(data)}

register.inclusion_tag('graphs/google_timeline.html', takes_context=True)(google_timeline)