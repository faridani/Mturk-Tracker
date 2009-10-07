# -*- coding: utf-8 -*-
from django.db.models import Model

import logging
import sys
import traceback

from crawler_common import grab_error

def callback_database(data, **kwargs):

    errors = []

    def save(model):
        try:
            model.save()
        except:
            raise Exception("Failed to save object:\n%s" % model.values()), None, sys.exc_info()[2]

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

                        #save_recursively(fields)

                        clazz = __import__('mturk.main.models', {}, {}, [model]).__getattribute__(model)
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
