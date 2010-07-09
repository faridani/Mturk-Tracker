#/usr/bin/env python
# -*- coding: utf-8 -*-
"""
   Small library to check for pid
"""
import logging
from os import getpid
from os import kill
from os import remove
from os import makedirs
from os.path import isdir
from sys import exit

from django.conf import settings

logger = logging.getLogger('pid_files')


if hasattr(settings, 'RUN_DATA_PATH') and not isdir(settings.RUN_DATA_PATH):
   logger.info('creating %s directory' % (settings.RUN_DATA_PATH,))
   makedirs(settings.RUN_DATA_PATH)

if not hasattr(settings, 'RUN_DATA_PATH'):
   logger.error('No settings.RUN_DATA_PATH, you pidfiles have nowhere to go.')


class Pid(object):
   """
   Simple class for pidfile managment. In settings you specify RUN_DATA_PATH variable.
   When pid object is instantiated we check if pid file for a given name already was created
   in that directory and if so we either set 'exists' variable to True or perform exit(1).
   Pidfile is removed in case of process that do not responds(this is for countering so-called
   'stale pidfile' case ).


   """
   def __init__(self, name, auto_exit=True):
       """
       This is pid object initializator

       :param name: pidfile name, will be created in RUN_DATA_PATH folder and appended .pid extension on creation
       :type name: string
       :param auto_exit: if True, when pidfile exists and is not stale process will sys.exit(1), else exists attribute is set to True
       :type auto_exit: boolean
       :default auto_exit: True

       """
       self.exists = False
       PID_FILE = '%s/%s.pid' % (settings.RUN_DATA_PATH, name)
       self.PID_FILE = PID_FILE
       try:
           old_pid = int(open(PID_FILE).read())
           try:
               kill(old_pid, 0)
               logger.info('process %s (%s) still exists' % (old_pid, name))
               if auto_exit:
                   exit(1)
               else:
                   self.exists = True
           except OSError:
               logger.info('process %s (%s) looks like almost dead' % (old_pid, name))
               remove(PID_FILE)
       except IOError:
           logger.info('no such %s (%s) file' % (PID_FILE, name))
       except ValueError:
           logger.info('value')

       self.actual_pid_file = open(PID_FILE, 'w')
       self.actual_pid = str(getpid())
       self.actual_pid_file.write(self.actual_pid)
       self.actual_pid_file.close()
       self.actual_pid
       logger.info('new pid %s => %s (%s) has been created' % (self.actual_pid, PID_FILE, name))
       self.name = name

   def remove_pid(self):
       """
       This method removes pidfile.
       """
       try:
           remove(self.PID_FILE)
       except OSError, e:
           if not self.exists:
               logger.info('error deleting pid file %s (%s), error: %s' % (self.PID_FILE, self.name, e))
       logger.info('pid file %s (%s) has been deleted' % (self.PID_FILE, self.name))

