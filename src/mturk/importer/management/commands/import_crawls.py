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
from django.core.management.base import BaseCommand
from mturk.importer.management.commands import write_counter, get_counter
from django.conf import settings
from mturk.main.models import Crawl
import time
import datetime
import os
from django.db import transaction


class Command(BaseCommand):
    help = 'Import crawls into db'

    def handle(self, **options):
        '''
        Sample data:
??crawl_id;start_time;end_time;sucess;error_if_any;day;month;year;dayofweek;datestring
1;2009-01-07 14:00:00;2009-01-07 14:02:51;YES;NO;7;1;2009;4;2009.01.07
2;2009-01-07 15:00:00;2009-01-07 15:02:27;YES;NO;7;1;2009;4;2009.01.07
3;2009-01-07 16:00:01;2009-01-07 16:02:17;YES;NO;7;1;2009;4;2009.01.07
4;2009-01-07 17:00:00;2009-01-07 17:02:49;YES;NO;7;1;2009;4;2009.01.07


model:
    start_time          = models.DateTimeField('Start Time')
    end_time            = models.DateTimeField('End Time')
    success             = models.BooleanField('Successfoul crawl?')
    groups_downloaded   = models.IntegerField('Groups downloaded')
    errors              = JSONField('Errors', blank=True, null=True)
    old_id              = models.IntegerField(null=True,blank=True)
        '''
        
        try:
            f = open(os.path.join(settings.ROOT_PATH,'data','crawl.utf8.csv'),"rb")
            f.readline()
            
            transaction.enter_transaction_management()
            transaction.managed(True)
        
            i = 0
        
            for row in f:
                row = unicode(row)
                row = row.strip()
                row = row.split(';')
                if len(row) == 10:
                    obj = Crawl(**{
                            'old_id':int(row[0]),
                            'start_time': datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S"),
                            'end_time': datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S"),
                            'success': True if row[3] == 'YES' else False,
                            'groups_downloaded':0
                            })
                    #obj.save()
                    i = i+1
                    
                    if row[3] == 'NO': print row[0]
                    
            #transaction.commit()
            print 'saved %s rows' % i
        except KeyboardInterrupt:
            transaction.rollback()
            exit()