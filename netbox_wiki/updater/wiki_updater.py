from netbox_wiki.updater import linked_fields
from netbox_wiki.updater.confluence_adapter import ConfluenceAdapter
from netbox_wiki.updater.exceptioins import WikiUpdateException


class WikiPageUpdater(object):
    """
    Updates Wiki page when NetBox site page is updated.
    """
    FIELD_MAP = {
        "status": linked_fields.StatusLinkedField,
        "description": linked_fields.TextLinkedField,
    }
    CUSTOM_FIELD_MAP = {
        "purpose": linked_fields.TextLinkedField,
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

        :raises: WikiUpdateException

        :rtype: list
        :returns: List of LinkedFields.
        """
        field_chain = list()

        for field, field_class in field_map.items():
            try:
                field_object = field_class(field, data[field])
            except KeyError:
                raise WikiUpdateException("Field {} is configured in updater but does"
                                          " not present in webhook payload.".format(field))
            field_chain.append(field_object)

        return field_chain

    def update(self):
        """
        Update the data on the Wiki page.

        :rtype: void
        :returns: void
        """
        # Implemented as chain of responsibilities.
        # Each field will change its own field for which it is responsible and pass data to another one.
        # [LinkedField1, LinkedField2, ...]
        # (Wikis old content) -> LinkedField1 -> LinkedField2 -> ... -> (Wikis new content).
        field_chain = self.get_field_chain()

        page_content = self.confluence.get_page_content()

        # Provide page content to each field so each will update the content with it specific way.
        for field in field_chain:
            page_content = self.confluence.update_content_for_field(page_content, field)

        # After all fields are done with the changes update page content.
        self.confluence.update_page_content(page_content)

    def get_field_chain(self):
        """
        Get field chain for fields that should be updated on the Wiki.

        :raises: WikiUpdateException

        :rtype: list
        :returns: List of fields that should update the data.
        """
        try:
            field_chain = self.create_field_chain(self.FIELD_MAP, self.data['data'])
            custom_field_chain = self.create_field_chain(self.CUSTOM_FIELD_MAP, self.data['data']['custom_fields'])
        except KeyError as exception:
            raise WikiUpdateException("Wrong formatted request body:"
                                      " `{}` is not present in webhook payload.".format(exception.args[0]))

        return field_chain + custom_field_chain
