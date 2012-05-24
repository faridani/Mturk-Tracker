Html documentation
==================

Options
-------

There are two methods of generating the documentation:
* using make to generate the html's directly,
* using django-sphinxdoc management command.

Both approaches use sphinx-build command to generate the output files.

From now on, all paths will be given relative from `/path/to/Mturk-Tracker`, while your domain will be referred to as `yourdomain.com`.

Makefile, pure Sphinx
---------------------

The pure approach is to create the output html documentation files and host them as static files.

To do so:

    $ cd doc
    $ make html

The output will be available in `doc/build`, the documentation
index at: `doc/build/html/index.html`.

The documentation can be themed using custom themes, such as [10Clouds theme](doc/themes/10Clouds).

Default: django-sphinxdoc
-------------------------

A more integrated approach provided by: [django-sphinxdoc](https://bitbucket.org/ssc/django-sphinxdoc).

Short [docs](http://stefan.sofa-rockers.org/docs/django-sphinxdoc/quickstart/#setup):
1. Make sure that Mturk-Tracker appears in: `yourdomain.com/admin/sphinxdoc/project/` and path points to `doc/source/` - root directory of the documentation where the conf.py is.
2. Build the json documentation:

    $ python  manage.py updatedoc -b mturk-tracker
3. You should be able to see the documentation at: `yourdomain.com/docs/`, while the output files should be available in `source/_build/json/` and relates entries at `yourdomain.com/admin/sphinxdoc/document/`.

To add extra styles for the documentation, [override the default templates and/or change css](http://stefan.sofa-rockers.org/docs/django-sphinxdoc/change_appearance/).

Generating apidoc
-----------------

To create an automated api documentation, use sphinx-apidoc:

    sphinx-apidoc -o doc/source/api_doc/ . -H Mturk-Tracker wapi migrations
