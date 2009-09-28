import htmlentitydefs
import re
from datetime import datetime


def calculate_similarity(text1, text2):

    t1 = re.sub(r"[^a-z0-9 ]", '', text1.lower()).split()
    t2 = re.sub(r"[^a-z0-9 ]", '', text2.lower()).split()

    intersection = []

    for l in t1:
        if l in t2: intersection.append(l)

    sum = t1

    for l in t2:
        if l not in t1: sum.append(l)

    coefficient = float(len(intersection)) / float(len(sum))

    return coefficient

def fuse(array, separator):

    if type(array) != type([]) and type(array) != type(()):
        raise Exception, 'Fused object must be a list or a tuple.'

    if type(separator) != type(''):
        raise Exception, 'Separator must be a string.'

    array_length = len(array)
    if array_length > 1:

        result = ''
        for i in range(0, array_length):
            result += array[i]
            if i < array_length-1:
                result += separator
        return result

    elif array_length == 1:
        return array[0]


def remove_whitespaces(text):

    def remove_ascii(text):
        text = str(re.sub(r"\s{2,50}", ' ', text)).strip()
        text = str(re.sub(r"\n", ' ', text))
        return text

    def remove_unicode(text):
        text = unicode(re.sub(r"\s{2,50}", ' ', text)).strip()
        text = unicode(re.sub(r"\n", ' ', text))
        return text

    encoding = 'ascii'

    if type(text) != type(''):
        if type(text) == type(u''):
            encoding = 'unicode'
        else:
            raise Exception, 'Text must be a string.'

    while text.find('  ') > -1:
        if encoding == 'unicode':
            try:
                text = remove_ascii(text)
            except:
                text = remove_unicode(text)
        else:
            text = remove_unicode(text)

    return text


def strip_html(text, mode = 'strict'):

    if mode == 'strict':
        text = filter(lambda c: ord(c) < 128, text)

    def fixup(m):
        text = m.group(0)
        if text[:1] == "<":
            return "" # ignore tags
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        elif text[:1] == "&":
            import htmlentitydefs
            entity = htmlentitydefs.entitydefs.get(text[1:-1])
            if entity:
                if entity[:2] == "&#":
                    try:
                        return unichr(int(entity[2:-1]))
                    except ValueError:
                        pass
                else:
                    return unicode(entity, "iso-8859-1")
        return text # leave as is

    try:
        return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)
    except UnicodeDecodeError:
        return re.sub("(?s)<[^>]*>|&#?\w+;", ' ', text)


def ts():

    d = datetime.now()
    return str(d.year).zfill(4) + str(d.month).zfill(2) + str(d.day).zfill(2) + str(d.hour).zfill(2) + str(d.minute).zfill(2) + str(d.second).zfill(2)