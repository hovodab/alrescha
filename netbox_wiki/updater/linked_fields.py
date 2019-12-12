from abc import ABCMeta, abstractmethod


class AbstractLinkedField(object, metaclass=ABCMeta):
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


class TextLinkedField(AbstractLinkedField):
    """
    Represents text field which should be updated on Wiki.
    """

    def provide_value(self):
        """
        TODO
        """
        return self.value


class StatusLinkedField(AbstractLinkedField):
    """
    Represents text field which should be updated on Wiki.
    """

    def provide_value(self):
        """
        TODO
        """
        return self.value['label']
