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
from base import *
import logging
import sys

DATABASE_NAME = 'mturk_crawl'
DEBUG=False

USE_CACHE=True
SOLR_MAIN = "http://localhost:8983/solr/en"

LOG_DIRECTORY = '/var/log/mturk/'


FORMAT = '%(asctime)s %(levelname)s %(message)s' 
formatter = logging.Formatter(FORMAT)

logging.basicConfig(
    level = logging.INFO,
    format = FORMAT,
    filename = LOG_DIRECTORY + 'crawl.log',
    filemode = 'a'
)

stdout_log_handler = logging.StreamHandler(sys.stdout)
stdout_log_handler.setFormatter(formatter)

_log = logging.getLogger()
_log.addHandler(stdout_log_handler)


CACHE_BACKEND = 'memcached://127.0.0.1:11211/'