#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # if it's crawl script - monkeypatch!
    if 'crawl' in sys.argv:
        from gevent import monkey
        monkey.patch_all()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
        "mtracker.settings.development")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
