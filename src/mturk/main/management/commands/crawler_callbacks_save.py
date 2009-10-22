# -*- coding: utf-8 -*-

# Konrad Adamczyk (conrad.adamczyk at gmail.com)

# Changelog:
# 07.10.2009:	First release

##########################################################################################

# Functions saving data fetched from a Amazon Mechanical Turk (mturk.com) service.

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
        try:
            fields = {}
            for field in model._meta.get_all_field_names():
                
                if model._meta.get_field_by_name(field).__class__.__name__ == 'DateTimeField':
                    continue
                
                if field != 'id':
                    try:
                        value = model.serializable_value(field)
                        if len(str(value)) <= 500:
                            fields[field] = model.serializable_value(field)
                    except:
                        pass 
                    
            clazz = __import__('mturk.main.models', {}, {},
                        [model.__class__.__name__]).__getattribute__(model.__class__.__name__)
            
            try:
                obj = clazz.objects.get(**fields)
            except clazz.DoesNotExist:
                model.save()
                
        except:
            raise Exception("Failed to save object:\n%s" % model.values()), None, sys.exc_info()[2]

    ######################################################################################
    # Saves any Model object nested in the given record. (Currently unused)
    #
    # In:
    #  fields - dictionary representing a record
    ######################################################################################
    def save_recursively(fields):
        for key,value in fields.items():
            if isinstance(value, Model):
                    save(value)
            else:
                if type(value) == type([]):
                    callback_database(value)

    if type(data) != type([]):
        raise Exception, '::callback_database() must be called with one list argument'

    logging.debug('Saving results to database (%s records)' % len(data))   
    
    for record in data:
        try:
            if type(record) == type({}):

                for model,fields in record.items():
                    try:

                        save_recursively(fields)

                        clazz = __import__('mturk.main.models', {}, {}, 
                                           [model]).__getattribute__(model)
                        obj = clazz(**fields)
                        try:
                            obj.save()
                        except:
                            for key,value in fields.items():
                                if isinstance(value, Model):
                                    value.delete()
                            raise Exception("Failed to save object with values:\n%s" % fields), None, sys.exc_info()[2]
                            
                    except:
                        errors.append(grab_error(sys.exc_info()))
            else:
                if isinstance(record, Model):

                    save(record)
        
        except:
            errors.append(grab_error(sys.exc_info()))
    
    return ([],errors)
