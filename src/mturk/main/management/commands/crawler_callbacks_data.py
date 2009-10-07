# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup, ResultSet
from tenclouds.text import fuse, remove_whitespaces, strip_html

import datetime
import logging
import re
import sys
import traceback
import urllib2

from crawler_common import get_allhit_url, get_group_url, grab_error
from mturk.main.models import HitGroupContent

def callback_allhit(pages, **kwargs):

    if type(pages) != type([]):
        raise Exception, '::callback_allhit() must be called with one list argument'

    def remove_newline_fields(list):
        while True:
            try:    list.remove("\n")
            except: break
        return list

    def is_soup(object):
        if type(object) == type(BeautifulSoup()) or type(object) == type(ResultSet('')):
            return True
        return False

    data = []
    errors = []

    for page_number in pages:
        try:
            logging.debug("Downloading page: %s" % page_number)
            response = urllib2.urlopen(get_allhit_url(page_number))
            html = response.read()
            soup = BeautifulSoup(html)

            table = soup.find('table', cellpadding='0', cellspacing='5', border='0', width='100%')
            table.contents = remove_newline_fields(table.contents)

            hits_available = soup.find('b', style='display:block;color:#CC6600')
            if is_soup(hits_available):
                hits_available = hits_available.contents[0]
                hits_available = int(re.sub(',', '', hits_available[:hits_available.index(' ')]))

            for i_group in range(0,len(table.contents)):

                group_html = table.contents[i_group]

                title = group_html.find('a', {'class':'capsulelink'})
                if is_soup(title):
                    try:
                        title = str(title.contents[0])
                    except:
                        title = unicode(title.contents[0])
                    title = unicode(remove_whitespaces(title))

                group_id = group_html.find('span', {'class':'capsulelink'})
                if is_soup(group_id):
                    group_id = remove_newline_fields(group_id.contents)[0]
                    if 'href' in group_id._getAttrMap():
                        start = group_id['href'].index('groupId=')+8
                        stop = group_id['href'].index('&')
                        group_id = group_id['href'][start:stop]
                    else:
                        group_id = '0'

                fields = group_html.findAll('td', {'align':'left','valign':'top','class':'capsule_field_text'})

                if is_soup(fields):

                    requester_html = remove_newline_fields(fields[0].contents)[0]
                    requester_name = unicode(requester_html.contents[0])
                    requester_id = requester_html['href']
                    start = requester_id.index('requesterId=')+12
                    stop = requester_id.index('&state')
                    requester_id = requester_id[start:stop]

                    hit_expiration_date = remove_newline_fields(fields[1].contents)[0]
                    hit_expiration_date = remove_whitespaces(strip_html(hit_expiration_date))
                    hit_expiration_date = hit_expiration_date[:hit_expiration_date.index('(')-2]
                    hit_expiration_date = datetime.datetime.strptime(hit_expiration_date, '%b %d, %Y')

                    time_alloted = remove_newline_fields(fields[2].contents)[0]
                    time_alloted = remove_whitespaces(strip_html(time_alloted))
                    time_alloted = int(time_alloted[:time_alloted.index(' ')])

                    reward = float(remove_newline_fields(fields[3].contents)[0][1:])

                    description = unicode(remove_newline_fields(fields[5].contents)[0])

                    keywords_raw = remove_newline_fields(fields[6].contents)
                    keywords = []
                    for i in range(0, len(keywords_raw)):
                        try:
                            keyword = keywords_raw[i].contents[0]
                            keywords.append(keyword)
                        except:
                            continue
                    keywords = unicode(fuse(keywords, ','))
                    
                    hit_group_content = None
                    try:
                        hit_group_content = HitGroupContent.objects.get(group_id=group_id, requester_id=requester_id, title=title)
                        print "Got %s: %s, %s" % (group_id,requester_id,title)
                    except HitGroupContent.DoesNotExist: 
                        print "Creating %s: %s, %s" % (group_id,requester_id,title)
                        hit_group_content = HitGroupContent(**{
                                'title': title,
                                'requester_id': requester_id,
                                'requester_name': requester_name,
                                'time_alloted': time_alloted,
                                'reward': reward,
                                'description': description,
                                'keywords': keywords,
                                'group_id': group_id
                            })
                        hit_group_content.save()

                    data.append({
                        'HitGroupStatus': {
                            'group_id': group_id,
                            'hits_available': hits_available,
                            'page_number': page_number,
                            'inpage_position': i_group+1,
                            'hit_expiration_date': hit_expiration_date,
                            'hit_group_content': hit_group_content
                        }
                    })

        except:
            logging.error("Failed to process page %d" % (page_number))
            errors.append(grab_error(sys.exc_info()))

    return (data,errors)

    
def callback_details(data, **kwargs):

    if type(data) != type([]):
        raise Exception, '::callback_allhit() must be called with one list argument'
        
    errors = []

    for i in range(0, len(data)):
        group_id = data[i]['HitGroupStatus']['group_id']
        if group_id != '0':
            try:
                logging.debug("Downloading group details for: %s" % group_id)
                html = None

                preview_html = urllib2.urlopen(get_group_url(group_id)).read()

                iframe_url = re.search(re.compile(r"<iframe.*?src=\"(.*?)\""), preview_html)

                if iframe_url:
                    html = urllib2.urlopen(iframe_url.group(1)).read()[:10]
                else:
                    html = str(BeautifulSoup(preview_html).find('div', {'id':'hit-wrapper'}))[:10]

                if html:
                    data[i]['HitGroupStatus']['hit_group_content'].html = html
            except:
                logging.error("Failed to process group details for %s" % (group_id))
                errors.append(grab_error(sys.exc_info()))

    return (data,errors)

def callback_add_crawlfk(data, **kwargs):

    if type(data) != type([]):
        raise Exception, '::callback_add_crawlfk() must be called with one list argument'

    if 'crawl' not in kwargs:
        raise Exception, '::callback_add_crawlfk() must be called with \'crawl_id\' kwarg being an id of Crawl'

    for i in range(0, len(data)):
        data[i]['HitGroupStatus']['crawl'] = kwargs['crawl']

    return (data,[])
