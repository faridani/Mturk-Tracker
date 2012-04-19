import traceback
from wapi.auth.basic import ApiAuthBasic
from django.conf import settings


def grab_error(exc_info):
    return {
        'type': str(exc_info[0].__name__),
        'value': str(exc_info[1]),
        'traceback': unicode(traceback.extract_tb(exc_info[2]))
    }


class MturkApiAuth(ApiAuthBasic):
    '''Always true when in debug mode'''
    def check_password(self, request, realm, user, password):
        if settings.DEBUG:
            return True
        else:
            return user.check_password(password)
