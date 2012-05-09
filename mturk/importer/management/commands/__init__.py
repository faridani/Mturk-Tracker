from django.conf import settings
import csv
import os


def write_counter(counter_name, value):
    f = open(os.path.join( settings.ROOT_PATH, '%s.counter' % counter_name ), 'w')
    f.write(str(value))
    f.close()


def get_counter(counter_name):
    f = open(os.path.join( settings.ROOT_PATH, '%s.counter' % counter_name ), 'r')
    counter = int(f.read())
    f.close()
    return counter


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')
