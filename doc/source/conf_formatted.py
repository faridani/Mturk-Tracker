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
if "%(project_dir)s".find('/') > 0:
    ROOT_PATH = os.path.join("%(project_dir)s", 'code')
else:
    ROOT_PATH = os.path.abspath(os.path.dirname(DOC_PATH))

sys.path.insert(0, os.path.join(ROOT_PATH, 'deployment'))
sys.path.insert(0, os.path.join(ROOT_PATH, 'app'))
sys.path.insert(0, os.path.join(ROOT_PATH))

from mtracker.settings import development as settings
from django.core.management import setup_environ
setup_environ(settings)
