# -*- coding: utf-8 -*-

from django import template
from django.utils import simplejson

import datetime


register = template.Library()

def row_formater(input):
    for cc in input:
        date = cc['date']
        if isinstance(date, datetime.datetime):
            row = "new Date(%s,%s,%s,%s,%s)," % (date.year, date.month-1, date.day, date.hour, date.minute)
        else:
            row = "new Date(%s,%s,%s)," % (date.year, date.month-1, date.day)
        row += ",".join(cc['row'])
        yield "["+row+"]"

def text_row_formater(input):
    for cc in input:

        row = []
        for el in cc:
            if isinstance(el, datetime.datetime):
                row.append("new Date(%s,%s,%s,%s,%s)" % (el.year, el.month-1, el.day, el.hour, el.minute))
            elif isinstance(el, datetime.date):
                row.append("new Date(%s,%s,%s)" % (el.year, el.month-1, el.day))
            elif isinstance(el, datetime.timedelta):
                row.append(str(el.days + (float(el.seconds)/(60*60*24)) ))
            else:
                row.append(simplejson.dumps(el))
        
        print row
        yield "["+','.join(row)+"]"

@register.simple_tag
def google_timeline(context, columns, data):
    '''
    http://code.google.com/apis/visualization/documentation/gallery/annotatedtimeline.html
    '''
    return {'data':row_formater(data), 'columns':columns}

@register.simple_tag
def google_table(context, columns, data):
    return {'data':text_row_formater(data), 'columns':columns}


register.inclusion_tag('graphs/google_timeline.html', takes_context=True)(google_timeline)
register.inclusion_tag('graphs/google_table.html', takes_context=True)(google_table)