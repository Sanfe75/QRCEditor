# Copyright 2020 Simone <sanfe75@gmail.com>
#
# Licensed under the Apache License, Version 2.0(the "License"); you may not use this file except
# in compliance with the License.You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License
# for the specific language governing permissions and limitations under the License.
#

import os

from xml.etree import ElementTree


class Resource(object):
    """ Create a Resource object.
    """

    def __init__(self, file, alias=''):
        """Constructor for the Resource class.

        Parameters:
        file (str): the full file name of the resource
        alias (str): alias for the resource
        """

        self.__file = file
        self.__alias = alias

    def __lt__(self, other):
        """Rich comparison for lower than.
        """

        return self.key() < other.key()

    def __le__(self, other):
        """Rich comparison for lower equal.
        """

        return self.key() <= other.key()

    def __eq__(self, other):
        """Rich comparison for equal.
        """

        return self.key() == other.key()

    def __ne__(self, other):
        """Rich comparison for not equal.
        """

        return self.key() != other.key()

    def __gt__(self, other):
        """Rich comparison for greater than.
        """

        return self.key() > other.key()

    def __ge__(self, other):
        """Rich comparison for greater equal.
        """

        return self.key() >= other.key()

    def alias(self):
        """Getter for self.__alias.
        """

        return self.__alias

    def file(self):
        """Getter for self.__file.
        """

        return self.__file

    def key(self):
        """Return the standard sorting key.
        """

        return [self.__alias, self.__file]

    def set_alias(self, alias):
        """Setter for self.__alias.
        """

        self.__alias = alias

    def set_file(self, file):
        """Setter for self.__file.
        """

        self.__file = file


class Resources(list):
    """ Create a list of Resource.
    """

    def __init__(self, language=None, prefix=None):
        """Constructor for the Resources class.
        """

        super(Resources, self).__init__()
        self.__language = language
        self.__prefix = prefix

    def language(self):
        """Getter for self.__language.
        """

        return self.__language

    def prefix(self):
        """Getter for self.__prefix.
        """

        return self.__prefix

    def is_duplicate(self, alias):
        """Check if the resource alias is a duplicate.

        Return:
        bool: True if it is a duplicate, False otherwise
        """

        aliases = [resource.alias() for resource in self if resource.alias() is not None]
        return aliases.count(alias) > 1

    def set_language(self, language):
        """Setter for self.__language.
        """

        self.__language = language

    def set_prefix(self, prefix):
        """Setter for self.__prefix.
        """

        self.__prefix = prefix


class ResourceCollection(list):
    """ Create a Resource object.
    """

    def __init__(self):
        """Constructor for the ResourceCollection class.
        """

        super(ResourceCollection, self).__init__()
        self.__file_name = None
        self.__dirty = False

    def __contains__(self, item):
        """Redefine in checking only ___language and __prefix.
        """

        for resources in self:
            if resources.language() == item.language() and resources.prefix() == item.prefix():
                return True
        return False

    def clear(self, clear_file_name=True):
        """Clear the collection.

        Parameters:
        clear_file_name (bool): if True also the file name will be cleared
        """

        del self[:]
        if clear_file_name:
            self.__file_name = None
            self.__dirty = False
        else:
            self.__dirty = True

    def index(self, item, start=0, end=None):
        """Redefine index checking only ___language and __prefix.
        """

        for index, resources in enumerate(self[start:end]):
            if resources.language() == item.language() and resources.prefix() == item.prefix():
                return index + start
        raise ValueError("{0} doesn't exists in the Collection".format(item))

    def load(self, file_name=""):
        """Load a file.

        Parameters:
        file_name (str): the full name of the file

        Return:
        bool: a boolean to represent if the load was successful
        str: a message
        """

        if file_name:
            self.__file_name = file_name
        self.clear(False)
        try:
            tree = ElementTree.parse(self.__file_name)
        except (IOError, OSError) as err:
            error = "Failed to load {0}".format(err)
            return False, error
        root = tree.getroot()
        count = 0
        for child in root:
            if "lang" in child.attrib.keys():
                language = child.attrib["lang"]
            else:
                language = None
            if "prefix" in child.attrib.keys():
                prefix = child.attrib["prefix"]
            else:
                prefix = None
            resources = Resources(language, prefix)
            self.append(resources)
            for resource in child:
                if "alias" in resource.attrib.keys():
                    alias = resource.attrib["alias"]
                else:
                    alias = None
                resources.append(Resource(resource.text, alias))
                count += 1

        self.__dirty = False
        return True, "Loaded {0} resources from {1}".format(count, os.path.basename(self.__file_name))

    def dirty(self):
        """Return the dirty status.

        Return:
        bool: the dirty flag
        """

        return self.__dirty

    def file_name(self):
        """Return the file name.

        Return:
        str: the file name
        """

        return self.__file_name

    def remove(self, resources):
        """Remove the resource from the collection.

        Return:
        bool: False if collection doesn't exit, True otherwise
        """

        if resources not in self:
            return False

        self.__dirty = True
        return True

    def save(self, file_name=""):
        """Save the data to self.__file_name.

        Parameters:
        file_name (str): the file to save

        Return:
        bool: a boolean to represent if the save was successful
        str: a message
        """

        if file_name:
            self.__file_name = file_name
        with open(self.__file_name, "wt") as file_handle:
            file_handle.write("""<!DOCTYPE RCC><RCC version="1.0">\n""")
            count = 0
            for resources in self:
                line = "    <qresource"
                if (language := resources.language()) is not None:
                    line += ' lang="{0}"'.format(language)
                if (prefix := resources.prefix()) is not None:
                    line += '  prefix="{0}"'.format(prefix)
                line += ">\n"
                file_handle.write(line)
                for resource in resources:
                    if resource.alias():
                        line = '        <file alias="{0}">{1}</file>\n'.format(resource.alias(), resource.file())
                    else:
                        line = '        <file>{0}</file>\n'.format(resource.file())
                    file_handle.write(line)
                    count += 1
                file_handle.write("    </qresource>\n")
            file_handle.write("</RCC>")
        self.__dirty = False
        return True, "Saved {0} resources to {1}".format(count, os.path.basename(self.__file_name))

    def set_dirty(self, dirty):
        """Setter for self.__dirty.
        """

        self.__dirty = dirty

    def set_file_name(self, file_name):
        """Setter for self.__file_name.
        """

        self.__file_name = file_name
        self.__dirty = True
