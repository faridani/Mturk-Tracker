from BeautifulSoup import BeautifulSoup, ResultSet
from tenclouds.text import remove_whitespaces, strip_html

import datetime
import re
import urllib2

def callback_allhit(self, pages):

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

    results = []

    for page_number in pages:

        response = urllib2.urlopen(self.get_allhit_url(page_number))
        html = response.read()
        soup = BeautifulSoup(html)

        table = soup.find('table', cellpadding='0', cellspacing='5', border='0', width='100%')
        table.contents = remove_newline_fields(table.contents)

        print "Page number:",page_number
        hits_available = soup.find('b', style='display:block;color:#CC6600')
        if is_soup(hits_available):
            hits_available = hits_available.contents[0]
            hits_available = int(re.sub(',', '', hits_available[:hits_available.index(' ')]))

        result = {
        'page_number': page_number,
        'hits_available': hits_available,
        'groups': []
        }

        for i_group in range(0,len(table.contents)):

            group_html = table.contents[i_group]

            title = group_html.find('a', {'class':'capsulelink'})
            if is_soup(title):
                try:
                    title = str(title.contents[0])
                except:
                    title = unicode(title.contents[0])
                title = remove_whitespaces(title)

            group_id = group_html.find('span', {'class':'capsulelink'})
            if is_soup(group_id):
                group_id = remove_newline_fields(group_id.contents)[0]
                if 'href' in group_id._getAttrMap():
                    start = group_id['href'].index('groupId=')+8
                    stop = group_id['href'].index('&')
                    group_id = group_id['href'][start:stop]
                else:
                    group_id = 0

            fields = group_html.findAll('td', {'align':'left','valign':'top','class':'capsule_field_text'})

            if is_soup(fields):

                requester_html = remove_newline_fields(fields[0].contents)[0]
                requester_name = requester_html.contents[0]
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
                time_alloted = time_alloted[:time_alloted.index(' ')]

                reward = float(remove_newline_fields(fields[3].contents)[0][1:])

                description = remove_newline_fields(fields[5].contents)[0]

                keywords_raw = remove_newline_fields(fields[6].contents)
                keywords = []
                for i in range(0, len(keywords_raw)):
                    try:
                        keyword = keywords_raw[i].contents
                        keywords.append(keyword)
                    except:
                        continue

                result['groups'].append({
                'inpage_position': i_group+1,
                'group_id': group_id,
                'title': title,
                'requester_id': requester_id,
                'requester_name': requester_name,
                'hit_expiration_date': hit_expiration_date,
                'time_alloted': time_alloted,
                'reward': reward,
                'description': description
                })

        results.append(result)

    return results

def callback_group(self, id):

    if type(id) != type(1):
        raise Exception, '::callback_group() must be called with one integer argument'

    print 'group:',id