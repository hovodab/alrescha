from abc import ABCMeta, abstractmethod


class ABCLinkedFieldMeta(ABCMeta):
    linked_field_classes = dict()

    def __new__(mcs, name, parents, configs):
        new_class = super().__new__(mcs, name, parents, configs)
        # Ignore Abstract class, use only its derivatives.
        if object not in parents:
            assert name not in mcs.linked_field_classes
            mcs.linked_field_classes[name] = new_class
        return new_class


class AbstractLinkedField(object, metaclass=ABCLinkedFieldMeta):
    """
    Represents base field that should be linked with Confluence Wiki and should be updated when is changed on NetBox.
    """

    def __init__(self, name, value):
        """
        Init.

        :type name: str
        :param name: Name of the field.

        :type value: str|dict|int
        :param value: New value of the field.
        """
        self.name = name
        self.value = value

    @abstractmethod
    def provide_value(self):
        """
        Update page content.

        :raises: NotImplementedError
        """
        raise NotImplementedError()

    @property
    def verbose_name(self):
        return self.__class__.name


class TextLinkedField(AbstractLinkedField):
    """
    Represents text field which should be updated on Wiki.
    """

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
