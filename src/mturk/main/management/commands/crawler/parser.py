# -*- coding: utf-8 -*-

import re
import datetime


_RX_WHITECHARS_DUPLICATE = re.compile(r'\s{2,}')

_RX_HITS_MAINPAGE = \
    re.compile(r'''
        (\d+,?\d*)
        \s*?
        HITs
        </\w+?>
        \s*?
        available
    ''', re.M|re.X)

_RX_HITS_LIST = \
    re.compile(r'''
        <a\s+class="capsulelink"[^>]*>\s*(?P<title>.*?)\s*</a>
        .*?

        # this one is otional, because it's now always available
        (:?
            groupId=(?P<group_id>.*?)(&|")
            .*?
        )?

        Requester
        .*?
        <td[^>]*>
            \s*?
                <a[^>]*requesterId=(?P<requester_id>.*?)(&|")[^>]*>
                    (?P<requester>.*?)
                </a>
            \s*?
        </td>

        .*?
        HIT\s+Expiration\s+Date
        .*?
        <td[^>]*>
            (?P<expiration_date>[^&]*)
        &

        .*?
        Time\s+Allotted
        .*?
        <td[^>]*>
            (?P<time_alloted>.*?)
        </td>

        .*?
        Reward
        .{,150}?
        <td[^>]*>
            \$
            (?P<reward>[\.\d]*)
        </td>

        .*?
        HITs\s+Available
        .*?
        <td[^>]*>
            (?P<hits_available>\d+)
        </td>

        .*?
        Description:
        .*?
        <td[^>]*>
            (?P<description>.*?)
        </td>

        .*?
        Keywords
        .*?
        <td[^>]*>
            \s*
            (?P<keywords>.*?)
            \s*
        </td>

        .*?
        Qualifications\s+Required
        .*?
        <tr[^>]*>
            (?P<qualifications>.*?)
        </table>
    ''', re.M|re.X|re.S)

_RX_HITS_LIST_KEYWORDS = \
    re.compile(r'''
        \s*
        <a[^>]*>
            (.+?)
        </a>
        \s*
    ''', re.M|re.X|re.S)

_RX_HITS_LIST_QUALIFICATIONS = \
    re.compile(r'''
        <td[^>]*>
            \s*
                (.+?)
            \s*
        </td>
    ''', re.M|re.X|re.S)

def human_timedelta_seconds(hd):
    """Convert any human timedelta value to seconds. Human time delta values
    are for example:
        * 1 hour
        * 30 minutes
        * 2 hours 1 minute 18 seconds
    """
    def _to_seconds(value, time_type):
        value = int(value)
        if time_type.startswith('day'):
            return value * 24 * 60 * 60
        if time_type.startswith('hour'):
            return value * 60 * 60
        if time_type.startswith('minute'):
            return value * 60
        if time_type.startswith('second'):
            return value
        raise TypeError('Unknown time type: %s' % time_type)

    total = 0
    for delta in re.findall(r'(\d+)\s+(\S+)', hd):
        total += _to_seconds(*delta)
    return total

def rm_dup_whitechas(s, replacer=' '):
    """Replace every two or more whitechars with single space"""
    return _RX_WHITECHARS_DUPLICATE.sub(replacer, s)

def available_hits_mainpage(html):
    """Return number of available hits fetched from given html (should be
    fetched from https://www.mturk.com/mturk/welcome)

    Returns None if hits number was not found.
    """
    rx = _RX_HITS_MAINPAGE.search(html, 1)
    if rx is None:
        return None
    matched = rx.groups()[0]
    return int(matched.replace(',', ''))

def available_hits_list(html):
    """Yield info about every hits group found in given html string

    Page should be fetched from
    https://www.mturk.com/mturk/findhits?match=false
    """
    rx_i = _RX_HITS_LIST.finditer(html)
    for rx in rx_i:
        res = rx.groupdict()

        # make parse result more polite and convert to python objects
        res['reward'] = float(res['reward'])
        res['expiration_date'] = datetime.datetime.strptime(
                res['expiration_date'], '%b %d, %Y')
        res['hits_available'] = int(res['hits_available'])
        res['keywords'] = _RX_HITS_LIST_KEYWORDS.findall(res['keywords'])
        qualifications = _RX_HITS_LIST_QUALIFICATIONS.findall( res['qualifications'])
        res['qualifications'] = [rm_dup_whitechas(q) for q in qualifications]
        # group id is not always available
        res['group_id'] = res.get('group_id', None)
        # convert time allotated to seconds
        res['time_alloted'] = human_timedelta_seconds(res['time_alloted'])

        yield res
