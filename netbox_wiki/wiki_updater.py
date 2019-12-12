from abc import ABCMeta, abstractmethod

from lxml import etree as ETree
from xml.dom import minidom
from atlassian import Confluence


class AbstractLinkedField(object, metaclass=ABCMeta):
    """
    Represents base field that should be linked with Confluence Wiki and should be updated when is changed on NetBox.
    """

    def __init__(self, value):
        """
        Init.

        :type value: str
        :param value: New value of the field.
        """
        self.value = value

    @abstractmethod
    def update(self, page_content):
        """
        Update page content.

        :type page_content: ElementTree
        :param page_content: Wiki page content.

        :raises: NotImplementedError
        """
        raise NotImplementedError()


class TextLinkedField(AbstractLinkedField):
    """
    Represents text field which should be updated on Wiki.
    """

    def update(self, page_content):
        """
        TODO
        """
        print(page_content, ":::::::::::::::::::::::")
        return page_content


class WikiUpdateException(Exception):
    """
    Exception class for WikiPageUpdater exceptions.
    """


class ConfluenceAdapter(object):
    PAGE_TITLE = "partial-devices"
    SPACE_KEY = "SNOW"

    def __init__(self):
        self.confluence = Confluence(url='http://localhost:8090',
                                     username='admin',
                                     password='admin')
        self.page_id = None
        self.page_title = None

    def get_page_content(self):
        # TODO: Handle case when page doesn't exist.
        data = self.confluence.get_page_by_title(title=self.PAGE_TITLE, space=self.SPACE_KEY, expand="body.storage,version")
        if not data:
            # No such page exist. Then create such page.
            data = self.create_page()

        self.page_id = data['id']
        self.page_title = data['title']

        try:
            body = data['body']['storage']['value']
        except ValueError:
            raise WikiUpdateException("Can't get partial-devices page content.")

        # return ETree.fromstring(body, ETree.XMLParser(recover=True))
        body = minidom.parseString("""<?xml version='1.0'?><!DOCTYPE xml SYSTEM "xhtml.ent" []><xml xmlns:atlassian-content="http://atlassian.com/content" xmlns:ac="http://atlassian.com/content" xmlns:ri="http://atlassian.com/resource/identifier" xmlns:atlassian-template="http://atlassian.com/template" xmlns:at="http://atlassian.com/template" xmlns="http://www.w3.org/1999/xhtml"><div>{}</div></xml>""".format(body))
        print(body, type(body))
        for element in body.getElementsByTagName("ac:structured-macro"):
            if element.attributes['ac:name'].value == 'multiexcerpt':
                element.getElementsByTagName("ac:rich-text-body")[0].getElementsByTagName("p")[0].childNodes[0].replaceWholeText("Andromeda")
        return body

    def create_page(self):
        data = self.confluence.create_page(self.SPACE_KEY, self.PAGE_TITLE, body="")
        return data

    def update_page_content(self, body):
        # TODO: May be there is a better way to do this? May be use something else instead of `minidom`.
        body = body.toxml()[351:-12]
        data = self.confluence.update_existing_page(self.page_id, self.page_title, body)


class WikiPageUpdater(object):
    FIELD_MAP = {
        "status": TextLinkedField,
        "description": TextLinkedField,
    }
    CUSTOM_FIELD_MAP = {
        "purpose": TextLinkedField,
    }

    def __init__(self, data):
        self.data = data
        self.confluence = ConfluenceAdapter()

    @staticmethod
    def create_field_chain(field_map, data):
        """
        Create fields chain.

        :type field_map: dict
        :param field_map: Map between field name and its corresponding LinkedField.

        :type data: dict
        :param data: Data that needs to be updated on the Wiki page.

        :rtype: list
        :returns: List of LinkedFields.
        """
        field_chain = list()

        for field, field_class in field_map.items():
            try:
                field_object = field_class(data[field])
            except ValueError:
                raise WikiUpdateException("Field {} is configured in updater but does"
                                          " not present in webhook payload.".format(field))
            field_chain.append(field_object)

        return field_chain

    def update(self):
        # Implemented as chain of responsibilities.
        # Each field will change its own field for which it is responsible and pass data to another one.
        # [LinkedField1, LinkedField2, ...]
        # (Wikis old content) -> LinkedField1 -> LinkedField2 -> ... -> (Wikis new content).
        field_chain = self.get_field_chain()

        # TODO: Get page content.
        page_content = self.confluence.get_page_content()

        # Provide page content to each field so each will update the content with it specific way.
        for field in field_chain:
            page_content = field.update(page_content)
        # After all fields are done with the changes update page content.
        self.confluence.update_page_content(page_content)

    def get_field_chain(self):
        """
        Get field chain for fields that should be updated on the Wiki.
        :rtype
        """
        # TODO: Is there a better way to check ValueError more dynamic, for example if it is possible to get key name?
        try:
            field_chain = self.create_field_chain(self.FIELD_MAP, self.data['data'])
        except ValueError:
            raise WikiUpdateException("Wrong formatted request body:"
                                      " `data` is not present in webhook payload.")

        try:
            custom_field_chain = self.create_field_chain(self.CUSTOM_FIELD_MAP, self.data['data']['custom_fields'])
        except ValueError:
            raise WikiUpdateException("Wrong formatted request body:"
                                      " `custom_fields` is not present in webhook payload.")

        return field_chain + custom_field_chain


