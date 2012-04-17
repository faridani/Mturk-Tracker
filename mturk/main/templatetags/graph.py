'''
Copyright (c) 2009 Panagiotis G. Ipeirotis

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

Initially designed and created by 10clouds.com, contact at 10clouds.com
'''
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
            elif isinstance(el, float):
                row.append("%.2f" % el)
            elif isinstance(el, datetime.timedelta):
                row.append("%.2f" % ( el.days + (float(el.seconds)/(60*60*24) ) ))
            else:
                row.append(simplejson.dumps(el))

        yield "["+','.join(row)+"]"

@register.simple_tag
def google_timeline(context, columns, data, multirow=False):
    '''
    http://code.google.com/apis/visualization/documentation/gallery/annotatedtimeline.html
    '''
    ctx = {
            'data': row_formater(data),
            'columns': columns,
            'multichart': context.get('multichart', False),
        }
    return ctx

@register.simple_tag
def google_table(context, columns, data):
    return {'data':text_row_formater(data), 'columns':columns}


register.inclusion_tag('graphs/google_timeline.html', takes_context=True)(google_timeline)
register.inclusion_tag('graphs/google_table.html', takes_context=True)(google_table)
