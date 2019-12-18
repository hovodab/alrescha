import uuid

from lxml import etree
from atlassian import Confluence

from django_netbox_confluence.updater.exceptioins import WikiUpdateException
from django.template.loader import render_to_string


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

    def __init__(self, url, username, password, space_key):
        self.confluence = Confluence(url=url, username=username, password=password)
        self.space_key = space_key
        self.get_space_or_create()

    def get_space_or_create(self):
        """
        Check whether space exists or not. If it doesn't, then create the space.

        :rtype: dict
        :return: Space data.
        """
        space = self.confluence.get_space(self.space_key)
        if type(space) is not dict:
            raise WikiUpdateException("Can't retrieve valid information about Confluence space."
                                      " Please check configurations. Data: {}".format(space))

        if space.get('statusCode', None) == 404:
            space = self.confluence.create_space(self.space_key, self.space_key)
        return space

    def get_page_or_create(self, page_title):
        """
        Get page content, if no such page then create it.

        :type page_title: str
        :param page_title: Title of the page which should be retrieved.

        :raises: WikiUpdateException

        :rtype: tuple(int, lxml.etree._Element)
        :returns: Tuple where first element is the id of the page. The second is the parsed content data.
        """
        data = self.confluence.get_page_by_title(title=page_title,
                                                 space=self.space_key,
                                                 expand="body.storage,version")
        if not data:
            # No such page exist. Then create such page.
            data = self.create_page(page_title)

        try:
            content_xml = data['body']['storage']['value']
        except KeyError:
            raise WikiUpdateException("Can't get partial-devices page content.")

        body_xml = render_to_string('wrapper.xml', {
            'content': content_xml
        })
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
        data = self.confluence.create_page(self.space_key, page_title, body="")
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

        :raises: WikiUpdateException

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
        return element.xpath('//ac:structured-macro/ac:parameter'
                             '[@ac:name="MultiExcerptName" and translate(normalize-space(text()), " ", "")="{}"]'
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
            # If element does not exist then create it.
            macro_id = uuid.uuid4()
            data = render_to_string('multiexcerpt.xml', {
                "macro_id": macro_id,
                "field_name": field.name,
                "field_value": field.provide_value()
            })
            element = etree.fromstring(data)
            page_content.insert(-1, element)
            # Can leave without this return, but `Explicit is better than implicit.` (C) Python Zen.
            return page_content

        for field_element in field_elements:
            field_element.text = field.provide_value()

        return page_content
