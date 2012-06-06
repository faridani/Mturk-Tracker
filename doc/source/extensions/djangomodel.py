"""
    Plugin for auto-docummenting django model classes
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Inhereting from a django model changes type's metaclass confusing sphinx.
    Thus, django Models will not appear in documentation created using:

    ..automodule:: path.to.some.module

    This plugin searches files for automodule invocations in  the form of

    ..automodule:: path.to.some.app.models

    imports such modules and searches them for classes inheriting
    django.db.models.Model, adding ``autoclass`` directive for matching models:

    ..autoclass:: path.to.module.ClassName

    after the ``automodule`` statement in question.

"""
import re
import sys
import inspect
from django.db import models


RE_STR = r"^.. automodule:: [\w.]*models\s*$"
MODELS_MODULE_RE = re.compile(RE_STR, re.MULTILINE)
""" A re used for finding modules containing django models.
    .. automodule:: [some.app.path.]models[any spaces]

"""


def source_read(app, docname, source):
    """ Fixing autodoc unability to document django model classes.

    Subscribing to 'doctree-read' event done just afer reading a number of
    input lines and before unfolding of any directives.

    Source is searched for '.. automodule::' directives targeted at modules
    containing django models. Next, modules are imported and .. autoclass
    directive is added for each of the contained classes.

    Sphinx note: source is a one-element list.

    """
    def __get_models(mod_path):
        """Returns a list of django classes in a module."""
        modnames = []
        if mod_path not in sys.modules:
            __import__(mod_path)
        # get classes
        clsmembers = inspect.getmembers(sys.modules[mod_path], inspect.isclass)
        for c in clsmembers:
            # only model.Models classes
            if issubclass(c[1], models.Model):
                # get full model paths
                modnames.append(c[1].__module__ + '.' + c[1].__name__)
        return modnames

    def __get_directives(class_names):
        """Returns a list of directives for each of the specified class_names.
        """
        return [".. autoclass:: {0}".format(c) for c in class_names]

    instring = source[0]
    changes = []
    for match in MODELS_MODULE_RE.finditer(instring):
        if match:
            # cut the '.. automodule:: ' part
            modname = match.group().strip()[16:]
            to = instring.find('\n\n', match.end())
            to = to if to != -1 else len(instring)
            # import model and generate list of directives
            inserts = __get_directives(__get_models(modname))
            # append only if there is somethind to add
            if len(inserts) > 0:
                changes.append((to, '\n\n' + '\n\n'.join(inserts)))

        result = []
        last_index = 0
        # split and then join the string with new directives
        for index, c in enumerate(changes):
            result.append(instring[last_index:c[0]])
            result.append(c[1])
            last_index = c[0]
        result.append(instring[last_index:])
        source[0] = ''.join(result)


def setup(app):
    app.connect('source-read', source_read)
