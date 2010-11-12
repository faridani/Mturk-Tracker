#!/usr/bin/env python

if __name__ == "__main__":
    import os
    import sys

    my_path = os.path.dirname(os.path.abspath(__file__))

    #Set up PYTHONPATH
    sys.path = [os.path.join(my_path, "libs"),
                os.path.join(my_path, "src")] + sys.path

    while my_path in sys.path:
        sys.path.remove(my_path)

    #Set up the DJANGO_SETTINGS_MODULE
    from django.conf import ENVIRONMENT_VARIABLE

    """
    trying to read settings from env
    """
    settings_path = os.path.join(my_path, ENVIRONMENT_VARIABLE)
    if os.path.isfile(settings_path):
        os.environ[ENVIRONMENT_VARIABLE] = open(settings_path).read().strip()

    """
    --settings opt always is important
    """
    for opt in sys.argv:
        if opt.startswith('--settings='):
            os.environ[ENVIRONMENT_VARIABLE] = opt.replace("--settings=",
'')

    """
    if all fails settings can still be taken from env
    """

    #Import settings
    try:
        print 'Settings: %s' % os.environ[ENVIRONMENT_VARIABLE]
        __mod = __import__(os.environ[ENVIRONMENT_VARIABLE], {}, {}, [''])
    except ImportError, e:
        raise ImportError, "Could not import settings '%s' (Is it on sys.path? Does it have syntax errors?): %s" % (os.environ[ENVIRONMENT_VARIABLE], e)

    from django.core.management import execute_manager
    execute_manager(__mod)
