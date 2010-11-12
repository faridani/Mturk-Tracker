# -*- coding: utf-8 -*-

import re


_RX_HITS_MAINPAGE = \
    re.compile(r'(\d+,?\d*)\s*?HITs</\w+?>\s*?available', re.M)

_RX_HITS_LIST = \
    re.compile(r'''
    (
        # get expiration date
        HIT Expiration Date:[^<]*
        (?:<[^>]+>)*?
        (?P<exp_date>[\d\w\ ]+?)
        (?:&nbsp;)?
        \(

        .*?

        # get number of available hits
        (?P<hits>[\d,]+)
        \s*?
        HITs
        </\w+?>
        \s*?
        available
    )*
    ''', re.M|re.X)



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
        res['hits'] = int(res['hits'].replace(',', ''))
        yield res
