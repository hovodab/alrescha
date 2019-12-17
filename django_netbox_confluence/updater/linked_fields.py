from abc import ABCMeta, abstractmethod

from django_netbox_confluence.updater.exceptioins import WikiUpdateException


class ABCLinkedFieldMeta(ABCMeta):
    """
    Add ability of registration of classes which are derived from AbstractLinkedField.
    """
    linked_field_classes = dict()

    def __new__(mcs, name, parents, configs):
        new_class = super().__new__(mcs, name, parents, configs)
        # Check if verbose_name is defined in class definition. If yes then set special variable so it will be used
        # instead of the class name when accessing `verbose_name`.
        if 'verbose_name' in configs:
            new_class._verbose_name = configs['verbose_name']

        # If class is defined with the same name.
        if name in mcs.linked_field_classes:
            raise WikiUpdateException("Seems the class {new_class} with name `{name}` was already defined as "
                                      "{existing}.".format(new_class=new_class,
                                                           name=name,
                                                           existing=mcs.linked_field_classes[name]))

        # Ignore Abstract class, use only its derivatives.
        if object not in parents:
            mcs.linked_field_classes[name] = new_class
        return new_class

    @property
    def verbose_name(self):
        """
        Verbose name of the class/type. This text should appear in the dropdown when user creates new field which is
        meant to be synchronized between NetBox and Confluence Wiki.
        If not defined on derivatives then the class name will be used.
        """
        if hasattr(self, '_verbose_name'):
            return self._verbose_name
        return self.__name__


class AbstractLinkedField(object, metaclass=ABCLinkedFieldMeta):
    """
    Represents base field that should be linked with Confluence Wiki and should be updated when is changed on NetBox.
    """

    def __init__(self, name, value, is_custom=False):
        """
        Init.

        :type name: str
        :param name: Name of the field.

        :type value: str|dict|int
        :param value: New value of the field.

        :type is_custom: bool
        :param is_custom: Is field custom field or not.
        """
        self.is_custom = is_custom
        self.value = value
        self.name = "custom_{}".format(name) if self.is_custom else name

    @abstractmethod
    def provide_value(self):
        """
        Update page content.

        :raises: NotImplementedError
        """
        raise NotImplementedError()


class TextLinkedField(AbstractLinkedField):
    """
    Represents text field which should be updated on Wiki.
    """
    verbose_name = "Text Linked Field"

    def provide_value(self):
        """
        Provide value for the field.

        :rtype: str
        :returns: Value of the field.
        """
        return self.value


class StatusLinkedField(AbstractLinkedField):
    """
    Represents text field which should be updated on Wiki.
    """
    verbose_name = "Drop down field."

    def provide_value(self):
        """
        Provide value for the field

        :rtype: str
        :returns: Status of the site.
        """
        return self.value['label']
