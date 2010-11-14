# -*- coding: utf-8 -*-

import re
import datetime


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
        Requester
        .*?
        <td[^>]*>
            \s*?
                <a[^>]*>
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
            (?P<hits>\d+)
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
    ''', re.M|re.X|re.S)

_RX_HITS_LIST_KEYWORDS = \
    re.compile(r'''
        \s*
        <a[^>]*>
            (.+?)
        </a>
        \s*
    ''', re.M|re.X|re.S)


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
    """
    Should be fetched from https://www.mturk.com/mturk/findhits?match=false
    """
    rx_i = _RX_HITS_LIST.finditer(html)
    for rx in rx_i:
        res = rx.groupdict()

        # convert to python objects
        res['reward'] = float(res['reward'])
        res['expiration_date'] = datetime.datetime.strptime(
                res['expiration_date'], '%b %d, %Y')
        res['hits'] = int(res['hits'])
        res['keywords'] = _RX_HITS_LIST_KEYWORDS.findall(res['keywords'])

        yield res
