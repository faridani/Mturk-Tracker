# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    """HTML tags stripper

    http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
    """

    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    stripper = MLStripper()
    stripper.feed(html)
    return stripper.get_data()
