from xml.dom import minidom

from lxml import etree as ETree
from atlassian import Confluence
from netbox_wiki.updater.exceptioins import WikiUpdateException
from django.conf import settings


class ConfluenceAdapter(object):
    """
    Adapter for Atlassian Confluence class.
    Encapsulates content retrieve and update functionality.
    """
    PAGE_TITLE = "partial-devices"
    SPACE_KEY = "SNOW"

    def __init__(self):
        self.confluence = Confluence(url=settings.CONFLUENCE_CREDENTIALS['url'],
                                     username=settings.CONFLUENCE_CREDENTIALS['username'],
                                     password=settings.CONFLUENCE_CREDENTIALS['password'])
        self.page_id = None

    def get_page_content(self):
        """
        Get page content.

        :raises: WikiUpdateException

        :rtype: xml.dom.minidom.Document
        :returns: Page content data.
        """
        data = self.confluence.get_page_by_title(title=self.PAGE_TITLE, space=self.SPACE_KEY,
                                                 expand="body.storage,version")
        if not data:
            # No such page exist. Then create such page.
            data = self.create_page()

        # TODO: Change the way this works. May be get_page_content should be performed on init.
        self.page_id = data['id']

        try:
            raw_xml = data['body']['storage']['value']
        except KeyError:
            raise WikiUpdateException("Can't get partial-devices page content.")

        # return ETree.fromstring(body, ETree.XMLParser(recover=True))
        body = minidom.parseString('<?xml version="1.0"?><!DOCTYPE xml SYSTEM "xhtml.ent" []>'
                                   '<xml xmlns:atlassian-content="http://atlassian.com/content"'
                                   ' xmlns:ac="http://atlassian.com/content"'
                                   ' xmlns:ri="http://atlassian.com/resource/identifier"'
                                   ' xmlns:atlassian-template="http://atlassian.com/template"'
                                   ' xmlns:at="http://atlassian.com/template" xmlns="http://www.w3.org/1999/xhtml">'
                                   '<div>{}</div></xml>'.format(raw_xml))

        return body

    def create_page(self):
        """
        Create new page.+

        :raises: WikiUpdateException

        :rtype: dict
        :return: Data of newly created page.
        """
        data = self.confluence.create_page(self.SPACE_KEY, self.PAGE_TITLE, body="")
        if not data or 'id' not in data:
            raise WikiUpdateException("Page `{}` could not be created. Response data: {}".format(self.PAGE_TITLE, data))
        return data

    def update_page_content(self, body):
        """
        Update existing page with new body.

        :type body: xml.dom.minidom.Document
        :param body: Page content data.

        :rtype: dict
        :returns: Data of newly updated page.
        """
        # TODO: May be there is a better way to do this? May be use something else instead of `minidom`.
        raw_xml = body.toxml()[351:-12]
        data = self.confluence.update_existing_page(self.page_id, self.PAGE_TITLE, raw_xml)
        if not data or 'id' not in data:
            raise WikiUpdateException("Page `{}` could not be updated. Response data: {}".format(self.PAGE_TITLE, data))
        return data

    @staticmethod
    def update_content_for_field(page_content, field):
        """
        Update content for field.

        :type page_content: ElementTree
        :param page_content: Wiki page content.

        :type field: AbstractLinkedField
        :param field: Field for which the page_content should be updated.

        :rtype: xml.dom.minidom.Document
        :returns: Page content data.
        """
        for element in page_content.getElementsByTagName("ac:structured-macro"):
            if element.attributes['ac:name'].value == 'multiexcerpt':
                for node in element.getElementsByTagName("ac:parameter"):
                    if node.attributes['ac:name'].value == 'MultiExcerptName' and node.childNodes[0].wholeText == field.name:
                        element.getElementsByTagName("ac:rich-text-body")[0].getElementsByTagName("p")[0].childNodes[0].replaceWholeText(field.provide_value())
        return page_content
