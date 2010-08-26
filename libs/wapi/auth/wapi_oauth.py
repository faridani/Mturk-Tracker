# -*- coding: utf-8 -*-

# Copyright (c) 2008 Alberto García Hierro <fiam@rm-fr.net>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from wapi.auth.base import ApiAuth
from oauth_provider.decorators import CheckOAuth 
from oauth.oauth import OAuthError
from oauth_provider.utils import initialize_server_request, send_oauth_error
    
    
class ApiAuthOAuth(ApiAuth):
    def login(self, request):
        if CheckOAuth.is_valid_request(request):
            try:
                consumer, token, parameters = CheckOAuth.validate_token(request) 
            except OAuthError, e: 
                return  send_oauth_error(e) 
        return None

    def login_required(self, request):
        """Returns a response indicating the user needs to log in"""
        response = HttpResponse(_('Authorization Required'))
        response['WWW-Authenticate'] = 'OAuth realm="%s"' % self.__class__.realm
        response.status_code = 401
        return response
