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

"""Different bindings for Wapi. This version only includes ReST"""
"""Modified to support caching"""

from copy import copy

from django.http import Http404
from django.conf import settings

from wapi.responses import get_response
from wapi.formatters import UnknownFormat
from wapi.exceptions import ApiError, ApiLoginRequired
from wapi.function import ApiFunction
from wapi.utils import api_iterate, get_instance
from django.core.cache import cache
from django.conf import settings
import hashlib
from django.utils.cache import patch_response_headers

def build_api_cache_key(method_name, request):
    
    params = [ method_name, request.method ]

    for k,v in request.REQUEST.items():
        params.extend([k,v])

    return hashlib.md5(':'.join(params).encode('utf-8')).hexdigest() 

class Binding(object):
    """Base class for all Wapi bindings"""
    def __init__(self, api):
        self.api = get_instance(api)
        self.registry = {
            'read': {},
            'write': {},
        }
        for func in api_iterate(api):
            registered_name = self.mangle_name(func.func_name)
            apifunc = ApiFunction(func)
            if settings.DEBUG or apifunc.is_read:
                self.registry['read'][registered_name] = apifunc
            if settings.DEBUG or apifunc.is_write:
                self.registry['write'][registered_name] = apifunc

    def mangle_name(self, name):
        """Modifies the function name which gets exposed"""
        return name

    def get_method(self, read_or_write, method_name):
        try:
            return self.registry[read_or_write][method_name]
        except KeyError:
            raise Http404('Method "%s" not found' % method_name)

class RestBinding(Binding):
    """Exposes an API trough ResT"""
    PATTERN = '(?P<method_name>.*)\.(?P<format>\w+)'
    READ_WRITE_MAPPING = {
        'GET': 'read',
        'POST': 'write',
        'DELETE': 'write',
        'PUT': 'write'
    }
    def __init__(self, api, auth=None):
        super(RestBinding, self).__init__(api)
        self.auth = get_instance(auth)

    def mangle_name(self, name):
        return name.replace('__', '/')

    def __call__(self, request, method_name, format):
        """Searchs the method, calls it and transforms the response
            into a serialized format"""
        if self.auth:
            response = self.auth.login(request)
            if response:
                return response

        try:
            response_cls = get_response(format)
        except UnknownFormat:
            raise Http404('No registered serializer for format "%s"' % format)

        try:
            method = self.get_method(self.READ_WRITE_MAPPING[request.method],
                method_name)
        except KeyError:
            raise Http404('Method "%s" not found' % method_name)

        try:
            if request.method == 'POST':
                data = copy(request.POST)
            else:
                data = copy(request.GET)
            
            if settings.USE_CACHE:
                cache_key = build_api_cache_key(method_name, request)
                func_val = cache.get(cache_key)
                if func_val is None:
                    func_val = method(request, data)
                    cache.set(cache_key, func_val, settings.API_CACHE_TIMEOUT)
            else:
                func_val = method(request, data)
                
            response = func_val
        except ApiLoginRequired:
            return self.auth.login_required(request)
        except ApiError, e:
            return e.get_response()

        response.kwargs['request'] = request
        ret = response.transform(response_cls)
        
        if settings.USE_CACHE:
            patch_response_headers(ret, settings.API_CACHE_TIMEOUT)            

        
        return ret
