#
# This file is imported by conf.py and contains all setings thar require
# formattin during deployment.
#
# Define path to documented modules and any setting you would like to
# see formatted when deploying.
#
import sys
import os

DOC_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# If this file is uploaded while deploying,
# project_dir will be na absolute path
if "%(project_dir)s".find('/') != -1:
    ROOT_PATH = os.path.join("%(project_dir)s", 'code')
else:
    ROOT_PATH = os.path.abspath(os.path.dirname(DOC_PATH))

sys.path.insert(0, os.path.join(ROOT_PATH, 'deployment'))
sys.path.insert(0, os.path.join(ROOT_PATH, 'app'))
sys.path.insert(0, os.path.join(ROOT_PATH))

settings_name = "%(settings_name)s"
if settings_name.find('(settings_name)s') != -1:
    settings_name = 'development'

settings_full_name = "mtracker.settings.{0}".format(settings_name)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_full_name)
