"""
    Django model sphinx autodoc plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Using autodoc-process-docstring event to extend the model documentation.
    Additionally, django schema nodelist is build to display using
    djangomodelschema directive.

    TODO1: Create nodes and nodelists to displays as 'djangomodelschema'
    TODO2: Get sphinx-documented members to display along with field properties
"""
import re
import sys
import inspect
import docutils
#from sphinx.locale import _
from sphinx.util.compat import Directive
from django.utils.html import strip_tags
from django.utils.encoding import force_unicode
from django.db import models


class djangomodel(docutils.nodes.General, docutils.nodes.Element):
    pass


class djangomodellist(docutils.nodes.General, docutils.nodes.Element):
    pass


class DjangoModellistDirective(Directive):

    def run(self):
        return [djangomodellist('')]


def purge_nodes(app, env, docname):
    if not hasattr(env, 'djmex_all_djangomodels'):
        return
    env.djmex_all_djangomodels = [m for m in env.djmex_all_djangomodels
                                    if m['docname'] != docname]


def process_nodes(app, doctree, fromdocname):
    """Replaces all djangomodellist nodes with a list of the collected models.
    """

    # use to hide some directives - unused in this case ?
    # if not app.config.todo_include_todos:
    #     for node in doctree.traverse(todo):
    #         node.parent.remove(node)

    env = app.builder.env

    content = []
    if app.config.djmex_include_djangomodellists:

        for info in env.djmex_all_djangomodels:

            para = docutils.nodes.paragraph()

            para += docutils.nodes.Text('Table: {0} ({1})'.format(
                info['target']._meta.db_table, info['name']))

            content.append(para)

            fields = info['target']._meta._fields()
            for field in fields:
                db_column = field.db_column or field.name
                help_text = strip_tags(force_unicode(field.help_text))
                #verbose_name = force_unicode(field.verbose_name).capitalize()
                ftype = u':type {0}: {1}'.format(
                    type(field).__name__, field.attname)
                db_index = 'Is index' if field.db_index else ''

                para = docutils.nodes.paragraph()
                para += docutils.nodes.Text(db_column, db_column)
                para += docutils.nodes.Text(db_index, db_index)
                para += docutils.nodes.Text(help_text, help_text)
                para += docutils.nodes.Text(ftype, ftype)
                content.append(para)

    for node in doctree.traverse(djangomodellist):
        node.replace_self(content)


def add_djangomodel_node(app, what, name, obj, options, lines):
    """Stores target class for rendering in process nodes."""
    env = app.builder.env
    if not hasattr(env, 'djmex_all_djangomodels'):
        env.djmex_all_djangomodels = []

    env.djmex_all_djangomodels.append({
        'docname': env.docname,
        'target': obj,
        'name': name
    })


def enrich_docstring(obj, lines):
     # Grab the field list from the meta class
        fields = obj._meta._fields()

        for field in fields:
            # Decode and strip any html out of the field's help text
            help_text = strip_tags(force_unicode(field.help_text))

            # Decode and capitalize the verbose name, for use if there isn't
            # any help text
            verbose_name = force_unicode(field.verbose_name).capitalize()

            if help_text:
                # Add the model field to the end of the docstring as a param
                # using the help text as the description
                lines.append(u':param %s: %s' % (field.attname, help_text))
            else:
                # Add the model field to the end of the docstring as a param
                # using the verbose name as the description
                lines.append(u':param %s: %s' % (field.attname, verbose_name))

            # Add the field's type to the docstring
            lines.append(u':type %s: %s' % (field.attname, type(field).__name__))


def process_docstring(app, what, name, obj, options, lines):
    """Gathers djangomodellist entries and enchances model docs for all django
    models processed.

    """
    if inspect.isclass(obj) and issubclass(obj, models.Model):
        # Add djangomodellist entry
        add_djangomodel_node(app, what, name, obj, options, lines)
        # Make pretty model description using verbose_names and help_text
        if app.config.djmex_pretty_model:
            lines = enrich_docstring(obj, lines)
    return lines


def setup(app):
    app.connect('autodoc-process-docstring', process_docstring)
    #app.connect('autodoc-process-signature', process_signature)

    #TODO:
    # show model lists:
    app.add_config_value('djmex_include_djangomodellists', False, False)
    # settings to disable nice display of models fields
    app.add_config_value('djmex_pretty_model', False, False)
    # settings to disable all djangoschema directives
    # app.add_config_value('djmex_show_schema', False, False)
    # settings to exclude modules
    # app.add_config_value('djmex_excluded', [], False)

    app.add_node(djangomodellist)
    app.add_node(djangomodel)
    app.add_directive('djangomodellist', DjangoModellistDirective)
    app.connect('doctree-resolved', process_nodes)
    app.connect('env-purge-doc', purge_nodes)


# def process_autoclass_nodes(app, doctree, fromdocname):
#     for node in doctree.traverse(docutils.nodes.Text):
#         print node
#         #import ipdb; ipdb.set_trace()
#         # if node.tagname == '#autoclass' and  node.parent.tagname in TEXT_NODES:
#         #     import ipdb; ipdb.set_trace()
#     pass


# def doctree_read(app, doctree):
#     for node in doctree.traverse(docutils.nodes.Text):
#         continue
#         print node
#         #import ipdb; ipdb.set_trace()
#         # if node.tagname == '#autoclass' and  node.parent.tagname in TEXT_NODES:
#         #     import ipdb; ipdb.set_trace()
#     pass


# def process_signature(app, what, name, obj, options, signature, return_annotation):
#     """Empty for now, no use for it?"""
#     return (signature, return_annotation)
