def callback_database(data, **kwargs):

    if type(data) != type([]):
        raise Exception, '::callback_database() must be called with one list argument'

    for record in data:
        for model,fields in record.items():
            print "\n-------------------------------------\n"
            print model
            print fields

            clazz = __import__('mturk.main.models', {}, {}, [model]).__getattribute__(model)
            obj = clazz(**fields)
            obj.save()