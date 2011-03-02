Getting started
===============

Mturk-Tracker is a Django web application and is setup within python virtualenv and requires a working python envioroment and PostgreSQL database.

Required libraries 
------------------

Mturk-Tracker requires some basic packages::

	$ sudo apt-get install python-virtualenv
	$ sudo apt-get install git
	$ sudo apt-get install subversion
	$ sudo apt-get install mercurial
	$ sudo apt-get install postgresql-8.4
	$ sudo apt-get install postgresql-server-dev-8.4
	$ sudo apt-get install python2.6-dev
	$ sudo apt-get install libevent-dev
	
	
Project setup 
-------------

To initialize project, virtualenv_ python package is required (you may also
want to use virtualenvwrapper_ extension). First, create and activate new
virtual python environment::

    $ virtualenv mturk --no-site-packages
    $ cd  mturk
    $ . bin/activate

or::

    $ mkvirtualenv mturk --no-site-packages
    $ workon mturk
    $ cd $VIRTUAL_ENV

if using virtualenvwrapper_.

After that, clone mturk code from repository and install all
dependencies using pip_ (you have to install *mercurial* and *subversion*
first)::

	$ git clone git://github.com/mickek/Mturk-Tracker.git src
	$ cd src
	$ git fetch
	$ git checkout -b virtualenv --track origin/virtualenv
	$ echo "mturk.settings.base" > DJANGO_SETTINGS_MODULE
	$ pip install -r requirements.txt
	
Libraries update
~~~~~~~~~~~~~~~~

Because ``pip`` should take care of all libraries, use it to update already
existing configuration. Whenever new dependency appears, run ``pip -r
requirements.txt`` just to update.


Choosing custom settings module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default ``mturk.settings.defaults`` configuration module is being used. To add
custom variables you can add code to:

- ``mturk.settings.default`` - project default variables visible for all other
  configuration files

You can also setup any other configuration module by setting
``DJANGO_SETTINGS_MODULE`` shell variable or file as given in example above.


Setting up Database
~~~~~~~~~~~~~~~~~~~

Make sure that django app can connect to database, the best way to do that is to allow postgres to accept local connections by editing pg_hba.conf file.
Check if you can connect to database::

	$ psql -U postgres

In order to setup a clean db you have to create the database and populate it with tables::

	$ createdb -U postgres  mturk_tracker
	$ createlang plpgsql -U postgres -d mturk_tracker
	$ python manage.py syncdb
	$ python manage.py migrate

Running django appliaction
--------------------------

Nothing special, just type::

    $ sudo python manage.py runserver 80

in django project directory. And then point your browser to http://localhost/
 
Crawling mturk
--------------

You may launch initial crawl by::

	$ python manage.py crawl --workers=8 --logconf=logging.conf

Logs will be saved in /tmp/crawler.log

To generate data that will be displayed on graphs you need to launch scripts::

	$ python manage.py db_refresh_mviews
	$ python manage.py db_update_agregates
	$ python manage.py db_calculate_daily_stats
	
Solr
----

TODO