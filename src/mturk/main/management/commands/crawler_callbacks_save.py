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
from django.db.models import Model

import logging
import sys
import traceback

from crawler_common import grab_error

##########################################################################################
# saves data in a database.
#
# In:
#  pages - list of page numbers
##########################################################################################
def callback_database(data, **kwargs):

    errors = []

    ######################################################################################
    # Saves a given model.
    #
    # In:
    #  model - instance of aModel object
    ######################################################################################
    def save(model):
        fields = {}
        
        for field in model._meta.get_all_field_names():
            
            #if model._meta.get_field_by_name(field)[0].__class__.__name__ == 'DateTimeField':
            #    continue
                
            # Interested only in possibly most defining fields
            if 'id' in field and field != 'id' and field != 'first_crawl':
                try:
                    value = model.serializable_value(field)
                    fields[field] = value
                except:
                    pass 
                    
        clazz = __import__('mturk.main.models', {}, {},
                        [model.__class__.__name__]).__getattribute__(model.__class__.__name__)
        
        try:
            obj = clazz.objects.get(**fields)
            return obj
        except clazz.MultipleObjectsReturned:
            model.save()
            return model
        except clazz.DoesNotExist:
            model.save()
            return model

    ######################################################################################
    # Saves any Model object nested in the given record. (Currently unused)
    #
    # In:
    #  fields - dictionary representing a record
    ######################################################################################
    def save_recursively(fields):
        for key in fields.keys():
            if isinstance(fields[key], Model):
                fields[key] = save(fields[key])
            #else:
            #    if type(fields[key]) == type([]):
            #        callback_database(fields[key])
        return fields

    if type(data) != type([]):
        raise Exception, '::callback_database() must be called with one list argument'

    logging.debug('Saving results to database (%s records)' % len(data))   
    
    for record in data:
        try:
            if type(record) == type({}):

                for model in record.keys():
                    try:

                        record[model] = save_recursively(record[model])

                        clazz = __import__('mturk.main.models', {}, {}, 
                                           [model]).__getattribute__(model)
                        obj = clazz(**record[model])
                        try:
                            obj.save()
                        except:
                            for key,value in record[model].items():
                                if isinstance(value, Model):
                                    try: # value may be not saved in save_recursively because it is in DB already
                                        value.delete()
                                    except:
                                        pass
                            raise Exception("Failed to save object with values:\n%s" % fields), None, sys.exc_info()[2]
                            
                    except:
                        errors.append(grab_error(sys.exc_info()))
            else:
                if isinstance(record, Model):

                    save(record)
        
        except:
            errors.append(grab_error(sys.exc_info()))
    
    return ([],errors)
