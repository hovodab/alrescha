import uuid

from lxml import etree
from atlassian import Confluence
from netbox_wiki.updater.exceptioins import WikiUpdateException
from django.conf import settings


class ConfluenceAdapter(object):
    """
    Adapter for Atlassian Confluence class.
    Encapsulates content retrieve and update functionality.
    """
    NAMESPACES = {
        "atlassian-content": "http://atlassian.com/content",
        "ac": "http://atlassian.com/content",
        "ri": "http://atlassian.com/content",
        "atlassian-template": "http://atlassian.com/template",
        "at": "http://atlassian.com/template",
    }

    def __init__(self):
        self.confluence = Confluence(url=settings.CONFLUENCE_CREDENTIALS['url'],
                                     username=settings.CONFLUENCE_CREDENTIALS['username'],
                                     password=settings.CONFLUENCE_CREDENTIALS['password'])

    def get_page_content(self, page_title):
        """
        Get page content.

        :type page_title: str
        :param page_title: Title of the page which should be retrieved.

        :raises: WikiUpdateException

        :rtype: tuple(int, lxml.etree._Element)
        :returns: Tuple where first element is the id of the page. The second is the parsed content data.
        """
        data = self.confluence.get_page_by_title(title=page_title,
                                                 space=settings.SPACE_KEY,
                                                 expand="body.storage,version")
        if not data:
            # No such page exist. Then create such page.
            data = self.create_page(page_title)

        try:
            content_xml = data['body']['storage']['value']
        except KeyError:
            raise WikiUpdateException("Can't get partial-devices page content.")

        # TODO: Move XML to template xml files.
        body_xml = ('<?xml version="1.0"?><!DOCTYPE xml SYSTEM "xhtml.ent" []>'
                       '<xml xmlns:atlassian-content="http://atlassian.com/content"'
                       ' xmlns:ac="http://atlassian.com/content"'
                       ' xmlns:ri="http://atlassian.com/resource/identifier"'
                       ' xmlns:atlassian-template="http://atlassian.com/template"'
                       ' xmlns:at="http://atlassian.com/template" xmlns="http://www.w3.org/1999/xhtml">'
                       '{}</xml>'.format(content_xml))
        return data['id'], etree.fromstring(body_xml)

    def create_page(self, page_title):
        """
        Create new page.+

        :type page_title: str
        :param page_title: Title of the page which should be created.

        :raises: WikiUpdateException

        :rtype: dict
        :return: Data of newly created page.
        """
        data = self.confluence.create_page(settings.SPACE_KEY, page_title, body="")
        if not data or 'id' not in data:
            raise WikiUpdateException("Page `{}` could not be created. Response data: {}".format(page_title, data))
        return data

    def update_page_content(self, page_id, page_title, body):
        """
        Update existing page with new body.

        :type page_id: int
        :param page_id: Page id which should be modified.

        :type page_title: str
        :param page_title: Title of the page which should be modified.

        :type body: lxml.etree._Element
        :param body: Page content data.

        :rtype: dict
        :returns: Data of newly updated page.
        """
        # Get raw xml.
        body_xml = etree.tostring(body).decode('utf-8')

        # <xml xmlns:******> <p></p>***<ac:structured-macro>***</ac:structured-macro> </xml>
        #                  ^                                                        ^
        # Take the content starting right after `>` of the opening xml tag and till `<` of xml closing tag.
        content_xml = body_xml[body_xml.find('>') + 1:body_xml.rfind('<')]

        data = self.confluence.update_existing_page(page_id, page_title, content_xml)
        if not data or 'id' not in data:
            raise WikiUpdateException("Page `{}` could not be updated. Response data: {}".format(page_title, data))
        return data

    @classmethod
    def get_field_element(cls, element, field):
        """
        Get element from tree by field name.

        :rtype: lxml.etree._Element
        :returns: Element data.
        """
        return element.xpath('//ac:structured-macro/ac:parameter[@ac:name="MultiExcerptName" and text()="{}"]'
                                '/following-sibling::ac:rich-text-body/*[local-name()="p"]'.format(field.name),
                             namespaces=cls.NAMESPACES)

    @classmethod
    def update_content_for_field(cls, page_content, field):
        """
        Update content for field.

        :type page_content: lxml.etree._Element
        :param page_content: Wiki page content.

        :type field: AbstractLinkedField
        :param field: Field for which the page_content should be updated.

        :rtype: lxml.etree._Element
        :returns: Page content data.
        """
        field_elements = cls.get_field_element(page_content, field)
        if not field_elements:
            macro_id = uuid.uuid4()
            # TODO: Move XML to template xml files.
            element = etree.fromstring('<ac:structured-macro xmlns:ac="http://atlassian.com/content" '
                                           'ac:name="multiexcerpt" ac:schema-version="1" ac:macro-id="{macro_id}">'
                                           '<ac:parameter ac:name="MultiExcerptName">{field_name}</ac:parameter>'
                                           '<ac:parameter ac:name="atlassian-macro-output-type">INLINE</ac:parameter>'
                                           '<ac:rich-text-body><p>{field_value}</p></ac:rich-text-body>'
                                           '</ac:structured-macro>'.format(macro_id=macro_id,
                                                                           field_name=field.name,
                                                                           field_value=field.provide_value()))
            page_content.insert(-1, element)

        for field_element in field_elements:
            field_element.text = field.provide_value()

        return page_content
