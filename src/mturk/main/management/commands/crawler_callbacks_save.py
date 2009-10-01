from django.db.models import Model

import logging
import sys

def callback_database(data, **kwargs):

    def save_recursively(fields):
        for key,value in fields.items():
            if isinstance(value, Model):
                value.save()
            else:
                if type(value) == type([]):
                    callback_database(value)

    if type(data) != type([]):
        raise Exception, '::callback_database() must be called with one list argument'

    logging.debug('Saving results to database')   

    for record in data:
        if type(record) == type({}):

            for model,fields in record.items():

                save_recursively(fields)

                clazz = __import__('mturk.main.models', {}, {}, [model]).__getattribute__(model)
                obj = clazz(**fields)
                try:
                    obj.save()
                except Exception, e:
                    for key,value in fields.items():
                        if isinstance(value, Model):
                            value.delete()
                    raise Exception("Failed to save object with values:\n%s" % fields), None, sys.exc_info()[2]

        else:
            if isinstance(record, Model):

                record.save()
