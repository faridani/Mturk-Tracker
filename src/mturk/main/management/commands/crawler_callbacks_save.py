from django.db.models import Model

def callback_database(data, **kwargs):

    if type(data) != type([]):
        raise Exception, '::callback_database() must be called with one list argument'

    for record in data:
        if type(record) == type({}):

            for model,fields in record.items():

                for key,value in fields.items():
                    if isinstance(value, Model):
                        value.save()
                    else:
                        if type(value) == type([]):
                            callback_database(value)

                clazz = __import__('mturk.main.models', {}, {}, [model]).__getattribute__(model)
                obj = clazz(**fields)
                print obj,fields
                obj.save()

        else:
            if isinstance(record, Model):

                record.save()
